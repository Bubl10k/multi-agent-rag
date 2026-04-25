from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models.message import Message, MessageRole
from rag.src.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_last_n(self, conversation_id: str, n: int) -> list[Message]:
        query = select(Message).from_statement(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(n)
        )
        result = await self.session.execute(query)
        messages = result.scalars().all()
        return list(reversed(messages))

    async def delete_by_conversation(self, conversation_id: str) -> None:
        query = delete(Message).where(Message.conversation_id == conversation_id)
        await self.session.execute(query)
        await self.session.commit()

    async def save(self, conversation_id: str, role: MessageRole, content: str) -> Message:
        return await self.create_one(
            {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }
        )
