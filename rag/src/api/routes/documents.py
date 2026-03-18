from fastapi import APIRouter, UploadFile

from rag.src.api.dependencies import DocumentServiceDep
from rag.src.api.schemas.documents import SearchDocumentsResponse, UploadDocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document_to_vector_store(
    file: UploadFile,
    collection_name: str,
    document_service: DocumentServiceDep,
):
    return await document_service.upload_file_to_store(file=file, collection_name=collection_name)


@router.get("/search", response_model=SearchDocumentsResponse)
async def search_vector_store(
    collection_name: str,
    query: str,
    k: int = 4,
    document_service: DocumentServiceDep = ...,
):
    return await document_service.search_in_store(query=query, collection_name=collection_name, k=k)
