from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    collection: str
    chunks_stored: int