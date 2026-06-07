from pathlib import Path
from string import Template

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing_extensions import NotRequired

from rag.src.agent.tools.vector_search import make_vector_search_tool
from rag.src.agent.types import AgentType
from rag.src.utils.i18n import DEFAULT_LOCALE, LANGUAGE_NAMES, Locale

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class _LocalizedAgentState(AgentState):
    language: NotRequired[str]


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

        def build_prompt(state: _LocalizedAgentState) -> list[BaseMessage]:
            return [BaseAgentGraph._system_message(prompt, state.get("language")), *state["messages"]]

        return create_react_agent(
            model=llm,
            tools=tools,
            prompt=RunnableLambda(build_prompt),
            state_schema=_LocalizedAgentState,
            checkpointer=checkpointer,
        )

    @staticmethod
    def get_all_nodes(agent_type: AgentType) -> dict[str, str]:
        dir_path = _PROMPTS_DIR / agent_type.value
        if not dir_path.exists():
            return {}
        return {p.stem: p.read_text(encoding="utf-8") for p in sorted(dir_path.glob("*.md"))}

    @staticmethod
    def _render_prompt(template: str, **kwargs) -> str:
        return Template(template).safe_substitute(kwargs)

    @staticmethod
    def _localize_prompt(prompt: str, language: str | None) -> str:
        try:
            locale = Locale(language) if language else DEFAULT_LOCALE
        except ValueError:
            locale = DEFAULT_LOCALE
        if locale == DEFAULT_LOCALE:
            return prompt
        return (
            f"{prompt}\n\nIMPORTANT: Respond to the user in {LANGUAGE_NAMES[locale]}, "
            "regardless of the language used in the source documents or tool output."
        )

    @classmethod
    def _system_message(cls, prompt: str, language: str | None) -> SystemMessage:
        return SystemMessage(content=cls._localize_prompt(prompt, language))

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
