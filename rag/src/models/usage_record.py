from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from rag.src.models.base import BaseModel


class UsageRecord(BaseModel):
    __tablename__ = "usage_record"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    hour: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("user_id", "hour", name="uq_usage_record_user_hour"),)
