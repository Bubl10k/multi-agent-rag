import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status

from rag.src.api.schemas.platform_llm import PlatformLLMRead
from rag.src.common.settings import settings
from rag.src.utils.unit_of_work import UnitOfWork

_PROVIDER_MAP = {
    "openai": None,
    "google": "google_genai",
}


class PlatformLLMService:
    @staticmethod
    def _current_hour() -> datetime:
        now = datetime.now(UTC)
        return now.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    async def get_all_active_with_usage(uow: UnitOfWork, user_id: uuid.UUID) -> list[PlatformLLMRead]:
        async with uow:
            current_hour = PlatformLLMService._current_hour()
            platform_llms = await uow.platform_llm_repository.get_many(skip=1, limit=100, is_active=True)
            requests_used = await uow.usage_record_repository.get_request_count(user_id, current_hour)
            limit = settings.platform_llm.PLATFORM_LLM_HOURLY_LIMIT

            return [
                PlatformLLMRead(
                    id=llm.id,
                    display_name=llm.display_name,
                    model_name=llm.model_name,
                    provider=llm.provider,
                    is_active=llm.is_active,
                    requests_used=requests_used,
                    requests_limit=limit,
                )
                for llm in platform_llms
            ]

    @staticmethod
    async def check_and_increment_usage(uow: UnitOfWork, user_id: uuid.UUID) -> None:
        async with uow:
            current_hour = PlatformLLMService._current_hour()
            limit = settings.platform_llm.PLATFORM_LLM_HOURLY_LIMIT
            requests_used = await uow.usage_record_repository.get_request_count(user_id, current_hour)

            if requests_used >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Hourly limit of {limit} requests reached. Try again next hour.",
                )

            await uow.usage_record_repository.increment(user_id, current_hour)

    @staticmethod
    def get_api_key(provider: str) -> str:
        keys = {
            "openai": settings.platform_llm.OPENAI_PLATFORM_API_KEY,
            "google": settings.platform_llm.GOOGLE_PLATFORM_API_KEY,
        }
        key = keys.get(provider, "")
        if not key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Platform API key for provider '{provider}' is not configured.",
            )
        return key

    @staticmethod
    def get_provider_kwargs(provider: str) -> dict:
        mapped = _PROVIDER_MAP.get(provider)
        return {"model_provider": mapped} if mapped else {}
