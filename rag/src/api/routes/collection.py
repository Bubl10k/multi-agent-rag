from fastapi import APIRouter, status

from rag.src.api.dependencies import CollectionServiceDep, UnitOfWorkDep, UserDep
from rag.src.api.schemas.collection import CollectionCreate, CollectionRead, CollectionUpdate

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(data: CollectionCreate, service: CollectionServiceDep, uow: UnitOfWorkDep, user: UserDep):
    return await service.create(uow, data, user.id)


@router.get("", response_model=list[CollectionRead])
async def get_collections(
    uow: UnitOfWorkDep, _: UserDep, service: CollectionServiceDep, page: int = 1, limit: int = 20
):
    return await service.get_all(uow, page, limit)


@router.get("/{collection_id}", response_model=CollectionRead)
async def get_collection(collection_id: str, uow: UnitOfWorkDep, service: CollectionServiceDep, _: UserDep):
    return await service.get(uow, collection_id)


@router.patch("/{collection_id}", response_model=CollectionRead)
async def update_collection(
    collection_id: str, data: CollectionUpdate, uow: UnitOfWorkDep, service: CollectionServiceDep, _: UserDep
):
    return await service.update(uow, collection_id, data)


@router.delete("/{collection_id}", response_model=CollectionRead)
async def delete_collection(collection_id: str, uow: UnitOfWorkDep, service: CollectionServiceDep, _: UserDep):
    return await service.delete(uow, collection_id)
