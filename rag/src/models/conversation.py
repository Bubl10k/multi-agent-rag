from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversation"

    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agent.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    messages: Mapped[list["Message"]] = relationship(  # noqa F821
        "Message", back_populates="conversation", order_by="Message.created_at", lazy="selectin"
    )
