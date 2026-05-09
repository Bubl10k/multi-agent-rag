from fastapi import APIRouter, status

from rag.src.api.dependencies import UnitOfWorkDep, UserDep
from rag.src.api.schemas.collection import CollectionCreate, CollectionRead, CollectionUpdate
from rag.src.services.collection import CollectionService

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(data: CollectionCreate, uow: UnitOfWorkDep, user: UserDep):
    return await CollectionService.create(uow, data, user.id)


@router.get("", response_model=list[CollectionRead])
async def get_collections(uow: UnitOfWorkDep, _: UserDep, page: int = 1, limit: int = 20):
    return await CollectionService.get_all(uow, page, limit)


@router.get("/{collection_id}", response_model=CollectionRead)
async def get_collection(collection_id: str, uow: UnitOfWorkDep, _: UserDep):
    return await CollectionService.get(uow, collection_id)


@router.patch("/{collection_id}", response_model=CollectionRead)
async def update_collection(collection_id: str, data: CollectionUpdate, uow: UnitOfWorkDep, _: UserDep):
    return await CollectionService.update(uow, collection_id, data)


@router.delete("/{collection_id}", response_model=CollectionRead)
async def delete_collection(collection_id: str, uow: UnitOfWorkDep, _: UserDep):
    return await CollectionService.delete(uow, collection_id)
