from fastapi import APIRouter, UploadFile

from rag.src.api.dependencies import DocumentServiceDep, UserDep
from rag.src.api.schemas.documents import (
    CollectionFilesResponse,
    ParsedDocumentResponse,
    SearchDocumentsResponse,
    UploadDocumentResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document_to_vector_store(
    file: UploadFile,
    collection_name: str,
    document_service: DocumentServiceDep,
    _: UserDep,
):
    return await document_service.upload_file_to_store(file=file, collection_name=collection_name)


@router.post("/parse", response_model=ParsedDocumentResponse)
async def parse_document(
    file: UploadFile,
    document_service: DocumentServiceDep,
    _: UserDep,
):
    return await document_service.parse_file(file=file)


@router.get("/files", response_model=CollectionFilesResponse)
async def get_collection_files(
    collection_name: str,
    document_service: DocumentServiceDep,
    _: UserDep,
):
    return document_service.get_collection_files(collection_name=collection_name)


@router.get("/search", response_model=SearchDocumentsResponse)
async def search_vector_store(
    collection_name: str,
    query: str,
    document_service: DocumentServiceDep,
    _: UserDep,
    k: int = 4,
):
    return await document_service.search_in_store(query=query, collection_name=collection_name, k=k)
