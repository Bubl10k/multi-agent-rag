import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from rag.src.api.schemas.llm import LLMCreate, LLMUpdate
from rag.src.services.llm import LLMService
from rag.src.tests.helpers import LLM_ID, USER_ID, make_llm_obj
from rag.src.utils.crypto import encrypt


def _make_uow():
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.llm_repository = AsyncMock()
    return uow


class TestLLMService:
    @pytest.mark.asyncio
    async def test_create_encrypts_api_key(self):
        uow = _make_uow()
        uow.llm_repository.create_one = AsyncMock(return_value=make_llm_obj())

        data = LLMCreate(model_name="gpt-4o", api_key="sk-plaintext")
        await LLMService.create(uow, data, USER_ID)

        call_payload = uow.llm_repository.create_one.call_args[0][0]
        # api_key must be stored as bytes (encrypted), not the plaintext string
        assert isinstance(call_payload["api_key"], bytes)
        assert call_payload["api_key"] != b"sk-plaintext"

    @pytest.mark.asyncio
    async def test_create_stores_user_id(self):
        uow = _make_uow()
        uow.llm_repository.create_one = AsyncMock(return_value=make_llm_obj())

        data = LLMCreate(model_name="gpt-4o", api_key="key")
        await LLMService.create(uow, data, USER_ID)

        call_payload = uow.llm_repository.create_one.call_args[0][0]
        assert call_payload["user_id"] == USER_ID

    @pytest.mark.asyncio
    async def test_create_returns_llm_read(self):
        uow = _make_uow()
        uow.llm_repository.create_one = AsyncMock(return_value=make_llm_obj())

        data = LLMCreate(model_name="gpt-4o", api_key="key")
        result = await LLMService.create(uow, data, USER_ID)

        assert result.id == LLM_ID
        assert result.model_name == "gpt-4o"
        assert result.user_id == USER_ID
        # api_key must NOT appear in the read schema
        assert not hasattr(result, "api_key")

    @pytest.mark.asyncio
    async def test_get_returns_llm_read(self):
        uow = _make_uow()
        uow.llm_repository.get_one_or_404 = AsyncMock(return_value=make_llm_obj())

        result = await LLMService.get(uow, str(LLM_ID))

        assert result.id == LLM_ID

    @pytest.mark.asyncio
    async def test_get_not_found_raises_404(self):
        uow = _make_uow()
        uow.llm_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        with pytest.raises(HTTPException) as exc_info:
            await LLMService.get(uow, str(uuid.uuid4()))

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_all_returns_list(self):
        uow = _make_uow()
        uow.llm_repository.get_many = AsyncMock(return_value=[make_llm_obj()])

        result = await LLMService.get_all(uow)

        assert len(result) == 1
        assert result[0].id == LLM_ID

    @pytest.mark.asyncio
    async def test_update_encrypts_api_key_when_present(self):
        uow = _make_uow()
        uow.llm_repository.update_one = AsyncMock(return_value=make_llm_obj())

        data = LLMUpdate(api_key="new-key")
        await LLMService.update(uow, str(LLM_ID), data)

        call_payload = uow.llm_repository.update_one.call_args[0][1]
        assert isinstance(call_payload["api_key"], bytes)

    @pytest.mark.asyncio
    async def test_update_without_api_key_does_not_encrypt(self):
        uow = _make_uow()
        uow.llm_repository.update_one = AsyncMock(return_value=make_llm_obj())

        data = LLMUpdate(model_name="gpt-3.5-turbo")
        await LLMService.update(uow, str(LLM_ID), data)

        call_payload = uow.llm_repository.update_one.call_args[0][1]
        assert "api_key" not in call_payload

    @pytest.mark.asyncio
    async def test_delete_returns_llm_read(self):
        uow = _make_uow()
        uow.llm_repository.delete_one = AsyncMock(return_value=make_llm_obj())

        result = await LLMService.delete(uow, str(LLM_ID))

        assert result.id == LLM_ID

    def test_get_decrypted_api_key(self):
        plaintext = "my-secret-key"
        encrypted = encrypt(plaintext)
        decrypted = LLMService.get_decrypted_api_key(encrypted)
        assert decrypted == plaintext


class TestLLMEndpoints:
    @pytest.mark.asyncio
    async def test_create_llm(self, async_client, mock_uow):
        mock_uow.llm_repository.create_one = AsyncMock(return_value=make_llm_obj())

        response = await async_client.post(
            "/api/llms",
            json={"model_name": "gpt-4o", "api_key": "sk-test"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["model_name"] == "gpt-4o"
        assert "api_key" not in body

    @pytest.mark.asyncio
    async def test_create_llm_requires_auth(self):
        from httpx import ASGITransport, AsyncClient
        from rag.src.main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/llms", json={"model_name": "x", "api_key": "y"})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_llms(self, async_client, mock_uow):
        mock_uow.llm_repository.get_many = AsyncMock(return_value=[make_llm_obj()])

        response = await async_client.get("/api/llms")

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["id"] == str(LLM_ID)

    @pytest.mark.asyncio
    async def test_get_llm_by_id(self, async_client, mock_uow):
        mock_uow.llm_repository.get_one_or_404 = AsyncMock(return_value=make_llm_obj())

        response = await async_client.get(f"/api/llms/{LLM_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(LLM_ID)

    @pytest.mark.asyncio
    async def test_get_llm_not_found(self, async_client, mock_uow):
        mock_uow.llm_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        response = await async_client.get(f"/api/llms/{uuid.uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_llm(self, async_client, mock_uow):
        updated = make_llm_obj()
        updated.model_name = "gpt-3.5-turbo"
        mock_uow.llm_repository.update_one = AsyncMock(return_value=updated)

        response = await async_client.patch(
            f"/api/llms/{LLM_ID}",
            json={"model_name": "gpt-3.5-turbo"},
        )

        assert response.status_code == 200
        assert response.json()["model_name"] == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_delete_llm(self, async_client, mock_uow):
        mock_uow.llm_repository.delete_one = AsyncMock(return_value=make_llm_obj())

        response = await async_client.delete(f"/api/llms/{LLM_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(LLM_ID)
