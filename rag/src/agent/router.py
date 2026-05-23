import logging
from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from typing_extensions import TypedDict

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import RouterNode
from rag.src.agent.invoice import InvoiceAgentGraph
from rag.src.agent.math import MathAgentGraph
from rag.src.agent.programming import ProgrammingAgentGraph
from rag.src.agent.researcher import ResearcherAgentGraph
from rag.src.agent.types import AgentType

logger = logging.getLogger(__name__)

_SUB_AGENT_CLASSES: dict[AgentType, type[BaseAgentGraph]] = {
    AgentType.GENERAL: BaseAgentGraph,
    AgentType.PROGRAMMING: ProgrammingAgentGraph,
    AgentType.MATH: MathAgentGraph,
    AgentType.RESEARCHER: ResearcherAgentGraph,
    AgentType.INVOICE: InvoiceAgentGraph,
}


class RouterDecision(BaseModel):
    agent_type: AgentType
    reasoning: str


class RouterState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    selected_agent: str


class RouterAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.system_msg = SystemMessage(content=prompt)
        self.collection_names = collection_names
        self.checkpointer = checkpointer
        self.agent_config = agent_config

    def _build_sub_agents(self) -> dict[AgentType, CompiledStateGraph]:
        from rag.src.services.prompt import PromptService  # lazy import to avoid circular dependency

        sub_configs: dict = self.agent_config.get("sub_agent_configs", {})
        agents: dict[AgentType, CompiledStateGraph] = {}
        for agent_type, klass in _SUB_AGENT_CLASSES.items():
            config = sub_configs.get(agent_type.value, {})
            prompt = PromptService.get(agent_type)
            # Sub-agents are compiled without a checkpointer; the parent router handles persistence.
            agents[agent_type] = klass.create_agent_graph(
                llm=self.llm,
                collection_names=self.collection_names,
                prompt=prompt,
                checkpointer=None,
                agent_config=config,
            )
        return agents

    async def route(self, state: RouterState) -> dict:
        structured_llm = self.llm.with_structured_output(RouterDecision)
        result: RouterDecision = await structured_llm.ainvoke([self.system_msg] + list(state["messages"]))
        logger.info("Router selected: %s (%s)", result.agent_type, result.reasoning)
        return {"selected_agent": result.agent_type}

    def _build(self, sub_agents: dict[AgentType, CompiledStateGraph]) -> CompiledStateGraph:
        graph = StateGraph(RouterState)
        graph.add_node(RouterNode.ROUTE, self.route)

        for agent_type, subgraph in sub_agents.items():
            node_name = RouterNode(agent_type.value)
            graph.add_node(node_name, subgraph)
            graph.add_edge(node_name, END)

        graph.set_entry_point(RouterNode.ROUTE)
        graph.add_conditional_edges(
            RouterNode.ROUTE,
            lambda state: RouterNode(state["selected_agent"]),
            {RouterNode(t.value): RouterNode(t.value) for t in sub_agents},
        )

        compiled = graph.compile(checkpointer=self.checkpointer)

        output_node_names: set[str] = set()
        for subgraph in sub_agents.values():
            nodes = getattr(subgraph, "output_nodes", None)
            if nodes:
                output_node_names.update(nodes)
            else:
                output_node_names.add("agent")
        compiled.output_nodes = frozenset(output_node_names)

        return compiled

    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        instance = RouterAgentGraph(llm, collection_names, prompt, checkpointer, agent_config or {})
        sub_agents = instance._build_sub_agents()
        return instance._build(sub_agents)
