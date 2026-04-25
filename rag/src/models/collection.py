from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rag.src.models.base import BaseModel


# TODO: add relationships with user
class Collection(BaseModel):
    __tablename__ = "collection"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False)
