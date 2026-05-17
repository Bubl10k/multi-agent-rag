import uuid

from fastapi import APIRouter, status

from rag.src.api.dependencies import ConversationServiceDep, UnitOfWorkDep, UserDep
from rag.src.api.schemas.conversation import ConversationRead

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationRead])
async def get_conversations(
    uow: UnitOfWorkDep, user: UserDep, service: ConversationServiceDep, page: int = 1, limit: int = 20
):
    return await service.get_all(uow, user.id, page, limit)


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: uuid.UUID, uow: UnitOfWorkDep, service: ConversationServiceDep, user: UserDep
):
    return await service.get(uow, user.id, conversation_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID, uow: UnitOfWorkDep, service: ConversationServiceDep, user: UserDep
):
    await service.delete(uow, user.id, conversation_id)
