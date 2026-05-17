import asyncio
import logging
from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import MathNode
from rag.src.agent.tools.math_tools import sympy_compute
from rag.src.agent.tools.vector_search import make_vector_search_tool

logger = logging.getLogger(__name__)


class MathState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    problem_type: str
    parsed_components: dict
    is_ambiguous: bool
    solution_expr: str
    solution_numeric: float | None
    verification_passed: bool
    retry_count: int
    max_retries: int
    explanation: str


class MathAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.system_msg = SystemMessage(content=prompt)
        self.max_retries: int = agent_config.get("max_retries", 3)
        self.sympy_timeout: float = agent_config.get("sympy_timeout_seconds", 5.0)
        self.search_tools: list[StructuredTool] = [make_vector_search_tool(name) for name in collection_names]

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
        content = (
            f"Analyze this math problem and extract its structure.\n\n"
            f"Problem: {user_question}\n\n"
            f"Respond in this exact format:\n"
            f"PROBLEM_TYPE: <algebra|calculus|statistics|geometry|arithmetic|other>\n"
            f"KNOWNS: <comma-separated list of known values/conditions>\n"
            f"UNKNOWNS: <comma-separated list of what needs to be found>\n"
            f"CONSTRAINTS: <comma-separated list of constraints>\n"
            f"AMBIGUOUS: <yes|no>\n"
            f"If AMBIGUOUS is yes, add a CLARIFICATION_NEEDED line explaining what is unclear."
        )
        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
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

        return {
            "problem_type": problem_type,
            "parsed_components": {"knowns": knowns, "unknowns": unknowns, "constraints": constraints},
            "is_ambiguous": is_ambiguous,
            "retry_count": 0,
            "max_retries": self.max_retries,
        }

    async def clarify(self, state: MathState) -> dict:
        content = (
            f"The math problem is ambiguous. Ask the user a specific question to resolve it.\n\n"
            f"Identified components:\n"
            f"  Knowns: {state['parsed_components'].get('knowns', [])}\n"
            f"  Unknowns: {state['parsed_components'].get('unknowns', [])}\n"
            f"  Constraints: {state['parsed_components'].get('constraints', [])}\n\n"
            f"Ask a single, clear question that will let you proceed with solving."
        )
        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
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

        content = (
            f"Solve this math problem step by step.\n\n"
            f"Problem: {user_question}\n"
            f"Type: {state.get('problem_type', 'unknown')}\n"
            f"Components: {state.get('parsed_components', {})}{hint}\n\n"
            f"If possible, provide a SymPy-evaluable expression for the final answer on a line starting with 'SYMPY: '."
        )
        if context:
            content += f"\n\nRelevant formulas/theorems:\n{context}"

        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
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

        return {
            "solution_expr": sympy_expr or solution_text,
            "solution_numeric": solution_numeric,
        }

    async def verify(self, state: MathState) -> dict:
        content = (
            f"Verify this mathematical solution.\n\n"
            f"Problem components: {state.get('parsed_components', {})}\n"
            f"Solution: {state.get('solution_expr', '')}\n\n"
            f"Check that the solution satisfies all constraints and is mathematically correct. "
            f"Start your response with exactly CORRECT or INCORRECT, then explain."
        )
        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
        text = self._response_text(response.content)
        verification_passed = text.strip().upper().startswith("CORRECT")

        return {
            "verification_passed": verification_passed,
            "retry_count": state.get("retry_count", 0) + (0 if verification_passed else 1),
        }

    async def explain(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        content = (
            f"Provide a clear, step-by-step explanation of the solution to this math problem.\n\n"
            f"Problem: {user_question}\n"
            f"Solution: {state.get('solution_expr', '')}\n"
            f"Components: {state.get('parsed_components', {})}"
        )
        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
        text = self._response_text(response.content)
        return {"explanation": text, "messages": [AIMessage(content=text)]}

    async def explain_failure(self, state: MathState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        content = (
            f"The math problem could not be solved and verified after {state.get('retry_count', 0)} attempt(s). "
            f"Summarize what was tried, why verification failed, and suggest next steps.\n\n"
            f"Problem: {user_question}\n"
            f"Last solution attempted: {state.get('solution_expr', 'none')}"
        )
        response = await self.llm.ainvoke([self.system_msg, HumanMessage(content=content)])
        text = self._response_text(response.content)
        return {"explanation": text, "messages": [AIMessage(content=text)]}

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
