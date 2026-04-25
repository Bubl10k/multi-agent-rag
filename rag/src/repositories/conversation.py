from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models.conversation import Conversation
from rag.src.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)
