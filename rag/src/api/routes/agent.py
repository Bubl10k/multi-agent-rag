import uuid

from fastapi import APIRouter, Depends, WebSocket, status

from rag.src.agent import BaseAgentGraph
from rag.src.agent.types import AgentType
from rag.src.api.dependencies import AgentServiceDep, AgentStreamingServiceDep, UnitOfWorkDep, UserDep
from rag.src.api.schemas.agent import (
    AgentCreate,
    AgentDefaultPrompt,
    AgentGraphJSON,
    AgentGraphMermaid,
    AgentRead,
    AgentUpdate,
)
from rag.src.services.agent_streaming import AgentStreamingService
from rag.src.services.prompt import PromptService
from rag.src.utils.ws import ws_get_user_id

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(data: AgentCreate, uow: UnitOfWorkDep, service: AgentServiceDep, user: UserDep):
    return await service.create(uow, data, user.id)


@router.get("", response_model=list[AgentRead])
async def get_agents(service: AgentServiceDep, _: UserDep, uow: UnitOfWorkDep, page: int = 1, limit: int = 20):
    return await service.get_all(uow, page, limit)


@router.get("/prompts", response_model=list[AgentDefaultPrompt])
async def get_default_prompts(_: UserDep):
    return [
        AgentDefaultPrompt(agent_type=agent_type, content=content)
        for agent_type, content in PromptService.get_all().items()
    ]


@router.get("/prompts/{agent_type}", response_model=AgentDefaultPrompt)
async def get_default_prompt(agent_type: AgentType, _: UserDep):
    return AgentDefaultPrompt(agent_type=agent_type, content=PromptService.get(agent_type))


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: uuid.UUID, uow: UnitOfWorkDep, service: AgentServiceDep, _: UserDep):
    return await service.get(uow, agent_id)


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: uuid.UUID, data: AgentUpdate, uow: UnitOfWorkDep, service: AgentServiceDep, _: UserDep
):
    return await service.update(uow, agent_id, data)


@router.delete("/{agent_id}", response_model=AgentRead)
async def delete_agent(agent_id: uuid.UUID, uow: UnitOfWorkDep, service: AgentServiceDep, _: UserDep):
    return await service.delete(uow, agent_id)


@router.get("/{agent_id}/graph/json", response_model=AgentGraphJSON)
async def get_agent_graph_json(agent_id: uuid.UUID, uow: UnitOfWorkDep, service: AgentStreamingServiceDep, _: UserDep):
    graph, _ = await service.build_graph(uow, agent_id)
    return BaseAgentGraph.get_graph_json(graph)


@router.get("/{agent_id}/graph/mermaid", response_model=AgentGraphMermaid)
async def get_agent_graph_mermaid(agent_id: uuid.UUID, uow: UnitOfWorkDep, _: UserDep):
    graph, _ = await AgentStreamingService.build_graph(uow, agent_id)
    return AgentGraphMermaid(mermaid=BaseAgentGraph.get_graph_mermaid(graph))


# TODO: add separate router for ws
@router.websocket("/{agent_id}/chat")
async def chat_with_agent(
    websocket: WebSocket,
    agent_id: uuid.UUID,
    uow: UnitOfWorkDep,
    service: AgentStreamingServiceDep,
    user_id: uuid.UUID = Depends(ws_get_user_id),
):
    await service.handle_ws(websocket, uow, agent_id, user_id)
