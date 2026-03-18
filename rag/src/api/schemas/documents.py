from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    collection: str
    chunks_stored: int


class DocumentSearchResult(BaseModel):
    content: str
    metadata: dict
    score: float


class SearchDocumentsResponse(BaseModel):
    collection: str
    query: str
    results: list[DocumentSearchResult]
