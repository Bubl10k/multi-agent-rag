import logging
import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.common import settings
from rag.src.db.postgres import get_async_session
from rag.src.models.base import Base

logger = logging.getLogger(__name__)


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth.JWT_SECRET
    verification_token_secret = settings.auth.JWT_SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info("User %s registered.", {user.id})

    @staticmethod
    async def get_user_manager(user_db=Depends(get_user_db)):
        yield UserManager(user_db)
