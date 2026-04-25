import uuid

from pydantic import BaseModel

from rag.src.common import settings


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    embedding_model: str | None = settings.llm.EMBEDDING_MODEL


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    embedding_model: str | None = None


class CollectionRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    embedding_model: str

    model_config = {"from_attributes": True}
