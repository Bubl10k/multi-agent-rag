from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from rag.src.models.base import BaseModel


class PlatformLLM(BaseModel):
    __tablename__ = "platform_llm"

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
