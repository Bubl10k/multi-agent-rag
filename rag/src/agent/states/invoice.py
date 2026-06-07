from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict


class InvoiceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    client_info: dict
    line_items: list[dict]
    invoice_meta: dict
    tax_rate: float
    subtotal: float
    tax_amount: float
    total: float
    is_complete: bool
    is_valid: bool
    missing_fields: list[str]
    validation_errors: list[str]
    retry_count: int
    max_retries: int
    invoice_file_url: str | None
    invoice_file_name: str | None
    language: NotRequired[str]
