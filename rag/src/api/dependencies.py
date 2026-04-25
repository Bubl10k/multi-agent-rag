from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.db.postgres import get_async_session
from rag.src.models import User
from rag.src.models.user import UserManager
from rag.src.services.auth import current_active_user
from rag.src.services.document import DocumentService
from rag.src.utils.unit_of_work import UnitOfWork

UnitOfWorkDep = Annotated[UnitOfWork, Depends(UnitOfWork)]
DocumentServiceDep = Annotated[DocumentService, Depends(DocumentService)]
UserDep = Annotated[User, Depends(current_active_user)]
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
UserManagerDep = Annotated[UserManager, Depends(UserManager.get_user_manager)]
CurrentUserDep = Annotated[User, Depends(current_active_user)]
