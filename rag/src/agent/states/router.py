from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict


class RouterState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    selected_agent: str
    language: NotRequired[str]
