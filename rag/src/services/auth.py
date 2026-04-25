import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.jwt import decode_jwt, generate_jwt

from rag.src.api.schemas.auth import InvalidDetailsEnum, TokenResponse
from rag.src.common import settings
from rag.src.models.user import User, UserManager
from rag.src.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

REFRESH_TOKEN_AUDIENCE = "rag:refresh"

bearer_transport = BearerTransport(tokenUrl="/api/auth/login")


class CustomJWTStrategy(JWTStrategy):
    async def write_token(self, user: User) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "email": user.email,
        }
        return generate_jwt(data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm)


def get_jwt_strategy() -> CustomJWTStrategy:
    return CustomJWTStrategy(
        secret=settings.auth.JWT_SECRET,
        lifetime_seconds=settings.auth.JWT_LIFETIME_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    UserManager.get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)


class AuthService:
    @staticmethod
    def _make_access_token(user: User) -> str:
        data = {"sub": str(user.id), "aud": "fastapi-users:auth", "email": user.email}
        return generate_jwt(data, settings.auth.JWT_SECRET, settings.auth.JWT_LIFETIME_SECONDS)

    @staticmethod
    def _make_refresh_token(user: User) -> tuple[str, str]:
        jti = str(uuid.uuid4())
        data = {"sub": str(user.id), "jti": jti, "aud": REFRESH_TOKEN_AUDIENCE}
        token = generate_jwt(data, settings.auth.JWT_SECRET, settings.auth.REFRESH_TOKEN_LIFETIME_SECONDS)
        return token, jti

    async def create_token_pair(self, uow: UnitOfWork, user: User) -> TokenResponse:
        access_token = self._make_access_token(user)
        refresh_token, jti = self._make_refresh_token(user)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.auth.REFRESH_TOKEN_LIFETIME_SECONDS)
        async with uow:
            await uow.refresh_token_repository.create_one(
                {
                    "user_id": user.id,
                    "jti": jti,
                    "expires_at": expires_at,
                    "is_revoked": False,
                    "created_at": datetime.now(timezone.utc),
                }
            )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    async def refresh_tokens(self, uow: UnitOfWork, refresh_token_str: str, user_manager: UserManager) -> TokenResponse:
        try:
            data = decode_jwt(refresh_token_str, settings.auth.JWT_SECRET, [REFRESH_TOKEN_AUDIENCE])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.INVALID_REFRESH_TOKEN
            )

        jti = data.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.INVALID_REFRESH_TOKEN
            )

        user_id = uuid.UUID(data["sub"])
        reuse_detected = False
        user = None

        async with uow:
            stored = await uow.refresh_token_repository.get_by_jti(jti)

            if stored is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.INVALID_REFRESH_TOKEN
                )

            if stored.is_revoked:
                # Raise after async with so UoW can commit the revocation
                await uow.refresh_token_repository.revoke_all_for_user(user_id)
                reuse_detected = True
            else:
                user = await user_manager.get(user_id)
                if not user or not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.USER_INACTIVE
                    )
                await uow.refresh_token_repository.revoke_jti(jti)

        if reuse_detected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.TOKEN_REUSE_DETECTED
            )

        return await self.create_token_pair(uow, user)

    @staticmethod
    async def revoke_refresh_token(uow: UnitOfWork, refresh_token_str: str) -> None:
        try:
            data = decode_jwt(refresh_token_str, settings.auth.JWT_SECRET, [REFRESH_TOKEN_AUDIENCE])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=InvalidDetailsEnum.INVALID_REFRESH_TOKEN
            )

        jti = data.get("jti")
        if not jti:
            return

        async with uow:
            stored = await uow.refresh_token_repository.get_by_jti(jti)
            if stored and not stored.is_revoked:
                await uow.refresh_token_repository.revoke_jti(jti)
