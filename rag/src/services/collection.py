import uuid

from rag.src.api.schemas.collection import CollectionCreate, CollectionRead, CollectionUpdate
from rag.src.utils.unit_of_work import UnitOfWork


class CollectionService:
    @staticmethod
    async def create(uow: UnitOfWork, data: CollectionCreate, user_id: uuid.UUID) -> CollectionRead:
        async with uow:
            collection = await uow.collection_repository.create_one({**data.model_dump(), "user_id": user_id})
            return CollectionRead.model_validate(collection)

    @staticmethod
    async def get(uow: UnitOfWork, collection_id: str) -> CollectionRead:
        async with uow:
            collection = await uow.collection_repository.get_one_or_404(id=collection_id)
            return CollectionRead.model_validate(collection)

    @staticmethod
    async def get_all(uow: UnitOfWork, page: int = 1, limit: int = 20) -> list[CollectionRead]:
        async with uow:
            collections = await uow.collection_repository.get_many(skip=page, limit=limit)
            return [CollectionRead.model_validate(c) for c in collections]

    @staticmethod
    async def update(uow: UnitOfWork, collection_id: str, data: CollectionUpdate) -> CollectionRead:
        async with uow:
            collection = await uow.collection_repository.update_one(collection_id, data.model_dump(exclude_none=True))
            return CollectionRead.model_validate(collection)

    @staticmethod
    async def delete(uow: UnitOfWork, collection_id: str) -> CollectionRead:
        async with uow:
            collection = await uow.collection_repository.delete_one(collection_id)
            return CollectionRead.model_validate(collection)
