from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.models import Conversation
from rag.src.models.base import BaseModel


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    __tablename__ = "message"

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversation.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
