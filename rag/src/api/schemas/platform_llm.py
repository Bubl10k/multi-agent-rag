import uuid

from pydantic import BaseModel


class PlatformLLMBasicRead(BaseModel):
    id: uuid.UUID
    display_name: str
    model_name: str
    provider: str
    is_active: bool

    model_config = {"from_attributes": True}


class PlatformLLMRead(PlatformLLMBasicRead):
    requests_used: int
    requests_limit: int
