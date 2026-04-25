import uuid

from fastapi import APIRouter, Depends, WebSocket, status

from rag.src.api.dependencies import UnitOfWorkDep, UserDep
from rag.src.api.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from rag.src.services.agent import AgentService
from rag.src.services.agent_streaming import AgentStreamingService
from rag.src.utils.ws import ws_get_user_id

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(data: AgentCreate, uow: UnitOfWorkDep, _: UserDep):
    return await AgentService.create(uow, data)


@router.get("", response_model=list[AgentRead])
async def get_agents(uow: UnitOfWorkDep, _: UserDep, page: int = 1, limit: int = 20):
    return await AgentService.get_all(uow, page, limit)


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: uuid.UUID, uow: UnitOfWorkDep, _: UserDep):
    return await AgentService.get(uow, agent_id)


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(agent_id: uuid.UUID, data: AgentUpdate, uow: UnitOfWorkDep, _: UserDep):
    return await AgentService.update(uow, agent_id, data)


@router.delete("/{agent_id}", response_model=AgentRead)
async def delete_agent(agent_id: uuid.UUID, uow: UnitOfWorkDep, _: UserDep):
    return await AgentService.delete(uow, agent_id)


@router.websocket("/{agent_id}/chat")
async def chat_with_agent(
    websocket: WebSocket,
    agent_id: uuid.UUID,
    uow: UnitOfWorkDep,
    user_id: uuid.UUID = Depends(ws_get_user_id),
):
    await AgentStreamingService.handle_ws(websocket, uow, agent_id, user_id)
