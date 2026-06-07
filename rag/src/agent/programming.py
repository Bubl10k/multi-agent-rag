import asyncio
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import ProgrammingNode
from rag.src.agent.schemes import ExecuteOutput, FinalAnswerOutput, PlanOutput, ReviewOutput, WriteCodeOutput
from rag.src.agent.states import ProgrammingState
from rag.src.agent.tools.code_execution import execute_in_sandbox
from rag.src.agent.tools.vector_search import make_vector_search_tool
from rag.src.agent.types import AgentType

logger = logging.getLogger(__name__)

_DEFAULT_ALLOWED_MODULES = ["math", "json", "re", "itertools", "datetime"]


class ProgrammingAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.prompt = prompt
        self.max_retries: int = agent_config.get("max_retries", 1)
        self.timeout: float = agent_config.get("execution_timeout_seconds", 10)
        self.allowed_modules: list[str] = agent_config.get("allowed_modules", _DEFAULT_ALLOWED_MODULES)
        self.search_tools: list[StructuredTool] = [make_vector_search_tool(name) for name in collection_names]
        self._prompts = self.get_all_nodes(AgentType.PROGRAMMING)

    async def _gather_context(self, query: str) -> str:
        if not self.search_tools:
            return ""
        results = await asyncio.gather(*[t.ainvoke({"query": query}) for t in self.search_tools])
        useful = [r for r in results if r and r != "No relevant documents found."]
        return "\n\n".join(useful)

    @staticmethod
    def _response_text(content: str | list) -> str:
        if isinstance(content, list):
            return "".join(
                block["text"] if isinstance(block, dict) and block.get("type") == "text" else str(block)
                for block in content
            )
        return content

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            return "\n".join(lines[1:end])
        return text

    async def plan(self, state: ProgrammingState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        context = await self._gather_context(str(user_question))

        context_section = f"\n\nRelevant context from knowledge base:\n{context}" if context else ""
        content = self._render_prompt(
            self._prompts["plan"],
            user_question=user_question,
            context_section=context_section,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        return PlanOutput(
            plan=self._response_text(response.content),
            retry_count=0,
            max_retries=self.max_retries,
        ).model_dump()

    async def write_code(self, state: ProgrammingState) -> dict:
        error_hint = ""
        if state.get("retry_count", 0) > 0 and state.get("stderr"):
            error_hint = (
                f"\n\nPrevious attempt failed.\n"
                f"Code:\n```python\n{state['code']}\n```\n"
                f"Error:\n{state['stderr']}\n\n"
                f"Fix the issue based on the revised plan above."
            )
        content = self._render_prompt(
            self._prompts["write_code"],
            plan=state["plan"],
            error_hint=error_hint,
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        return WriteCodeOutput(
            code=self._strip_code_fences(self._response_text(response.content)),
        ).model_dump()

    async def execute(self, state: ProgrammingState) -> dict:
        logger.info("Executing code (attempt %d)", state.get("retry_count", 0) + 1)
        result = await execute_in_sandbox(
            code=state["code"],
            timeout=self.timeout,
            allowed_modules=self.allowed_modules,
        )
        return ExecuteOutput(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
        ).model_dump()

    async def review(self, state: ProgrammingState) -> dict:
        content = self._render_prompt(
            self._prompts["review"],
            plan=state["plan"],
            code=state["code"],
            stderr=state["stderr"],
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        return ReviewOutput(
            plan=self._response_text(response.content),
            retry_count=state.get("retry_count", 0) + 1,
        ).model_dump()

    async def explain(self, state: ProgrammingState) -> dict:
        content = self._render_prompt(
            self._prompts["explain"],
            code=state["code"],
            stdout=state["stdout"],
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {**FinalAnswerOutput(final_answer=text).model_dump(), "messages": [AIMessage(content=text)]}

    async def explain_failure(self, state: ProgrammingState) -> dict:
        content = self._render_prompt(
            self._prompts["explain_failure"],
            attempts=state.get("retry_count", 0) + 1,
            code=state["code"],
            stderr=state["stderr"],
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {**FinalAnswerOutput(final_answer=text).model_dump(), "messages": [AIMessage(content=text)]}

    def route_after_execute(self, state: ProgrammingState) -> ProgrammingNode:
        if state.get("exit_code", 1) == 0:
            return ProgrammingNode.EXPLAIN
        if state.get("retry_count", 0) < state.get("max_retries", self.max_retries):
            return ProgrammingNode.REVIEW
        return ProgrammingNode.EXPLAIN_FAILURE

    def _build(self, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = StateGraph(ProgrammingState)

        graph.add_node(ProgrammingNode.PLAN, self.plan)
        graph.add_node(ProgrammingNode.WRITE_CODE, self.write_code)
        graph.add_node(ProgrammingNode.EXECUTE, self.execute)
        graph.add_node(ProgrammingNode.REVIEW, self.review)
        graph.add_node(ProgrammingNode.EXPLAIN, self.explain)
        graph.add_node(ProgrammingNode.EXPLAIN_FAILURE, self.explain_failure)

        graph.set_entry_point(ProgrammingNode.PLAN)
        graph.add_edge(ProgrammingNode.PLAN, ProgrammingNode.WRITE_CODE)
        graph.add_edge(ProgrammingNode.WRITE_CODE, ProgrammingNode.EXECUTE)
        graph.add_conditional_edges(
            ProgrammingNode.EXECUTE,
            self.route_after_execute,
            {
                ProgrammingNode.EXPLAIN: ProgrammingNode.EXPLAIN,
                ProgrammingNode.REVIEW: ProgrammingNode.REVIEW,
                ProgrammingNode.EXPLAIN_FAILURE: ProgrammingNode.EXPLAIN_FAILURE,
            },
        )
        graph.add_edge(ProgrammingNode.REVIEW, ProgrammingNode.WRITE_CODE)
        graph.add_edge(ProgrammingNode.EXPLAIN, END)
        graph.add_edge(ProgrammingNode.EXPLAIN_FAILURE, END)

        compiled = graph.compile(checkpointer=checkpointer)
        compiled.output_nodes = frozenset(
            {ProgrammingNode.WRITE_CODE, ProgrammingNode.EXPLAIN, ProgrammingNode.EXPLAIN_FAILURE}
        )
        return compiled

    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        return ProgrammingAgentGraph(llm, collection_names, prompt, agent_config)._build(checkpointer)
