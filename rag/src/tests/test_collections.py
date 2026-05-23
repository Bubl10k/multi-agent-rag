import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from rag.src.api.schemas.collection import CollectionCreate, CollectionUpdate
from rag.src.services.collection import CollectionService
from rag.src.tests.helpers import make_collection_obj, USER_ID, COLLECTION_ID


def _make_uow():
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.collection_repository = AsyncMock()
    return uow


class TestCollectionService:
    @pytest.mark.asyncio
    async def test_create_returns_collection_read(self):
        uow = _make_uow()
        uow.collection_repository.create_one = AsyncMock(return_value=make_collection_obj())

        data = CollectionCreate(name="my-col")
        result = await CollectionService.create(uow, data, USER_ID)

        assert result.name == "test-collection"
        assert result.user_id == USER_ID
        uow.collection_repository.create_one.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_returns_collection_read(self):
        uow = _make_uow()
        uow.collection_repository.get_one_or_404 = AsyncMock(return_value=make_collection_obj())

        result = await CollectionService.get(uow, str(COLLECTION_ID))

        assert result.id == COLLECTION_ID
        uow.collection_repository.get_one_or_404.assert_awaited_once_with(id=str(COLLECTION_ID))

    @pytest.mark.asyncio
    async def test_get_all_returns_list(self):
        uow = _make_uow()
        uow.collection_repository.get_many = AsyncMock(return_value=[make_collection_obj()])

        result = await CollectionService.get_all(uow, page=1, limit=20)

        assert len(result) == 1
        assert result[0].name == "test-collection"

    @pytest.mark.asyncio
    async def test_update_returns_updated_collection(self):
        updated = make_collection_obj()
        updated.name = "renamed"

        uow = _make_uow()
        uow.collection_repository.update_one = AsyncMock(return_value=updated)

        data = CollectionUpdate(name="renamed")
        result = await CollectionService.update(uow, str(COLLECTION_ID), data)

        assert result.name == "renamed"
        uow.collection_repository.update_one.assert_awaited_once_with(str(COLLECTION_ID), {"name": "renamed"})

    @pytest.mark.asyncio
    async def test_delete_returns_collection_read(self):
        uow = _make_uow()
        uow.collection_repository.delete_one = AsyncMock(return_value=make_collection_obj())

        result = await CollectionService.delete(uow, str(COLLECTION_ID))

        assert result.id == COLLECTION_ID
        uow.collection_repository.delete_one.assert_awaited_once_with(str(COLLECTION_ID))

    @pytest.mark.asyncio
    async def test_get_not_found_raises_404(self):
        uow = _make_uow()
        uow.collection_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        with pytest.raises(HTTPException) as exc_info:
            await CollectionService.get(uow, str(uuid.uuid4()))

        assert exc_info.value.status_code == 404


class TestCollectionEndpoints:
    @pytest.mark.asyncio
    async def test_create_collection(self, async_client, mock_uow):
        mock_uow.collection_repository.create_one = AsyncMock(return_value=make_collection_obj())

        response = await async_client.post(
            "/api/collections",
            json={"name": "my-col", "description": "desc"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "test-collection"
        assert body["user_id"] == str(USER_ID)

    @pytest.mark.asyncio
    async def test_create_collection_requires_auth(self):
        from httpx import ASGITransport, AsyncClient
        from rag.src.main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/collections", json={"name": "x"})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_collections(self, async_client, mock_uow):
        mock_uow.collection_repository.get_many = AsyncMock(return_value=[make_collection_obj()])

        response = await async_client.get("/api/collections")

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["id"] == str(COLLECTION_ID)

    @pytest.mark.asyncio
    async def test_get_collection_by_id(self, async_client, mock_uow):
        mock_uow.collection_repository.get_one_or_404 = AsyncMock(return_value=make_collection_obj())

        response = await async_client.get(f"/api/collections/{COLLECTION_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(COLLECTION_ID)

    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, async_client, mock_uow):
        mock_uow.collection_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        response = await async_client.get(f"/api/collections/{uuid.uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_collection(self, async_client, mock_uow):
        updated = make_collection_obj()
        updated.name = "new-name"
        mock_uow.collection_repository.update_one = AsyncMock(return_value=updated)

        response = await async_client.patch(
            f"/api/collections/{COLLECTION_ID}",
            json={"name": "new-name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "new-name"

    @pytest.mark.asyncio
    async def test_delete_collection(self, async_client, mock_uow):
        mock_uow.collection_repository.delete_one = AsyncMock(return_value=make_collection_obj())

        response = await async_client.delete(f"/api/collections/{COLLECTION_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(COLLECTION_ID)

    @pytest.mark.asyncio
    async def test_get_collections_pagination(self, async_client, mock_uow):
        mock_uow.collection_repository.get_many = AsyncMock(return_value=[])

        response = await async_client.get("/api/collections?page=2&limit=5")

        assert response.status_code == 200
        mock_uow.collection_repository.get_many.assert_awaited_once_with(skip=2, limit=5)
