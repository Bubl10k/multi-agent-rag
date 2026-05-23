import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi_users.jwt import generate_jwt

from rag.src.api.schemas.auth import InvalidDetailsEnum, TokenResponse
from rag.src.common import settings
from rag.src.services.auth import REFRESH_TOKEN_AUDIENCE, AuthService

JWT_SECRET = settings.auth.JWT_SECRET


def _make_refresh_token_jwt(user_id: uuid.UUID, jti: str, expired: bool = False) -> str:
    lifetime = -1 if expired else settings.auth.REFRESH_TOKEN_LIFETIME_SECONDS
    data = {"sub": str(user_id), "jti": jti, "aud": REFRESH_TOKEN_AUDIENCE}
    return generate_jwt(data, JWT_SECRET, lifetime)


def _make_user(user_id: uuid.UUID | None = None) -> MagicMock:
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    user.email = "test@example.com"
    user.is_active = True
    return user


def _make_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.refresh_token_repository = AsyncMock()
    return uow


class TestCreateTokenPair:
    @pytest.mark.asyncio
    async def test_returns_token_response(self):
        user = _make_user()
        uow = _make_uow()
        uow.refresh_token_repository.create_one = AsyncMock(return_value=None)

        service = AuthService()
        result = await service.create_token_pair(uow, user)

        assert isinstance(result, TokenResponse)
        assert result.token_type == "bearer"
        assert result.access_token
        assert result.refresh_token
        uow.refresh_token_repository.create_one.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stores_refresh_token_with_correct_fields(self):
        user = _make_user()
        uow = _make_uow()
        uow.refresh_token_repository.create_one = AsyncMock(return_value=None)

        service = AuthService()
        await service.create_token_pair(uow, user)

        call_data = uow.refresh_token_repository.create_one.call_args[0][0]
        assert call_data["user_id"] == user.id
        assert call_data["is_revoked"] is False
        assert "jti" in call_data
        assert "expires_at" in call_data


class TestRefreshTokens:
    @pytest.mark.asyncio
    async def test_valid_token_returns_new_pair(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        stored = SimpleNamespace(is_revoked=False)
        user = _make_user(user_id)

        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        uow.refresh_token_repository.revoke_jti = AsyncMock()
        uow.refresh_token_repository.create_one = AsyncMock(return_value=None)

        user_manager = AsyncMock()
        user_manager.get = AsyncMock(return_value=user)

        service = AuthService()
        result = await service.refresh_tokens(uow, token, user_manager)

        assert isinstance(result, TokenResponse)
        uow.refresh_token_repository.revoke_jti.assert_awaited_once_with(jti)

    @pytest.mark.asyncio
    async def test_invalid_jwt_raises_401(self):
        uow = _make_uow()
        user_manager = AsyncMock()

        service = AuthService()
        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_tokens(uow, "not-a-valid-token", user_manager)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == InvalidDetailsEnum.INVALID_REFRESH_TOKEN

    @pytest.mark.asyncio
    async def test_token_not_in_db_raises_401(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=None)
        user_manager = AsyncMock()

        service = AuthService()
        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_tokens(uow, token, user_manager)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == InvalidDetailsEnum.INVALID_REFRESH_TOKEN

    @pytest.mark.asyncio
    async def test_revoked_token_triggers_reuse_detection(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        stored = SimpleNamespace(is_revoked=True)
        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        uow.refresh_token_repository.revoke_all_for_user = AsyncMock()
        user_manager = AsyncMock()

        service = AuthService()
        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_tokens(uow, token, user_manager)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == InvalidDetailsEnum.TOKEN_REUSE_DETECTED
        uow.refresh_token_repository.revoke_all_for_user.assert_awaited_once_with(user_id)

    @pytest.mark.asyncio
    async def test_inactive_user_raises_401(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        stored = SimpleNamespace(is_revoked=False)
        inactive_user = _make_user(user_id)
        inactive_user.is_active = False

        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        user_manager = AsyncMock()
        user_manager.get = AsyncMock(return_value=inactive_user)

        service = AuthService()
        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_tokens(uow, token, user_manager)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == InvalidDetailsEnum.USER_INACTIVE


class TestRevokeRefreshToken:
    @pytest.mark.asyncio
    async def test_valid_active_token_is_revoked(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        stored = SimpleNamespace(is_revoked=False)
        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        uow.refresh_token_repository.revoke_jti = AsyncMock()

        await AuthService.revoke_refresh_token(uow, token)
        uow.refresh_token_repository.revoke_jti.assert_awaited_once_with(jti)

    @pytest.mark.asyncio
    async def test_already_revoked_token_is_not_revoked_again(self):
        user_id = uuid.uuid4()
        jti = str(uuid.uuid4())
        token = _make_refresh_token_jwt(user_id, jti)

        stored = SimpleNamespace(is_revoked=True)
        uow = _make_uow()
        uow.refresh_token_repository.get_by_jti = AsyncMock(return_value=stored)
        uow.refresh_token_repository.revoke_jti = AsyncMock()

        await AuthService.revoke_refresh_token(uow, token)
        uow.refresh_token_repository.revoke_jti.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        uow = _make_uow()
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.revoke_refresh_token(uow, "garbage-token")
        assert exc_info.value.status_code == 401
