from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.models.base import BaseModel


class Collection(BaseModel):
    __tablename__ = "collection"
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_collection_name_user"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa F821
