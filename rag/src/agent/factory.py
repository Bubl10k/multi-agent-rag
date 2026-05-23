from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.invoice import InvoiceAgentGraph
from rag.src.agent.math import MathAgentGraph
from rag.src.agent.programming import ProgrammingAgentGraph
from rag.src.agent.researcher import ResearcherAgentGraph
from rag.src.agent.router import RouterAgentGraph
from rag.src.agent.types import AgentType


class AgentGraphFactory:
    _registry: dict[AgentType, type[BaseAgentGraph]] = {
        AgentType.GENERAL: BaseAgentGraph,
        AgentType.PROGRAMMING: ProgrammingAgentGraph,
        AgentType.MATH: MathAgentGraph,
        AgentType.RESEARCHER: ResearcherAgentGraph,
        AgentType.INVOICE: InvoiceAgentGraph,
        AgentType.ROUTER: RouterAgentGraph,
    }

    @classmethod
    def create(
        cls,
        agent_type: AgentType,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict,
    ) -> CompiledStateGraph:
        klass = cls._registry.get(agent_type, BaseAgentGraph)
        return klass.create_agent_graph(
            llm=llm,
            collection_names=collection_names,
            prompt=prompt,
            checkpointer=checkpointer,
            agent_config=agent_config,
        )
