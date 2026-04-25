import uuid

from rag.src.api.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from rag.src.utils.unit_of_work import UnitOfWork


class AgentService:
    @staticmethod
    async def create(uow: UnitOfWork, data: AgentCreate) -> AgentRead:
        async with uow:
            await uow.llm_repository.get_one_or_404(id=data.llm_id)

            collection_ids = data.collection_ids
            payload = data.model_dump(exclude={"collection_ids"})
            agent = await uow.agent_repository.create_one(payload)

            if collection_ids:
                collections = await uow.collection_repository.get_many(
                    skip=1, limit=len(collection_ids), id=collection_ids
                )
                agent.collections = collections

            # TODO: refactor this via repository
            await uow.session.flush()
            await uow.session.refresh(agent)
            return AgentRead.model_validate(agent)

    @staticmethod
    async def get(uow: UnitOfWork, agent_id: uuid.UUID) -> AgentRead:
        async with uow:
            agent = await uow.agent_repository.get_one_or_404(id=agent_id)
            return AgentRead.model_validate(agent)

    @staticmethod
    async def get_all(uow: UnitOfWork, page: int = 1, limit: int = 20) -> list[AgentRead]:
        async with uow:
            agents = await uow.agent_repository.get_many(skip=page, limit=limit)
            return [AgentRead.model_validate(a) for a in agents]

    @staticmethod
    async def update(uow: UnitOfWork, agent_id: uuid.UUID, data: AgentUpdate) -> AgentRead:
        async with uow:
            if data.llm_id is not None:
                await uow.llm_repository.get_one_or_404(id=data.llm_id)

            collection_ids = data.collection_ids
            payload = data.model_dump(exclude_none=True, exclude={"collection_ids"})
            agent = await uow.agent_repository.update_one(str(agent_id), payload)

            if collection_ids is not None:
                collections = (
                    await uow.collection_repository.get_many(skip=1, limit=len(collection_ids), id=collection_ids)
                    if collection_ids
                    else []
                )
                agent.collections = collections

            await uow.session.flush()
            await uow.session.refresh(agent)
            return AgentRead.model_validate(agent)

    @staticmethod
    async def delete(uow: UnitOfWork, agent_id: uuid.UUID) -> AgentRead:
        async with uow:
            agent = await uow.agent_repository.delete_one(str(agent_id))
            return AgentRead.model_validate(agent)
