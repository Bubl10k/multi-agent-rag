import logging

from fastapi import UploadFile, status
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.src.api.schemas.documents import (
    CollectionFilesResponse,
    DocumentSearchResult,
    ParsedDocumentResponse,
    SearchDocumentsResponse,
    UploadDocumentResponse,
)
from rag.src.db.vector_store import VectorStore
from rag.src.repositories.vector_store import VectorStoreRepository
from rag.src.utils.exceptions import LocalizedHTTPException
from rag.src.utils.parsers import SUPPORTED_CONTENT_TYPES, extract_text

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


class DocumentService:
    @staticmethod
    async def upload_file_to_store(file: UploadFile, collection_name: str) -> UploadDocumentResponse:
        logger.info(
            "Uploading file '%s' (type=%s) to collection '%s'", file.filename, file.content_type, collection_name
        )

        if file.content_type not in SUPPORTED_CONTENT_TYPES:
            logger.warning("Rejected unsupported file type '%s' (file=%s)", file.content_type, file.filename)
            raise LocalizedHTTPException(
                status_code=415,
                detail="UNSUPPORTED_FILE_TYPE",
                content_type=file.content_type,
                supported=", ".join(sorted(SUPPORTED_CONTENT_TYPES)),
            )

        raw = await file.read()
        text = extract_text(raw, file.content_type)

        splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        chunks = splitter.split_text(text)

        store = VectorStore(collection_name=collection_name)
        ids = store.add_texts(chunks, metadatas=[{"source": file.filename}] * len(chunks))

        logger.info("Stored %d chunks from '%s' into collection '%s'", len(ids), file.filename, collection_name)
        return UploadDocumentResponse(collection=collection_name, chunks_stored=len(ids))

    @staticmethod
    async def search_in_store(query: str, collection_name: str, k: int = 4) -> SearchDocumentsResponse:
        logger.info("Searching in collection '%s' with query='%s', k=%d", collection_name, query, k)

        store = VectorStore(collection_name=collection_name)
        results = store.search_with_score(query, k=k)

        return SearchDocumentsResponse(
            collection=collection_name,
            query=query,
            results=[
                DocumentSearchResult(content=doc.page_content, metadata=doc.metadata, score=score)
                for doc, score in results
            ],
        )

    @staticmethod
    async def parse_file(file: UploadFile) -> ParsedDocumentResponse:
        logger.info("Parsing file '%s' (type=%s)", file.filename, file.content_type)

        if file.content_type not in SUPPORTED_CONTENT_TYPES:
            logger.warning("Rejected unsupported file type '%s' (file=%s)", file.content_type, file.filename)
            raise LocalizedHTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="UNSUPPORTED_FILE_TYPE",
                content_type=file.content_type,
                supported=", ".join(sorted(SUPPORTED_CONTENT_TYPES)),
            )

        raw = await file.read()
        content = extract_text(raw, file.content_type)
        return ParsedDocumentResponse(filename=file.filename, content=content)

    @staticmethod
    def get_collection_files(collection_name: str) -> CollectionFilesResponse:
        logger.info("Fetching files for collection '%s'", collection_name)
        files = VectorStoreRepository(collection_name).get_files()
        return CollectionFilesResponse(collection=collection_name, files=files)


document_service = DocumentService()
