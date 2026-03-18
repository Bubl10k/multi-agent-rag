import logging
import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.jwt import generate_jwt

from rag.src.common import settings
from rag.src.models.user import User, UserManager

logger = logging.getLogger(__name__)

bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


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
