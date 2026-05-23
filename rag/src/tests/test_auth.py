import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi_users.jwt import generate_jwt

from rag.src.common import settings
from rag.src.main import app
from rag.src.models.user import UserManager
from rag.src.services.auth import REFRESH_TOKEN_AUDIENCE

from rag.src.tests.helpers import USER_ID


def _refresh_jwt(user_id: uuid.UUID, jti: str) -> str:
    data = {"sub": str(user_id), "jti": jti, "aud": REFRESH_TOKEN_AUDIENCE}
    return generate_jwt(data, settings.auth.JWT_SECRET, settings.auth.REFRESH_TOKEN_LIFETIME_SECONDS)


def _mock_user_manager(user: MagicMock | None = None) -> AsyncMock:
    manager = AsyncMock(spec=UserManager)
    manager.authenticate = AsyncMock(return_value=user)
    manager.get = AsyncMock(return_value=user)
    return manager


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, mock_user, mock_uow):
        mock_uow.refresh_token_repository.create_one = AsyncMock(return_value=None)

        async def override_user_manager():
            yield _mock_user_manager(mock_user)

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "secret"},
        )

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_bad_credentials(self, async_client):
        async def override_user_manager():
            yield _mock_user_manager(user=None)

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post(
            "/api/auth/login",
            data={"username": "bad@example.com", "password": "wrong"},
        )

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 400
        assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client, mock_user):
        mock_user.is_active = False

        async def override_user_manager():
            yield _mock_user_manager(mock_user)

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "secret"},
        )

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 400


class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_success(self, async_client, mock_user, mock_uow):
        jti = str(uuid.uuid4())
        token = _refresh_jwt(USER_ID, jti)

        stored = SimpleNamespace(is_revoked=False)
        mock_uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        mock_uow.refresh_token_repository.revoke_jti = AsyncMock()
        mock_uow.refresh_token_repository.create_one = AsyncMock(return_value=None)

        async def override_user_manager():
            yield _mock_user_manager(mock_user)

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post("/api/auth/refresh", json={"refresh_token": token})

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client):
        async def override_user_manager():
            yield _mock_user_manager()

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post("/api/auth/refresh", json={"refresh_token": "not-a-jwt"})

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_reuse_detected(self, async_client, mock_uow):
        jti = str(uuid.uuid4())
        token = _refresh_jwt(USER_ID, jti)

        stored = SimpleNamespace(is_revoked=True)
        mock_uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        mock_uow.refresh_token_repository.revoke_all_for_user = AsyncMock()

        async def override_user_manager():
            yield _mock_user_manager()

        app.dependency_overrides[UserManager.get_user_manager] = override_user_manager

        response = await async_client.post("/api/auth/refresh", json={"refresh_token": token})

        del app.dependency_overrides[UserManager.get_user_manager]

        assert response.status_code == 401
        assert response.json()["detail"] == "TOKEN_REUSE_DETECTED"


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_success(self, async_client, mock_uow):
        jti = str(uuid.uuid4())
        token = _refresh_jwt(USER_ID, jti)

        stored = SimpleNamespace(is_revoked=False)
        mock_uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        mock_uow.refresh_token_repository.revoke_jti = AsyncMock()

        response = await async_client.post("/api/auth/logout", json={"refresh_token": token})

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_logout_requires_auth(self):
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/logout", json={"refresh_token": "any"})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_invalid_token_raises_401(self, async_client):
        response = await async_client.post("/api/auth/logout", json={"refresh_token": "garbage"})
        assert response.status_code == 401
