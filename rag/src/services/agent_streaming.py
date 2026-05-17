import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import WebSocket, WebSocketDisconnect
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent import StreamEvent
from rag.src.agent.factory import AgentGraphFactory
from rag.src.agent.types import AgentType
from rag.src.db.checkpointer import ensure_initialized, get_checkpointer
from rag.src.models.agent import Agent
from rag.src.models.conversation import Conversation
from rag.src.models.message import MessageRole
from rag.src.utils.crypto import decrypt
from rag.src.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class AgentStreamingService:
    @staticmethod
    async def load_agent(uow: UnitOfWork, agent_id: uuid.UUID) -> Agent:
        async with uow:
            return await uow.agent_repository.get_one_or_404(id=agent_id)

    @staticmethod
    async def build_graph(uow: UnitOfWork, agent_id: uuid.UUID) -> CompiledStateGraph:
        agent = await AgentStreamingService.load_agent(uow, agent_id)
        model_name = agent.llm.model_name
        provider_kwargs = {}
        if model_name.startswith("gemini"):
            provider_kwargs["model_provider"] = "google_genai"
        llm = init_chat_model(model=model_name, api_key=decrypt(agent.llm.api_key), **provider_kwargs)
        await ensure_initialized()
        return AgentGraphFactory.create(
            agent_type=AgentType(agent.agent_type),
            llm=llm,
            collection_names=[c.name for c in agent.collections],
            prompt=agent.prompt,
            checkpointer=get_checkpointer(),
            agent_config=agent.agent_config or {},
        )

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
    ) -> AsyncGenerator[str, None]:
        config = RunnableConfig(configurable={"thread_id": str(conversation_id)})

        async with uow:
            await uow.message_repository.save(str(conversation_id), MessageRole.USER, message)

        output_nodes: frozenset[str] | None = getattr(graph, "output_nodes", None)

        full_response: list[str] = []
        async for event in graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
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

        async with uow:
            await uow.message_repository.save(str(conversation_id), MessageRole.ASSISTANT, "".join(full_response))

    @staticmethod
    async def handle_ws(
        websocket: WebSocket,
        uow: UnitOfWork,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await websocket.accept()

        graph = await AgentStreamingService.build_graph(uow, agent_id)

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

                message = data.get("message", "").strip()
                logger.info(f"Received message: {message}")
                if not message:
                    await websocket.send_json({"error": "Field 'message' is required"})
                    continue

                if conversation is None:
                    conversation_id = data.get("conversation_id")
                    conversation = await AgentStreamingService.get_or_create_conversation(
                        uow=uow,
                        agent_id=agent_id,
                        user_id=user_id,
                        conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                    )

                async for token in AgentStreamingService.stream(graph, message, conversation.id, uow):
                    await websocket.send_text(token)

                await websocket.send_json({"done": True, "conversation_id": str(conversation.id)})
        except WebSocketDisconnect:
            pass
