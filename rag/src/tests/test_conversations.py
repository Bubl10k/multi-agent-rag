import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from rag.src.services.conversation import ConversationService
from rag.src.tests.helpers import (
    AGENT_ID,
    CONVERSATION_ID,
    OTHER_USER_ID,
    USER_ID,
    make_conversation_obj,
)


def _make_uow():
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.conversation_repository = AsyncMock()
    uow.message_repository = AsyncMock()
    return uow


class TestConversationService:
    @pytest.mark.asyncio
    async def test_get_all_returns_list(self):
        uow = _make_uow()
        uow.conversation_repository.get_many = AsyncMock(return_value=[make_conversation_obj()])

        result = await ConversationService.get_all(uow, USER_ID)

        assert len(result) == 1
        assert result[0].id == CONVERSATION_ID
        assert result[0].user_id == USER_ID

    @pytest.mark.asyncio
    async def test_get_all_passes_user_id_filter(self):
        uow = _make_uow()
        uow.conversation_repository.get_many = AsyncMock(return_value=[])

        await ConversationService.get_all(uow, USER_ID, page=2, limit=5)

        call_kwargs = uow.conversation_repository.get_many.call_args[1]
        assert call_kwargs["user_id"] == USER_ID
        assert call_kwargs["skip"] == 2
        assert call_kwargs["limit"] == 5

    @pytest.mark.asyncio
    async def test_get_own_conversation(self):
        uow = _make_uow()
        uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(USER_ID))

        result = await ConversationService.get(uow, USER_ID, CONVERSATION_ID)

        assert result.id == CONVERSATION_ID

    @pytest.mark.asyncio
    async def test_get_other_users_conversation_raises_403(self):
        uow = _make_uow()
        # Conversation belongs to OTHER_USER_ID
        uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(OTHER_USER_ID))

        with pytest.raises(HTTPException) as exc_info:
            await ConversationService.get(uow, USER_ID, CONVERSATION_ID)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_not_found_raises_404(self):
        uow = _make_uow()
        uow.conversation_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        with pytest.raises(HTTPException) as exc_info:
            await ConversationService.get(uow, USER_ID, uuid.uuid4())

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_own_conversation(self):
        uow = _make_uow()
        uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(USER_ID))
        uow.conversation_repository.delete_one = AsyncMock()
        uow.message_repository.delete_by_conversation = AsyncMock()

        await ConversationService.delete(uow, USER_ID, CONVERSATION_ID)

        uow.message_repository.delete_by_conversation.assert_awaited_once_with(str(CONVERSATION_ID))
        uow.conversation_repository.delete_one.assert_awaited_once_with(str(CONVERSATION_ID))

    @pytest.mark.asyncio
    async def test_delete_other_users_conversation_raises_403(self):
        uow = _make_uow()
        uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(OTHER_USER_ID))

        with pytest.raises(HTTPException) as exc_info:
            await ConversationService.delete(uow, USER_ID, CONVERSATION_ID)

        assert exc_info.value.status_code == 403
        uow.conversation_repository.delete_one.assert_not_awaited()


class TestConversationEndpoints:
    @pytest.mark.asyncio
    async def test_get_conversations(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_many = AsyncMock(return_value=[make_conversation_obj()])

        response = await async_client.get("/api/conversations")

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["id"] == str(CONVERSATION_ID)
        assert body[0]["agent_id"] == str(AGENT_ID)

    @pytest.mark.asyncio
    async def test_get_conversations_requires_auth(self):
        from httpx import ASGITransport, AsyncClient
        from rag.src.main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/conversations")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(USER_ID))

        response = await async_client.get(f"/api/conversations/{CONVERSATION_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(CONVERSATION_ID)

    @pytest.mark.asyncio
    async def test_get_conversation_wrong_user_returns_403(self, async_client, mock_uow):
        # Conversation belongs to a different user
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(OTHER_USER_ID))

        response = await async_client.get(f"/api/conversations/{CONVERSATION_ID}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        response = await async_client.get(f"/api/conversations/{uuid.uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_conversation(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(USER_ID))
        mock_uow.conversation_repository.delete_one = AsyncMock()
        mock_uow.message_repository.delete_by_conversation = AsyncMock()

        response = await async_client.delete(f"/api/conversations/{CONVERSATION_ID}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_conversation_wrong_user_returns_403(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=make_conversation_obj(OTHER_USER_ID))

        response = await async_client.delete(f"/api/conversations/{CONVERSATION_ID}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_conversation_includes_messages(self, async_client, mock_uow):
        conv = make_conversation_obj(USER_ID)
        mock_uow.conversation_repository.get_one_or_404 = AsyncMock(return_value=conv)

        response = await async_client.get(f"/api/conversations/{CONVERSATION_ID}")

        body = response.json()
        assert "messages" in body
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_get_conversations_pagination(self, async_client, mock_uow):
        mock_uow.conversation_repository.get_many = AsyncMock(return_value=[])

        response = await async_client.get("/api/conversations?page=3&limit=10")

        assert response.status_code == 200
        call_kwargs = mock_uow.conversation_repository.get_many.call_args[1]
        assert call_kwargs["skip"] == 3
        assert call_kwargs["limit"] == 10
