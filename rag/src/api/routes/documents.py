from fastapi import APIRouter, UploadFile

from rag.src.api.dependencies import DocumentServiceDep
from rag.src.api.schemas.documents import UploadDocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document_to_vector_store(
    file: UploadFile,
    collection_name: str,
    document_service: DocumentServiceDep,
):
    return await document_service.upload_file_to_store(file=file, collection_name=collection_name)
