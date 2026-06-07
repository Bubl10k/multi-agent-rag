import asyncio
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import MathNode
from rag.src.agent.schemes import ExplainOutput, ParseProblemOutput, SolveOutput, VerifyOutput
from rag.src.agent.states import MathState
from rag.src.agent.tools.math_tools import sympy_compute
from rag.src.agent.tools.vector_search import make_vector_search_tool
from rag.src.agent.types import AgentType

logger = logging.getLogger(__name__)


class MathAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.prompt = prompt
        self.max_retries: int = agent_config.get("max_retries", 3)
        self.sympy_timeout: float = agent_config.get("sympy_timeout_seconds", 5.0)
        self.search_tools: list[StructuredTool] = [make_vector_search_tool(name) for name in collection_names]
        self._prompts = self.get_all_nodes(AgentType.MATH)

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

    async def parse_problem(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        content = self._render_prompt(
            self._prompts["parse_problem"],
            user_question=user_question,
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)

        problem_type = "other"
        knowns, unknowns, constraints = [], [], []
        is_ambiguous = False

        for line in text.splitlines():
            if line.startswith("PROBLEM_TYPE:"):
                problem_type = line.split(":", 1)[1].strip().lower()
            elif line.startswith("KNOWNS:"):
                knowns = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
            elif line.startswith("UNKNOWNS:"):
                unknowns = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
            elif line.startswith("CONSTRAINTS:"):
                constraints = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
            elif line.startswith("AMBIGUOUS:"):
                is_ambiguous = "yes" in line.lower()

        return ParseProblemOutput(
            problem_type=problem_type,
            parsed_components={"knowns": knowns, "unknowns": unknowns, "constraints": constraints},
            is_ambiguous=is_ambiguous,
            retry_count=0,
            max_retries=self.max_retries,
        ).model_dump()

    async def clarify(self, state: MathState) -> dict:
        components = state["parsed_components"]
        content = self._render_prompt(
            self._prompts["clarify"],
            knowns=components.get("knowns", []),
            unknowns=components.get("unknowns", []),
            constraints=components.get("constraints", []),
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {"messages": [AIMessage(content=text)]}

    async def solve(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        context = await self._gather_context(str(user_question))

        hint = ""
        if state.get("retry_count", 0) > 0 and state.get("solution_expr"):
            hint = (
                f"\n\nPrevious solution attempt '{state['solution_expr']}' failed verification. "
                f"Try a different approach or check for errors."
            )

        context_section = f"\n\nRelevant formulas/theorems:\n{context}" if context else ""
        content = self._render_prompt(
            self._prompts["solve"],
            user_question=user_question,
            problem_type=state.get("problem_type", "unknown"),
            parsed_components=state.get("parsed_components", {}),
            hint=hint,
            context_section=context_section,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        solution_text = self._response_text(response.content)

        sympy_expr = ""
        for line in solution_text.splitlines():
            if line.strip().startswith("SYMPY:"):
                sympy_expr = line.split("SYMPY:", 1)[1].strip()
                break

        solution_numeric = None
        if sympy_expr:
            result = await sympy_compute(sympy_expr, timeout=self.sympy_timeout)
            try:
                solution_numeric = float(result)
            except (ValueError, TypeError):
                pass

        return SolveOutput(
            solution_expr=sympy_expr or solution_text,
            solution_numeric=solution_numeric,
        ).model_dump()

    async def verify(self, state: MathState) -> dict:
        content = self._render_prompt(
            self._prompts["verify"],
            parsed_components=state.get("parsed_components", {}),
            solution_expr=state.get("solution_expr", ""),
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        verification_passed = text.strip().upper().startswith("CORRECT")

        return VerifyOutput(
            verification_passed=verification_passed,
            retry_count=state.get("retry_count", 0) + (0 if verification_passed else 1),
        ).model_dump()

    async def explain(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        content = self._render_prompt(
            self._prompts["explain"],
            user_question=user_question,
            solution_expr=state.get("solution_expr", ""),
            parsed_components=state.get("parsed_components", {}),
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {**ExplainOutput(explanation=text).model_dump(), "messages": [AIMessage(content=text)]}

    async def explain_failure(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        content = self._render_prompt(
            self._prompts["explain_failure"],
            retry_count=state.get("retry_count", 0),
            user_question=user_question,
            solution_expr=state.get("solution_expr", "none"),
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {**ExplainOutput(explanation=text).model_dump(), "messages": [AIMessage(content=text)]}

    def route_after_parse(self, state: MathState) -> MathNode:
        return MathNode.CLARIFY if state.get("is_ambiguous") else MathNode.SOLVE

    def route_after_verify(self, state: MathState) -> MathNode:
        if state.get("verification_passed"):
            return MathNode.EXPLAIN
        if state.get("retry_count", 0) < state.get("max_retries", self.max_retries):
            return MathNode.SOLVE
        return MathNode.EXPLAIN_FAILURE

    def _build(self, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = StateGraph(MathState)

        graph.add_node(MathNode.PARSE_PROBLEM, self.parse_problem)
        graph.add_node(MathNode.CLARIFY, self.clarify)
        graph.add_node(MathNode.SOLVE, self.solve)
        graph.add_node(MathNode.VERIFY, self.verify)
        graph.add_node(MathNode.EXPLAIN, self.explain)
        graph.add_node(MathNode.EXPLAIN_FAILURE, self.explain_failure)

        graph.set_entry_point(MathNode.PARSE_PROBLEM)
        graph.add_conditional_edges(
            MathNode.PARSE_PROBLEM,
            self.route_after_parse,
            {MathNode.CLARIFY: MathNode.CLARIFY, MathNode.SOLVE: MathNode.SOLVE},
        )
        graph.add_edge(MathNode.CLARIFY, END)
        graph.add_edge(MathNode.SOLVE, MathNode.VERIFY)
        graph.add_conditional_edges(
            MathNode.VERIFY,
            self.route_after_verify,
            {
                MathNode.EXPLAIN: MathNode.EXPLAIN,
                MathNode.SOLVE: MathNode.SOLVE,
                MathNode.EXPLAIN_FAILURE: MathNode.EXPLAIN_FAILURE,
            },
        )
        graph.add_edge(MathNode.EXPLAIN, END)
        graph.add_edge(MathNode.EXPLAIN_FAILURE, END)

        compiled = graph.compile(checkpointer=checkpointer)
        compiled.output_nodes = frozenset({MathNode.CLARIFY, MathNode.EXPLAIN, MathNode.EXPLAIN_FAILURE})
        return compiled

    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        return MathAgentGraph(llm, collection_names, prompt, agent_config)._build(checkpointer)
