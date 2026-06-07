from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict


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
    language: NotRequired[str]
