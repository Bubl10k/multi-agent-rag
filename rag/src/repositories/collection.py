from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models import Collection
from rag.src.repositories.base import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    def __init__(self, session: AsyncSession):
        super().__init__(Collection, session)
