import uuid

from fastapi import APIRouter, status

from rag.src.api.dependencies import UnitOfWorkDep, UserDep
from rag.src.api.schemas.conversation import ConversationRead
from rag.src.services.conversation import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationRead])
async def get_conversations(uow: UnitOfWorkDep, user: UserDep, page: int = 1, limit: int = 20):
    return await ConversationService.get_all(uow, user.id, page, limit)


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get_conversation(conversation_id: uuid.UUID, uow: UnitOfWorkDep, user: UserDep):
    return await ConversationService.get(uow, user.id, conversation_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: uuid.UUID, uow: UnitOfWorkDep, user: UserDep):
    await ConversationService.delete(uow, user.id, conversation_id)
