import uuid

from fastapi import APIRouter

from rag.src.api.dependencies import LlmServiceDep, UnitOfWorkDep, UserDep
from rag.src.api.schemas.llm import LLMCreate, LLMRead, LLMUpdate

router = APIRouter(prefix="/llms", tags=["llms"])


@router.post("", response_model=LLMRead, status_code=201)
async def create_llm(data: LLMCreate, uow: UnitOfWorkDep, service: LlmServiceDep, user: UserDep):
    return await service.create(uow, data, user.id)


@router.get("", response_model=list[LLMRead])
async def get_llms(uow: UnitOfWorkDep, _: UserDep, service: LlmServiceDep, page: int = 1, limit: int = 20):
    return await service.get_all(uow, page, limit)


@router.get("/{llm_id}", response_model=LLMRead)
async def get_llm(llm_id: uuid.UUID, uow: UnitOfWorkDep, service: LlmServiceDep, _: UserDep):
    return await service.get(uow, llm_id)


@router.patch("/{llm_id}", response_model=LLMRead)
async def update_llm(llm_id: uuid.UUID, data: LLMUpdate, uow: UnitOfWorkDep, service: LlmServiceDep, _: UserDep):
    return await service.update(uow, llm_id, data)


@router.delete("/{llm_id}", response_model=LLMRead)
async def delete_llm(llm_id: uuid.UUID, uow: UnitOfWorkDep, service: LlmServiceDep, _: UserDep):
    return await service.delete(uow, llm_id)
