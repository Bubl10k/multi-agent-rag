from rag.src.api.schemas.llm import LLMCreate, LLMRead, LLMUpdate
from rag.src.utils.crypto import decrypt, encrypt
from rag.src.utils.unit_of_work import UnitOfWork


class LLMService:
    @staticmethod
    async def create(uow: UnitOfWork, data: LLMCreate) -> LLMRead:
        async with uow:
            payload = data.model_dump()
            payload["api_key"] = encrypt(payload["api_key"])
            llm = await uow.llm_repository.create_one(payload)
            return LLMRead.model_validate(llm)

    @staticmethod
    async def get(uow: UnitOfWork, llm_id: str) -> LLMRead:
        async with uow:
            llm = await uow.llm_repository.get_one_or_404(id=llm_id)
            return LLMRead.model_validate(llm)

    @staticmethod
    async def get_all(uow: UnitOfWork, page: int = 1, limit: int = 20) -> list[LLMRead]:
        async with uow:
            llms = await uow.llm_repository.get_many(skip=page, limit=limit)
            return [LLMRead.model_validate(llm) for llm in llms]

    @staticmethod
    async def update(uow: UnitOfWork, llm_id: str, data: LLMUpdate) -> LLMRead:
        async with uow:
            payload = data.model_dump(exclude_none=True)
            if "api_key" in payload:
                payload["api_key"] = encrypt(payload["api_key"])
            llm = await uow.llm_repository.update_one(llm_id, payload)
            return LLMRead.model_validate(llm)

    @staticmethod
    async def delete(uow: UnitOfWork, llm_id: str) -> LLMRead:
        async with uow:
            llm = await uow.llm_repository.delete_one(llm_id)
            return LLMRead.model_validate(llm)

    @staticmethod
    def get_decrypted_api_key(api_key: bytes) -> str:
        return decrypt(api_key)
