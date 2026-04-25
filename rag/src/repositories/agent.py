from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models import Agent
from rag.src.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: AsyncSession):
        super().__init__(Agent, session)
