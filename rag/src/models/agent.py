from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.agent.types import AgentType
from rag.src.models.base import Base, BaseModel
from rag.src.models.collection import Collection
from rag.src.models.llm import LLM
from rag.src.models.platform_llm import PlatformLLM

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
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, default=AgentType.GENERAL)
    agent_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    llm_id: Mapped[UUID | None] = mapped_column(ForeignKey("llm.id"), nullable=True)
    llm: Mapped[LLM | None] = relationship("LLM", lazy="joined")

    platform_llm_id: Mapped[UUID | None] = mapped_column(ForeignKey("platform_llm.id"), nullable=True)
    platform_llm: Mapped[PlatformLLM | None] = relationship("PlatformLLM", lazy="joined")

    collections: Mapped[list[Collection]] = relationship("Collection", secondary=agent_collection, lazy="selectin")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa F821
