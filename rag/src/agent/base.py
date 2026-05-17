from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from rag.src.agent.tools.vector_search import make_vector_search_tool


class BaseAgentGraph:
    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        tools = [make_vector_search_tool(name) for name in collection_names]
        return create_react_agent(
            model=llm,
            tools=tools,
            prompt=prompt,
            checkpointer=checkpointer,
        )

    @staticmethod
    def get_graph_mermaid(graph: CompiledStateGraph) -> str:
        return graph.get_graph().draw_mermaid()

    @staticmethod
    def get_graph_json(graph: CompiledStateGraph) -> dict:
        g = graph.get_graph()
        return {
            "nodes": [{"id": n.id, "name": n.name} for n in g.nodes.values()],
            "edges": [
                {"source": e.source, "target": e.target, "data": e.data, "conditional": e.conditional} for e in g.edges
            ],
        }
