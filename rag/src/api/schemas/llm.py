import uuid

from pydantic import BaseModel


class LLMCreate(BaseModel):
    model_name: str
    api_key: str  # plain string - encryption happens in the service layer
    is_active: bool = True


class LLMUpdate(BaseModel):
    model_name: str | None = None
    api_key: str | None = None
    is_active: bool | None = None


class LLMRead(BaseModel):
    id: uuid.UUID
    model_name: str
    is_active: bool

    model_config = {"from_attributes": True}
