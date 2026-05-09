from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from rag.src.agent.tool_calls import make_vector_search_tool


class BaseAgentGraph:
    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
    ) -> CompiledStateGraph:
        tools = [make_vector_search_tool(name) for name in collection_names]
        return create_react_agent(
            model=llm,
            tools=tools,
            prompt=prompt,
            checkpointer=checkpointer,
        )
