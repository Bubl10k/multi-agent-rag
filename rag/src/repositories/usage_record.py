import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from rag.src.models.usage_record import UsageRecord
from rag.src.repositories.base import BaseRepository


class UsageRecordRepository(BaseRepository[UsageRecord]):
    def __init__(self, session):
        super().__init__(UsageRecord, session)

    async def get_request_count(self, user_id: uuid.UUID, hour: datetime) -> int:
        result = await self.session.execute(
            select(UsageRecord.request_count).where(
                UsageRecord.user_id == user_id,
                UsageRecord.hour == hour,
            )
        )
        return result.scalar_one_or_none() or 0

    async def increment(self, user_id: uuid.UUID, hour: datetime) -> None:
        stmt = (
            insert(UsageRecord)
            .values(user_id=user_id, hour=hour, request_count=1)
            .on_conflict_do_update(
                index_elements=["user_id", "hour"],
                set_={"request_count": UsageRecord.request_count + 1, "updated_at": func.now()},
            )
        )
        await self.session.execute(stmt)
