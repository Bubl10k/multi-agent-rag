from typing import Annotated

from fastapi import Depends

from rag.src.models import User
from rag.src.services.auth import current_active_user
from rag.src.services.document import DocumentService
from rag.src.utils.unit_of_work import UnitOfWork

UnitOfWorkDep = Annotated[UnitOfWork, Depends(UnitOfWork)]
DocumentServiceDep = Annotated[DocumentService, Depends(DocumentService)]
UserDep = Annotated[User, Depends(current_active_user)]
