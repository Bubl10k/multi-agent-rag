from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag.src.models.base import BaseModel


class LLM(BaseModel):
    __tablename__ = "llm"

    api_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa F821
