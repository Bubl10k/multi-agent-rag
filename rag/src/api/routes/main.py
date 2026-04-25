from fastapi import APIRouter

from rag.src.api.routes.agent import router as agent_router
from rag.src.api.routes.auth import router as auth_router
from rag.src.api.routes.collection import router as collection_router
from rag.src.api.routes.conversation import router as conversation_router
from rag.src.api.routes.documents import router as documents_router
from rag.src.api.routes.health_check import router as health_check_router
from rag.src.api.routes.llm import router as llm_router
from rag.src.api.schemas.users import UserCreate, UserRead, UserUpdate
from rag.src.services.auth import fastapi_users

__all__ = ["router"]

router = APIRouter(prefix="/api")

router.include_router(health_check_router)
router.include_router(documents_router)
router.include_router(conversation_router)
router.include_router(collection_router)
router.include_router(llm_router)
router.include_router(agent_router)
router.include_router(auth_router)
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
