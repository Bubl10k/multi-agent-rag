from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict


class ResearcherState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    search_queries: list[str]
    search_results: list[dict]
    fetched_pages: list[dict]
    local_context: str
    draft_answer: str
    needs_more_info: bool
    search_round: int
    max_search_rounds: int
    final_answer: str
    sources: list[str]
    language: NotRequired[str]
