import uuid
from datetime import datetime

from pydantic import BaseModel

from rag.src.models.message import MessageRole


class MessageRead(BaseModel):
    id: uuid.UUID
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    messages: list[MessageRead]

    model_config = {"from_attributes": True}
