from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict


class ProgrammingState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    plan: str
    code: str
    stdout: str
    stderr: str
    exit_code: int
    retry_count: int
    max_retries: int
    final_answer: str
    language: NotRequired[str]
