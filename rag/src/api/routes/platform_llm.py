from fastapi import APIRouter

from rag.src.api.dependencies import PlatformLLMServiceDep, UnitOfWorkDep, UserDep
from rag.src.api.schemas.platform_llm import PlatformLLMRead

router = APIRouter(prefix="/platform-llms", tags=["platform-llms"])


@router.get("", response_model=list[PlatformLLMRead])
async def get_platform_llms(uow: UnitOfWorkDep, user: UserDep, service: PlatformLLMServiceDep):
    return await service.get_all_active_with_usage(uow, user.id)
