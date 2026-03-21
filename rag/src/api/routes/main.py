from fastapi import APIRouter

from rag.src.api.routes.documents import router as documents_router
from rag.src.api.routes.health_check import router as health_check_router
from rag.src.api.schemas.users import UserCreate, UserRead, UserUpdate
from rag.src.services.auth import auth_backend, fastapi_users

__all__ = ["router"]

router = APIRouter(prefix="/api")

router.include_router(health_check_router)
router.include_router(documents_router)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
