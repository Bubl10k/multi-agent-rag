import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent import StreamEvent
from rag.src.agent.enums import WsClientMessageType
from rag.src.agent.factory import AgentGraphFactory
from rag.src.agent.types import AgentType
from rag.src.db.checkpointer import ensure_initialized, get_checkpointer
from rag.src.models.agent import Agent
from rag.src.models.conversation import Conversation
from rag.src.models.message import MessageRole
from rag.src.services.platform_llm import PlatformLLMService
from rag.src.utils.crypto import decrypt
from rag.src.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class AgentStreamingService:
    @staticmethod
    async def load_agent(uow: UnitOfWork, agent_id: uuid.UUID) -> Agent:
        async with uow:
            return await uow.agent_repository.get_one_or_404(id=agent_id)

    @staticmethod
    async def build_graph(uow: UnitOfWork, agent_id: uuid.UUID) -> tuple[CompiledStateGraph, bool]:
        agent = await AgentStreamingService.load_agent(uow, agent_id)

        if agent.platform_llm_id is not None:
            platform_llm = agent.platform_llm
            api_key = PlatformLLMService.get_api_key(platform_llm.provider)
            model_name = platform_llm.model_name
            provider_kwargs = PlatformLLMService.get_provider_kwargs(platform_llm.provider)
            is_platform = True
        else:
            api_key = decrypt(agent.llm.api_key)
            model_name = agent.llm.model_name
            provider_kwargs = {}
            if model_name.startswith("gemini"):
                provider_kwargs["model_provider"] = "google_genai"
            is_platform = False

        llm = init_chat_model(model=model_name, api_key=api_key, **provider_kwargs)
        await ensure_initialized()
        graph = AgentGraphFactory.create(
            agent_type=AgentType(agent.agent_type),
            llm=llm,
            collection_names=[c.name for c in agent.collections],
            prompt=agent.prompt,
            checkpointer=get_checkpointer(),
            agent_config=agent.agent_config or {},
        )
        return graph, is_platform

    @staticmethod
    async def get_or_create_conversation(
        uow: UnitOfWork,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
    ) -> Conversation:
        async with uow:
            if conversation_id:
                return await uow.conversation_repository.get_one_or_404(id=conversation_id)
            return await uow.conversation_repository.create_one({"agent_id": agent_id, "user_id": user_id})

    @staticmethod
    async def stream(
        graph: CompiledStateGraph,
        message: str,
        conversation_id: uuid.UUID,
        uow: UnitOfWork,
        language: str | None = None,
    ) -> AsyncGenerator[str, None]:
        config = RunnableConfig(configurable={"thread_id": str(conversation_id)})

        async with uow:
            await uow.message_repository.save(str(conversation_id), MessageRole.USER, message)

        output_nodes: frozenset[str] | None = getattr(graph, "output_nodes", None)

        full_response: list[str] = []
        try:
            async for event in graph.astream_events(
                {"messages": [HumanMessage(content=message)], "language": language},
                config=config,
                version="v2",
            ):
                if event["event"] == StreamEvent.CHAT_MODEL_STREAM:
                    if output_nodes is not None:
                        node = event.get("metadata", {}).get("langgraph_node", "")
                        if node not in output_nodes:
                            continue
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        token = str(chunk.content)
                        full_response.append(token)
                        yield token
                elif event["event"] == StreamEvent.CHAT_MODEL_END:
                    output = event.get("data", {}).get("output")
                    usage = getattr(output, "usage_metadata", None)
                    if usage:
                        logger.info(
                            "Token usage — input: %d, output: %d, total: %d",
                            usage.get("input_tokens", 0),
                            usage.get("output_tokens", 0),
                            usage.get("total_tokens", 0),
                        )
        finally:
            if full_response:
                async with uow:
                    await uow.message_repository.save(
                        str(conversation_id), MessageRole.ASSISTANT, "".join(full_response)
                    )

    @staticmethod
    async def _stream_with_cancellation(
        websocket: WebSocket,
        graph: "CompiledStateGraph",
        message: str,
        conversation_id: uuid.UUID,
        uow: UnitOfWork,
        language: str | None = None,
    ) -> bool:
        """
        Stream tokens to the websocket while listening for a stop signal.

        Returns True if the client sent a stop message, False if streaming completed normally.
        """

        async def do_stream() -> None:
            async for token in AgentStreamingService.stream(graph, message, conversation_id, uow, language):
                await websocket.send_text(token)

        stream_task = asyncio.create_task(do_stream())
        stopped = False

        while not stream_task.done():
            receive_task = asyncio.create_task(websocket.receive_text())
            done, _ = await asyncio.wait({stream_task, receive_task}, return_when=asyncio.FIRST_COMPLETED)

            if receive_task in done and stream_task not in done:
                try:
                    data = json.loads(receive_task.result())
                    if data.get("type") == WsClientMessageType.STOP:
                        stream_task.cancel()
                        stopped = True
                except Exception:
                    stream_task.cancel()
                    try:
                        await stream_task
                    except (asyncio.CancelledError, Exception):
                        pass
                    raise
            else:
                if not receive_task.done():
                    receive_task.cancel()
                try:
                    await receive_task
                except (asyncio.CancelledError, Exception):
                    pass

        try:
            await stream_task
        except asyncio.CancelledError:
            pass

        return stopped

    @staticmethod
    async def handle_ws(
        websocket: WebSocket,
        uow: UnitOfWork,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await websocket.accept()

        graph, is_platform = await AgentStreamingService.build_graph(uow, agent_id)

        conversation: Conversation | None = None

        try:
            while True:
                raw = await websocket.receive_text()
                if not raw.strip():
                    continue

                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    await websocket.send_json({"error": "Invalid JSON"})
                    continue

                if data.get("type") == WsClientMessageType.STOP:
                    continue

                message = data.get("message", "").strip()
                language = data.get("language") or None
                logger.info(f"Received message: {message}")
                if not message:
                    await websocket.send_json({"error": "Field 'message' is required"})
                    continue

                if is_platform:
                    try:
                        await PlatformLLMService.check_and_increment_usage(UnitOfWork(), user_id)
                    except HTTPException as e:
                        await websocket.send_json({"error": e.detail})
                        continue

                if conversation is None:
                    conversation_id = data.get("conversation_id")
                    conversation = await AgentStreamingService.get_or_create_conversation(
                        uow=uow,
                        agent_id=agent_id,
                        user_id=user_id,
                        conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                    )

                try:
                    stopped = await AgentStreamingService._stream_with_cancellation(
                        websocket, graph, message, conversation.id, uow, language
                    )
                except Exception as e:
                    logger.exception("Error during streaming")
                    await websocket.send_json({"error": str(e)})
                    continue

                if stopped:
                    await websocket.send_json({"stopped": True, "conversation_id": str(conversation.id)})
                else:
                    await websocket.send_json({"done": True, "conversation_id": str(conversation.id)})
        except WebSocketDisconnect:
            pass
