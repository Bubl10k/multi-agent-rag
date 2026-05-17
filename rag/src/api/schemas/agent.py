import uuid

from pydantic import BaseModel

from rag.src.agent.types import AgentType
from rag.src.api.schemas.collection import CollectionRead
from rag.src.api.schemas.llm import LLMRead


class AgentCreate(BaseModel):
    name: str
    prompt: str
    llm_id: uuid.UUID
    agent_type: AgentType = AgentType.GENERAL
    agent_config: dict = {}
    collection_ids: list[uuid.UUID] = []
    is_active: bool = True


class AgentUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    llm_id: uuid.UUID | None = None
    agent_type: AgentType | None = None
    agent_config: dict | None = None
    collection_ids: list[uuid.UUID] | None = None
    is_active: bool | None = None


class AgentRead(BaseModel):
    id: uuid.UUID
    name: str
    prompt: str
    agent_type: AgentType
    agent_config: dict | list = []
    is_active: bool
    user_id: uuid.UUID
    llm: LLMRead
    collections: list[CollectionRead]

    model_config = {"from_attributes": True}


class AgentChatRequest(BaseModel):
    message: str


class GraphNode(BaseModel):
    id: str
    name: str


class GraphEdge(BaseModel):
    source: str
    target: str
    data: str | None
    conditional: bool


class AgentGraphJSON(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class AgentGraphMermaid(BaseModel):
    mermaid: str


class AgentDefaultPrompt(BaseModel):
    agent_type: AgentType
    content: str
