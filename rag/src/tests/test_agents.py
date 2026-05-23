import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from rag.src.agent.types import AgentType
from rag.src.api.schemas.agent import AgentCreate, AgentUpdate
from rag.src.tests.helpers import AGENT_ID, LLM_ID, USER_ID, make_agent_obj, make_llm_obj


def _make_uow(llm_exists: bool = True):
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.llm_repository = AsyncMock()
    uow.agent_repository = AsyncMock()
    uow.collection_repository = AsyncMock()
    uow.session = AsyncMock()

    if llm_exists:
        uow.llm_repository.get_one_or_404 = AsyncMock(return_value=make_llm_obj())
    else:
        uow.llm_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )
    return uow


class TestAgentService:
    @pytest.mark.asyncio
    async def test_create_agent(self):
        from rag.src.services.agent import AgentService

        agent_obj = make_agent_obj()
        uow = _make_uow()
        uow.agent_repository.create_one = AsyncMock(return_value=agent_obj)
        uow.collection_repository.get_many = AsyncMock(return_value=[])

        data = AgentCreate(name="bot", prompt="hello", llm_id=LLM_ID)
        result = await AgentService.create(uow, data, USER_ID)

        assert result.id == AGENT_ID
        assert result.user_id == USER_ID
        uow.llm_repository.get_one_or_404.assert_awaited_once_with(id=LLM_ID)

    @pytest.mark.asyncio
    async def test_create_agent_invalid_llm_raises_404(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow(llm_exists=False)

        data = AgentCreate(name="bot", prompt="hello", llm_id=uuid.uuid4())
        with pytest.raises(HTTPException) as exc_info:
            await AgentService.create(uow, data, USER_ID)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_agent(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow()
        uow.agent_repository.get_one_or_404 = AsyncMock(return_value=make_agent_obj())

        result = await AgentService.get(uow, AGENT_ID)

        assert result.id == AGENT_ID

    @pytest.mark.asyncio
    async def test_get_all_agents(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow()
        uow.agent_repository.get_many = AsyncMock(return_value=[make_agent_obj()])

        result = await AgentService.get_all(uow)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow()
        uow.agent_repository.delete_one = AsyncMock(return_value=make_agent_obj())

        result = await AgentService.delete(uow, AGENT_ID)

        assert result.id == AGENT_ID
        uow.agent_repository.delete_one.assert_awaited_once_with(str(AGENT_ID))

    @pytest.mark.asyncio
    async def test_update_agent_without_llm_change(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow()
        updated = make_agent_obj()
        updated.name = "updated-name"
        uow.agent_repository.update_one = AsyncMock(return_value=updated)

        data = AgentUpdate(name="updated-name")
        result = await AgentService.update(uow, AGENT_ID, data)

        assert result.name == "updated-name"
        uow.llm_repository.get_one_or_404.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_agent_with_llm_change_validates_llm(self):
        from rag.src.services.agent import AgentService

        uow = _make_uow()
        uow.agent_repository.update_one = AsyncMock(return_value=make_agent_obj())

        new_llm_id = uuid.uuid4()
        data = AgentUpdate(llm_id=new_llm_id)
        await AgentService.update(uow, AGENT_ID, data)

        uow.llm_repository.get_one_or_404.assert_awaited_once_with(id=new_llm_id)


class TestAgentEndpoints:
    @pytest.mark.asyncio
    async def test_create_agent(self, async_client, mock_uow):
        agent_obj = make_agent_obj()
        mock_uow.llm_repository.get_one_or_404 = AsyncMock(return_value=make_llm_obj())
        mock_uow.agent_repository.create_one = AsyncMock(return_value=agent_obj)
        mock_uow.collection_repository.get_many = AsyncMock(return_value=[])

        response = await async_client.post(
            "/api/agents",
            json={
                "name": "my-agent",
                "prompt": "You are helpful.",
                "llm_id": str(LLM_ID),
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "test-agent"
        assert body["user_id"] == str(USER_ID)

    @pytest.mark.asyncio
    async def test_create_agent_requires_auth(self):
        from httpx import ASGITransport, AsyncClient
        from rag.src.main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/agents",
                json={"name": "x", "prompt": "y", "llm_id": str(LLM_ID)},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_agents(self, async_client, mock_uow):
        mock_uow.agent_repository.get_many = AsyncMock(return_value=[make_agent_obj()])

        response = await async_client.get("/api/agents")

        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_get_agent_by_id(self, async_client, mock_uow):
        mock_uow.agent_repository.get_one_or_404 = AsyncMock(return_value=make_agent_obj())

        response = await async_client.get(f"/api/agents/{AGENT_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(AGENT_ID)

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, async_client, mock_uow):
        mock_uow.agent_repository.get_one_or_404 = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Object not found")
        )

        response = await async_client.get(f"/api/agents/{uuid.uuid4()}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_agent(self, async_client, mock_uow):
        updated = make_agent_obj()
        updated.name = "renamed"
        mock_uow.agent_repository.update_one = AsyncMock(return_value=updated)

        response = await async_client.patch(
            f"/api/agents/{AGENT_ID}",
            json={"name": "renamed"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "renamed"

    @pytest.mark.asyncio
    async def test_delete_agent(self, async_client, mock_uow):
        mock_uow.agent_repository.delete_one = AsyncMock(return_value=make_agent_obj())

        response = await async_client.delete(f"/api/agents/{AGENT_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(AGENT_ID)

    @pytest.mark.asyncio
    async def test_get_default_prompts(self, async_client):
        response = await async_client.get("/api/agents/prompts")

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        agent_types = {item["agent_type"] for item in body}
        assert AgentType.GENERAL in agent_types

    @pytest.mark.asyncio
    async def test_get_default_prompt_for_type(self, async_client):
        response = await async_client.get(f"/api/agents/prompts/{AgentType.GENERAL}")

        assert response.status_code == 200
        body = response.json()
        assert body["agent_type"] == AgentType.GENERAL
        assert isinstance(body["content"], str)
        assert len(body["content"]) > 0

    @pytest.mark.asyncio
    async def test_get_default_prompt_invalid_type(self, async_client):
        response = await async_client.get("/api/agents/prompts/nonexistent_type")

        assert response.status_code == 422
