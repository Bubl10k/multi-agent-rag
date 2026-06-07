import uuid

from fastapi import HTTPException, status

from rag.src.api.schemas.conversation import ConversationRead
from rag.src.models.conversation import Conversation
from rag.src.utils.unit_of_work import UnitOfWork


class ConversationService:
    @staticmethod
    async def get_all(uow: UnitOfWork, user_id: uuid.UUID, page: int = 1, limit: int = 20) -> list[ConversationRead]:
        async with uow:
            conversations = await uow.conversation_repository.get_many(
                skip=page,
                limit=limit,
                user_id=user_id,
                order_by=[Conversation.created_at.desc()],
            )
            return [ConversationRead.model_validate(c) for c in conversations]

    @staticmethod
    async def get(uow: UnitOfWork, user_id: uuid.UUID, conversation_id: uuid.UUID) -> ConversationRead:
        async with uow:
            conv = await uow.conversation_repository.get_one_or_404(id=conversation_id)
            if conv.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")
            return ConversationRead.model_validate(conv)

    @staticmethod
    async def delete(uow: UnitOfWork, user_id: uuid.UUID, conversation_id: uuid.UUID) -> ConversationRead:
        async with uow:
            conv = await uow.conversation_repository.get_one_or_404(id=conversation_id)
            if conv.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")
            result = ConversationRead.model_validate(conv)
            await uow.message_repository.delete_by_conversation(str(conversation_id))
            await uow.conversation_repository.delete_one(str(conversation_id))
            return result
