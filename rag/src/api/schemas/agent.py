import uuid

from pydantic import BaseModel

from rag.src.api.schemas.collection import CollectionRead
from rag.src.api.schemas.llm import LLMRead


class AgentCreate(BaseModel):
    name: str
    prompt: str
    llm_id: uuid.UUID
    tool_calls: list = []
    collection_ids: list[uuid.UUID] = []
    is_active: bool = True


class AgentUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    llm_id: uuid.UUID | None = None
    tool_calls: list | None = None
    collection_ids: list[uuid.UUID] | None = None
    is_active: bool | None = None


class AgentRead(BaseModel):
    id: uuid.UUID
    name: str
    prompt: str
    tool_calls: list
    is_active: bool
    user_id: uuid.UUID
    llm: LLMRead
    collections: list[CollectionRead]

    model_config = {"from_attributes": True}


class AgentChatRequest(BaseModel):
    message: str
