import typing
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.db import async_session
from rag.src.repositories.agent import AgentRepository
from rag.src.repositories.collection import CollectionRepository
from rag.src.repositories.conversation import ConversationRepository
from rag.src.repositories.llm import LLMRepository
from rag.src.repositories.message import MessageRepository
from rag.src.repositories.refresh_token import RefreshTokenRepository


class AbstractUnitOfWork(ABC):
    session: AsyncSession

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: typing.Any) -> None:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.session_maker = async_session

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_maker()

        # List of all repositories:
        self.agent_repository = AgentRepository(self.session)
        self.collection_repository = CollectionRepository(self.session)
        self.llm_repository = LLMRepository(self.session)
        self.conversation_repository = ConversationRepository(self.session)
        self.message_repository = MessageRepository(self.session)
        self.refresh_token_repository = RefreshTokenRepository(self.session)

        return self

    async def __aexit__(self, exc_type: typing.Any, exc: typing.Any, tb: typing.Any) -> None:
        if not exc:
            await self.session.commit()
            await self.session.close()
            return

        await self.session.rollback()
        await self.session.close()
        raise exc
