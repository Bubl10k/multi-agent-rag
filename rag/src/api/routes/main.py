from fastapi import APIRouter

from rag.src.api.routes.health_check import router as health_check_router

__all__ = ["router"]

router = APIRouter(prefix="/api")

router.include_router(health_check_router)
