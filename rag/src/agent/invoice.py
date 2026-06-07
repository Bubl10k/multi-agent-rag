import asyncio
import json
import logging
import re
import uuid
from datetime import date, timedelta
from urllib.parse import quote

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import InvoiceNode
from rag.src.agent.schemes import (
    ExtractDetailsOutput,
    FixItemsOutput,
    FormatInvoiceOutput,
    GenerateInvoiceOutput,
    ValidateOutput,
)
from rag.src.agent.states import InvoiceState
from rag.src.agent.tools.invoice_tools import calculate_totals, render_invoice_pdf, save_invoice_file
from rag.src.agent.tools.vector_search import make_vector_search_tool
from rag.src.agent.types import AgentType

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = [
    "client_info.name",
    "line_items (at least one with description and price)",
    "invoice_meta.issue_date",
]


class InvoiceAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.prompt = prompt
        self.default_currency: str = agent_config.get("default_currency", "USD")
        self.default_tax_rate: float = float(agent_config.get("default_tax_rate", 0.0))
        self.invoice_prefix: str = agent_config.get("invoice_number_prefix", "INV-")
        self.payment_terms_days: int = int(agent_config.get("payment_terms_days", 30))
        self.max_retries: int = int(agent_config.get("max_retries", 2))
        self.storage_dir: str = agent_config.get("storage_bucket", "/tmp/invoices")
        self.search_tools: list[StructuredTool] = [make_vector_search_tool(name) for name in collection_names]
        self._prompts = self.get_all_nodes(AgentType.INVOICE)

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
    def _extract_json(text: str) -> dict:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            text = match.group(1).strip()
        return json.loads(text)

    async def extract_details(self, state: InvoiceState) -> dict:
        user_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        conversation = "\n\n".join(f"User: {m.content}" for m in user_msgs[-6:])

        context = ""
        if user_msgs:
            context = await self._gather_context(str(user_msgs[-1].content))

        context_section = f"\n\nKnowledge base context (client/product templates):\n{context}" if context else ""
        content = self._render_prompt(
            self._prompts["extract_details"],
            conversation=conversation,
            default_currency=self.default_currency,
            default_tax_rate=self.default_tax_rate,
            context_section=context_section,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)

        try:
            data = self._extract_json(text)
        except Exception:
            logger.warning("Failed to parse extraction JSON: %s", text[:200])
            data = {}

        return ExtractDetailsOutput(
            client_info=data.get("client_info") or {},
            line_items=data.get("line_items") or [],
            invoice_meta=data.get("invoice_meta") or {},
            tax_rate=float(data.get("tax_rate") or self.default_tax_rate),
            is_complete=bool(data.get("is_complete", False)),
            missing_fields=data.get("missing_fields") or _REQUIRED_FIELDS,
            retry_count=0,
            max_retries=self.max_retries,
            validation_errors=[],
        ).model_dump()

    async def request_info(self, state: InvoiceState) -> dict:
        missing = state.get("missing_fields") or _REQUIRED_FIELDS
        missing_bullets = "\n".join(f"- {f}" for f in missing)

        content = self._render_prompt(
            self._prompts["request_info"],
            missing_bullets=missing_bullets,
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {"messages": [AIMessage(content=text)]}

    async def validate(self, state: InvoiceState) -> dict:
        errors: list[str] = []
        client = state.get("client_info") or {}
        line_items = state.get("line_items") or []
        meta = state.get("invoice_meta") or {}

        if not client.get("name"):
            errors.append("client name is missing")

        if not line_items:
            errors.append("no line items provided")
        else:
            for i, item in enumerate(line_items, 1):
                if not item.get("description"):
                    errors.append(f"line item {i}: missing description")
                try:
                    if float(item.get("qty", 0)) < 0:
                        errors.append(f"line item {i}: negative quantity")
                except (TypeError, ValueError):
                    errors.append(f"line item {i}: invalid quantity")
                try:
                    if float(item.get("unit_price", 0)) < 0:
                        errors.append(f"line item {i}: negative unit price")
                except (TypeError, ValueError):
                    errors.append(f"line item {i}: invalid unit price")

        if not meta.get("issue_date"):
            errors.append("issue date is missing")
        else:
            try:
                issue = date.fromisoformat(meta["issue_date"])
                if meta.get("due_date"):
                    due = date.fromisoformat(meta["due_date"])
                    if due < issue:
                        errors.append("due date is before issue date")
            except ValueError:
                errors.append("issue_date must be YYYY-MM-DD format")

        totals = calculate_totals(line_items, state.get("tax_rate") or 0.0)
        return ValidateOutput(
            line_items=totals["line_items"],
            subtotal=totals["subtotal"],
            tax_amount=totals["tax_amount"],
            total=totals["total"],
            is_valid=len(errors) == 0,
            validation_errors=errors,
        ).model_dump()

    async def fix_items(self, state: InvoiceState) -> dict:
        errors = state.get("validation_errors") or []
        errors_text = "\n".join(f"- {e}" for e in errors)

        current = {
            "client_info": state.get("client_info") or {},
            "line_items": state.get("line_items") or [],
            "invoice_meta": state.get("invoice_meta") or {},
            "tax_rate": state.get("tax_rate") or 0.0,
        }

        content = self._render_prompt(
            self._prompts["fix_items"],
            errors_text=errors_text,
            current_json=json.dumps(current, indent=2),
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)

        try:
            data = self._extract_json(text)
        except Exception:
            logger.warning("Failed to parse fix_items JSON, retaining current state")
            data = {}

        return FixItemsOutput(
            client_info=data.get("client_info") or state.get("client_info") or {},
            line_items=data.get("line_items") or state.get("line_items") or [],
            invoice_meta=data.get("invoice_meta") or state.get("invoice_meta") or {},
            tax_rate=float(data.get("tax_rate") or state.get("tax_rate") or 0.0),
            retry_count=(state.get("retry_count") or 0) + 1,
        ).model_dump()

    async def generate_invoice(self, state: InvoiceState) -> dict:
        meta = dict(state.get("invoice_meta") or {})

        if not meta.get("invoice_number"):
            short_id = str(uuid.uuid4())[:8].upper()
            meta["invoice_number"] = f"{self.invoice_prefix}{short_id}"

        if not meta.get("issue_date"):
            meta["issue_date"] = date.today().isoformat()

        if not meta.get("due_date"):
            try:
                issue = date.fromisoformat(meta["issue_date"])
                meta["due_date"] = (issue + timedelta(days=self.payment_terms_days)).isoformat()
            except ValueError:
                meta["due_date"] = (date.today() + timedelta(days=self.payment_terms_days)).isoformat()

        if not meta.get("currency"):
            meta["currency"] = self.default_currency

        return GenerateInvoiceOutput(invoice_meta=meta).model_dump()

    async def format_output(self, state: InvoiceState) -> dict:
        branding = await self._gather_context("company payment terms invoice branding template")

        meta = state.get("invoice_meta") or {}
        client = state.get("client_info") or {}
        invoice_num = meta.get("invoice_number", "INV-UNKNOWN")
        client_name = client.get("name", "Client")
        safe_name = "".join(c if c.isalnum() else "_" for c in client_name)[:30]
        filename = f"{invoice_num}_{safe_name}.pdf"
        currency = meta.get("currency", self.default_currency)

        file_url = ""
        try:
            pdf_bytes = render_invoice_pdf(
                client_info=client,
                line_items=state.get("line_items") or [],
                invoice_meta=meta,
                subtotal=state.get("subtotal") or 0.0,
                tax_amount=state.get("tax_amount") or 0.0,
                total=state.get("total") or 0.0,
                currency=currency,
                branding=branding,
            )
            s3_key = save_invoice_file(pdf_bytes, filename, self.storage_dir)
            file_url = f"/api/invoices/download?key={quote(s3_key)}"
        except Exception as exc:
            logger.error("PDF generation failed: %s", exc)

        download_section = (
            f"Download link (format as markdown): [Download Invoice]({file_url})\n"
            if file_url
            else "Note: PDF rendering was not available.\n"
        )
        branding_section = f"\n\nCompany context: {branding[:400]}" if branding else ""
        content = self._render_prompt(
            self._prompts["format_output"],
            invoice_num=invoice_num,
            client_name=client_name,
            total=f"{state.get('total', 0.0):.2f}",
            currency=currency,
            due_date=meta.get("due_date", "N/A"),
            filename=filename,
            download_section=download_section,
            branding_section=branding_section,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {
            **FormatInvoiceOutput(
                invoice_file_url=file_url or None,
                invoice_file_name=filename,
            ).model_dump(),
            "messages": [AIMessage(content=text)],
        }

    def route_after_extract(self, state: InvoiceState) -> InvoiceNode:
        return InvoiceNode.VALIDATE if state.get("is_complete") else InvoiceNode.REQUEST_INFO

    def route_after_validate(self, state: InvoiceState) -> InvoiceNode:
        if state.get("is_valid"):
            return InvoiceNode.GENERATE_INVOICE
        if (state.get("retry_count") or 0) < (state.get("max_retries") or self.max_retries):
            return InvoiceNode.FIX_ITEMS
        return InvoiceNode.GENERATE_INVOICE

    def _build(self, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = StateGraph(InvoiceState)

        graph.add_node(InvoiceNode.EXTRACT_DETAILS, self.extract_details)
        graph.add_node(InvoiceNode.REQUEST_INFO, self.request_info)
        graph.add_node(InvoiceNode.VALIDATE, self.validate)
        graph.add_node(InvoiceNode.FIX_ITEMS, self.fix_items)
        graph.add_node(InvoiceNode.GENERATE_INVOICE, self.generate_invoice)
        graph.add_node(InvoiceNode.FORMAT_OUTPUT, self.format_output)

        graph.set_entry_point(InvoiceNode.EXTRACT_DETAILS)
        graph.add_conditional_edges(
            InvoiceNode.EXTRACT_DETAILS,
            self.route_after_extract,
            {
                InvoiceNode.VALIDATE: InvoiceNode.VALIDATE,
                InvoiceNode.REQUEST_INFO: InvoiceNode.REQUEST_INFO,
            },
        )
        graph.add_edge(InvoiceNode.REQUEST_INFO, END)
        graph.add_conditional_edges(
            InvoiceNode.VALIDATE,
            self.route_after_validate,
            {
                InvoiceNode.GENERATE_INVOICE: InvoiceNode.GENERATE_INVOICE,
                InvoiceNode.FIX_ITEMS: InvoiceNode.FIX_ITEMS,
            },
        )
        graph.add_edge(InvoiceNode.FIX_ITEMS, InvoiceNode.VALIDATE)
        graph.add_edge(InvoiceNode.GENERATE_INVOICE, InvoiceNode.FORMAT_OUTPUT)
        graph.add_edge(InvoiceNode.FORMAT_OUTPUT, END)

        compiled = graph.compile(checkpointer=checkpointer)
        compiled.output_nodes = frozenset({InvoiceNode.REQUEST_INFO, InvoiceNode.FORMAT_OUTPUT})
        return compiled

    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        return InvoiceAgentGraph(llm, collection_names, prompt, agent_config)._build(checkpointer)
