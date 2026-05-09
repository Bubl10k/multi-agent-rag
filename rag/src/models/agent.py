from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.models.base import Base, BaseModel
from rag.src.models.collection import Collection
from rag.src.models.llm import LLM

# m2m junction table
agent_collection = Table(
    "agent_collection",
    Base.metadata,
    Column("agent_id", ForeignKey("agent.id"), primary_key=True),
    Column("collection_id", ForeignKey("collection.id"), primary_key=True),
)


class Agent(BaseModel):
    __tablename__ = "agent"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    llm_id: Mapped[UUID] = mapped_column(ForeignKey("llm.id"), nullable=False)
    llm: Mapped[LLM] = relationship("LLM", lazy="joined")

    collections: Mapped[list[Collection]] = relationship("Collection", secondary=agent_collection, lazy="selectin")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa F821
