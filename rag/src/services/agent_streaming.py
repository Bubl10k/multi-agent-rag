import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import WebSocket, WebSocketDisconnect
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from rag.src.db.vector_store import VectorStore
from rag.src.models.agent import Agent
from rag.src.models.conversation import Conversation
from rag.src.models.message import MessageRole
from rag.src.utils.crypto import decrypt
from rag.src.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

# TODO: 5 is very small number, but for now it's okay
HISTORY_WINDOW = 5  # last N messages passed to LLM


class AgentStreamingService:
    @staticmethod
    async def load_agent(uow: UnitOfWork, agent_id: uuid.UUID) -> Agent:
        async with uow:
            return await uow.agent_repository.get_one_or_404(id=agent_id)

    @staticmethod
    async def get_or_create_conversation(
        uow: UnitOfWork,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
    ) -> tuple[Conversation, list[BaseMessage]]:
        async with uow:
            if conversation_id:
                conv = await uow.conversation_repository.get_one_or_404(id=conversation_id)
                history = await uow.message_repository.get_last_n(str(conversation_id), HISTORY_WINDOW)
                lc_history: list[BaseMessage] = [
                    HumanMessage(content=m.content) if m.role == MessageRole.USER else AIMessage(content=m.content)
                    for m in history
                ]
                return conv, lc_history
            conv = await uow.conversation_repository.create_one({"agent_id": agent_id, "user_id": user_id})
            return conv, []

    @staticmethod
    async def stream(
        agent: Agent,
        llm: BaseChatModel,
        message: str,
        conversation_id: uuid.UUID,
        lc_history: list[BaseMessage],
        uow: UnitOfWork,
    ) -> AsyncGenerator[str, None]:
        # 1. Retrieve context from all agent collections
        context_parts: list[str] = []
        for collection in agent.collections:
            docs_with_score = await asyncio.to_thread(
                VectorStore(collection_name=collection.name).search_with_score, message, 4
            )
            logger.info(docs_with_score)
            context_parts.extend(doc.page_content for doc, score in docs_with_score if score > 0.5)

        # 2. Build system prompt with retrieved context
        system_content = agent.prompt
        if context_parts:
            logger.info(f"Retrieved context: {context_parts}")
            context_text = "\n\n---\n\n".join(context_parts)
            system_content += f"\n\nRelevant context:\n{context_text}"

        # 3. Save user message to DB
        async with uow:
            await uow.message_repository.save(str(conversation_id), MessageRole.USER, message)

        # 4. Build messages: system + in-memory history + current
        messages = [SystemMessage(content=system_content), *lc_history, HumanMessage(content=message)]

        # 5. Stream and collect full response
        full_response: list[str] = []
        async for chunk in llm.astream(messages):
            if chunk.content:
                token = str(chunk.content)
                full_response.append(token)
                yield token

        ai_content = "".join(full_response)

        # 6. Save AI response to DB and update in-memory history
        async with uow:
            await uow.message_repository.save(str(conversation_id), MessageRole.ASSISTANT, ai_content)

        lc_history.append(HumanMessage(content=message))
        lc_history.append(AIMessage(content=ai_content))

        logger.info(f"Conversation history: {lc_history}")

        if len(lc_history) > HISTORY_WINDOW * 2:
            del lc_history[: len(lc_history) - HISTORY_WINDOW * 2]

    @staticmethod
    async def handle_ws(
        websocket: WebSocket,
        uow: UnitOfWork,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await websocket.accept()

        agent = await AgentStreamingService.load_agent(uow, agent_id)
        api_key = decrypt(agent.llm.api_key)
        llm = init_chat_model(model=agent.llm.model_name, api_key=api_key)

        conversation: Conversation | None = None
        lc_history: list[BaseMessage] = []

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
                    conversation, lc_history = await AgentStreamingService.get_or_create_conversation(
                        uow=uow,
                        agent_id=agent_id,
                        user_id=user_id,
                        conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                    )

                async for token in AgentStreamingService.stream(agent, llm, message, conversation.id, lc_history, uow):
                    await websocket.send_text(token)

                await websocket.send_json({"done": True, "conversation_id": str(conversation.id)})
        except WebSocketDisconnect:
            pass
