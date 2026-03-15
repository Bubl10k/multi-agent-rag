from typing import Annotated

from fastapi import Depends

from rag.src.services import get_document_service

DocumentServiceDep = Annotated[get_document_service, Depends()]
