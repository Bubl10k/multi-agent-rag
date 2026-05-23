# Multi-Agent System Design

## Overview

This document describes the architecture for extending the RAG system with specialized graph agents. Every agent is implemented as a custom LangGraph `StateGraph` with explicit nodes and conditional routing. Every agent inherits from `BaseAgentGraph`, which provides vector search over configured collections as its foundational tool — available to any node that needs it.

---

## Current Architecture

```
BaseAgentGraph
  └── create_react_agent(llm, tools=[vector_search_*], prompt, checkpointer)
```

The existing `BaseAgentGraph.create_agent_graph` wraps LangGraph's `create_react_agent`. All state is checkpointed to PostgreSQL per `thread_id` (= conversation UUID).

---

## Target Architecture

### Class Hierarchy

```
BaseAgentGraph                        ← vector search tools, graph visualization helpers
├── ProgrammingAgentGraph             ← plan → write → execute → review/fix loop → explain
├── MathAgentGraph                    ← parse → solve → verify loop → explain
├── ResearcherAgentGraph              ← plan_queries → search → fetch → synthesize → cite
└── InvoiceAgentGraph                 ← extract → validate/fix loop → generate → format
```

### Agent Type Enum (new)

```python
# rag/src/agent/types.py
from enum import StrEnum

class AgentType(StrEnum):
    GENERAL      = "general"
    PROGRAMMING  = "programming"
    MATH         = "math"
    RESEARCHER   = "researcher"
    INVOICE      = "invoice"
```

### Factory (new)

```python
# rag/src/agent/factory.py
class AgentGraphFactory:
    _registry: dict[AgentType, type[BaseAgentGraph]] = {
        AgentType.GENERAL:       BaseAgentGraph,
        AgentType.PROGRAMMING:   ProgrammingAgentGraph,
        AgentType.MATH:          MathAgentGraph,
        AgentType.RESEARCHER:    ResearcherAgentGraph,
        AgentType.INVOICE:       InvoiceAgentGraph,
    }

    @classmethod
    def create(
        cls,
        agent_type: AgentType,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict,
    ) -> CompiledStateGraph:
        klass = cls._registry[agent_type]
        return klass.create_agent_graph(
            llm, collection_names, prompt, checkpointer, agent_config
        )
```

---

## Database Changes

### Agent Model — add `agent_type` column

```python
# rag/src/models/agent.py
agent_type: Mapped[str] = mapped_column(String, default=AgentType.GENERAL)
```

The existing `tool_calls: JSONB` column is repurposed to hold agent-specific configuration (sandbox settings, search API references, retry limits, etc.) — renamed to `agent_config` in schemas.

### Schema Changes

```python
# rag/src/api/schemas/agent.py
class AgentCreate(BaseModel):
    name: str
    prompt: str
    llm_id: uuid.UUID
    agent_type: AgentType = AgentType.GENERAL
    agent_config: dict = {}
    collection_ids: list[uuid.UUID] = []
    is_active: bool = True
```

---

## File Layout

```
rag/src/agent/
├── __init__.py
├── base.py               (existing — unchanged)
├── events.py             (existing — unchanged)
├── types.py              (new — AgentType enum)
├── factory.py            (new — AgentGraphFactory)
├── programming.py        (new)
├── math.py               (new)
├── researcher.py         (new)
├── invoice.py            (new)
└── tools/
    ├── __init__.py
    ├── vector_search.py  (moved from tool_calls.py)
    ├── code_execution.py (new — shared sandbox executor)
    ├── web_search.py     (new)
    ├── math_tools.py     (new)
    └── invoice_tools.py  (new)
```

---

## Agent Designs

---

### 1. General Agent (existing, unchanged)

**Graph:** `create_react_agent` (ReAct loop — kept as-is)

**Tools:** `search_{collection}` per configured collection

**Use case:** General Q&A grounded in uploaded documents. No changes required.

---

### 2. Programming Agent

**Graph topology:**

```
START
  │
  ▼
plan              Analyze the request, outline approach, search vector store for context
  │
  ▼
write_code        Generate code based on plan
  │
  ▼
execute           Run code in sandbox, capture stdout/stderr/exit_code
  │
  ├─(success)───► explain         Format final answer with code + output
  │                    │
  │                    ▼
  │                   END
  │
  ├─(error, retries_left)──► review     Analyze error, suggest fix
  │                               │
  │                               ▼
  │                           write_code  (loop)
  │
  └─(error, max_retries)──► explain_failure   Explain what was tried and why it failed
                                  │
                                  ▼
                                 END
```

**State:**

```python
class ProgrammingState(TypedDict):
    messages:      Annotated[list[BaseMessage], add_messages]
    plan:          str
    code:          str
    stdout:        str
    stderr:        str
    exit_code:     int
    retry_count:   int
    max_retries:   int
    final_answer:  str
```

**Nodes:**

| Node | Responsibility |
|------|---------------|
| `plan` | Calls LLM to outline approach; calls `search_{collection}` for relevant code/docs |
| `write_code` | Calls LLM to produce Python code given plan + previous error (if retry) |
| `execute` | Runs code via sandboxed executor; populates `stdout`, `stderr`, `exit_code` |
| `review` | Calls LLM to diagnose error; updates state with corrected plan/hint for next write |
| `explain` | Calls LLM to format the final answer: code + output + explanation |
| `explain_failure` | Calls LLM to summarize what was attempted and why it failed |

**Routing conditions:**

```python
def route_after_execute(state: ProgrammingState) -> str:
    if state["exit_code"] == 0:
        return "explain"
    if state["retry_count"] < state["max_retries"]:
        return "review"
    return "explain_failure"

def route_after_review(state: ProgrammingState) -> str:
    return "write_code"
```

**Tools available to nodes:**
- `plan` node: `search_{collection}` (vector search)
- `execute` node: sandboxed Python executor (from `tools/code_execution.py`)

**`agent_config` fields:**
```json
{
  "execution_timeout_seconds": 10,
  "max_retries": 3,
  "allowed_modules": ["math", "json", "re", "itertools", "datetime"]
}
```

---

### 3. Math Agent

**Graph topology:**

```
START
  │
  ▼
parse_problem     Extract knowns, unknowns, problem type, constraints
  │
  ├─(ambiguous)──► clarify        Ask the LLM to request clarification from the user
  │                    │
  │                    ▼
  │               parse_problem   (loop until unambiguous)
  │
  ▼
solve             Apply SymPy symbolic computation + LLM reasoning;
  │               calls search_{collection} for formulas/theorems
  │
  ▼
verify            Numerically verify answer; check units; run SymPy simplify
  │
  ├─(incorrect, retries_left)──► solve      (loop with corrective hint)
  │
  ├─(incorrect, max_retries)───► explain_failure
  │                                   │
  │                                   ▼
  │                                  END
  │
  └─(correct)──► explain         Format step-by-step human-readable solution
                      │
                      ▼
                     END
```

**State:**

```python
class MathState(TypedDict):
    messages:             Annotated[list[BaseMessage], add_messages]
    problem_type:         str           # "algebra" | "calculus" | "statistics" | "geometry" | …
    parsed_components:    dict          # {"knowns": […], "unknowns": […], "constraints": […]}
    is_ambiguous:         bool
    solution_expr:        str           # SymPy expression string
    solution_numeric:     float | None
    verification_passed:  bool
    retry_count:          int
    max_retries:          int
    explanation:          str
```

**Nodes:**

| Node | Responsibility |
|------|---------------|
| `parse_problem` | Calls LLM to extract structured components; sets `is_ambiguous` |
| `clarify` | Emits a clarification question to the user; waits for next message via checkpointer |
| `solve` | Calls `sympy_compute` tool + LLM; writes `solution_expr` and `solution_numeric` |
| `verify` | Numerically evaluates `solution_expr` against constraints; sets `verification_passed` |
| `explain` | Calls LLM to produce a step-by-step explanation using `parsed_components` + `solution_expr` |
| `explain_failure` | Summarizes what was attempted and why verification repeatedly failed |

**Routing conditions:**

```python
def route_after_parse(state: MathState) -> str:
    return "clarify" if state["is_ambiguous"] else "solve"

def route_after_verify(state: MathState) -> str:
    if state["verification_passed"]:
        return "explain"
    if state["retry_count"] < state["max_retries"]:
        return "solve"
    return "explain_failure"
```

**Tools available to nodes:**
- `solve` node: `sympy_compute` (from `tools/math_tools.py`), `search_{collection}`
- `verify` node: `sympy_compute`

**`agent_config` fields:**
```json
{
  "max_retries": 3,
  "use_sympy": true,
  "sympy_timeout_seconds": 5
}
```

---

### 4. Researcher Agent

**Graph topology:**

```
START
  │
  ▼
plan_queries      Decompose user question into N focused search queries;
  │               calls search_{collection} for local context first
  │
  ▼
web_search        Executes each query via Tavily; collects ranked snippets + URLs
  │
  ▼
fetch_pages       Fetches full content for top-K URLs; strips HTML to plain text
  │
  ▼
synthesize        Calls LLM to combine local vector results + web content into a draft answer
  │
  ├─(needs_more_info)──► plan_queries    (loop with refined queries, up to max_search_rounds)
  │
  ▼
cite_sources      Formats inline citations; lists sources with URLs
  │
  ▼
END
```

**State:**

```python
class ResearcherState(TypedDict):
    messages:          Annotated[list[BaseMessage], add_messages]
    search_queries:    list[str]
    search_results:    list[dict]       # [{"url": …, "snippet": …, "score": …}]
    fetched_pages:     list[dict]       # [{"url": …, "content": …}]
    local_context:     str              # vector store results
    draft_answer:      str
    needs_more_info:   bool
    search_round:      int
    max_search_rounds: int
    final_answer:      str
    sources:           list[str]        # cited URLs
```

**Nodes:**

| Node | Responsibility |
|------|---------------|
| `plan_queries` | Calls LLM to generate focused sub-queries; calls `search_{collection}` for local context |
| `web_search` | Calls `web_search` tool for each query; aggregates and deduplicates results |
| `fetch_pages` | Calls `fetch_page` tool for top-K URLs; stores plain text content |
| `synthesize` | Calls LLM to synthesize local + web content into a draft; sets `needs_more_info` |
| `cite_sources` | Calls LLM to format the draft with inline citations and a sources list |

**Routing conditions:**

```python
def route_after_synthesize(state: ResearcherState) -> str:
    if state["needs_more_info"] and state["search_round"] < state["max_search_rounds"]:
        return "plan_queries"
    return "cite_sources"
```

**Tools available to nodes:**
- `plan_queries` node: `search_{collection}`
- `web_search` node: `web_search` (Tavily, from `tools/web_search.py`)
- `fetch_pages` node: `fetch_page` (HTTP fetch + HTML strip, from `tools/web_search.py`)

**`agent_config` fields:**
```json
{
  "search_provider": "tavily",
  "tavily_api_key_env": "TAVILY_API_KEY",
  "max_search_results": 5,
  "max_fetch_urls": 3,
  "max_page_fetch_chars": 8000,
  "max_search_rounds": 2
}
```

---

### 5. Invoice Generator Agent

**Graph topology:**

```
START
  │
  ▼
extract_details   LLM extracts structured invoice data from user message
  │               (client info, line items, dates, currency);
  │               calls search_{collection} for saved client/product templates
  │
  ├─(incomplete)──► request_info    Emits questions for missing required fields;
  │                      │          waits for user reply via checkpointer
  │                      └────────► extract_details  (loop until complete)
  │
  ▼
validate          Checks line item math, required fields, date logic;
  │               calculates subtotal / tax / total
  │
  ├─(invalid, retries_left)──► fix_items    LLM corrects validation errors;
  │                                 │        increments retry_count
  │                                 └──────► validate  (loop)
  │
  ▼
generate_invoice  LLM assembles the full structured invoice document
  │               (invoice number, payment terms, itemized table, totals)
  │
  ▼
format_output     Calls search_{collection} for company branding / payment terms;
  │               renders invoice to a PDF file via `generate_pdf` tool;
  │               writes file to object storage; stores download URL in state
  ▼
END
```

**State:**

```python
class InvoiceState(TypedDict):
    messages:         Annotated[list[BaseMessage], add_messages]
    client_info:      dict          # name, address, email, tax_id
    line_items:       list[dict]    # [{"description": …, "qty": …, "unit_price": …, "total": …}]
    invoice_meta:     dict          # invoice_number, issue_date, due_date, currency
    tax_rate:         float
    subtotal:         float
    tax_amount:       float
    total:            float
    is_complete:      bool          # all required fields present
    is_valid:         bool          # validation passed
    retry_count:      int
    max_retries:      int
    invoice_file_url: str | None    # object-storage download URL for generated PDF
    invoice_file_name: str | None   # e.g. "INV-0042_Acme_Corp.pdf"
```

**Nodes:**

| Node | Responsibility |
|------|---------------|
| `extract_details` | Calls LLM to parse client info, line items, and meta from user message; calls `search_{collection}` for saved templates; sets `is_complete` |
| `request_info` | Emits targeted questions for each missing required field; suspends via checkpointer until user replies |
| `validate` | Verifies line item arithmetic, required fields, and date ordering; computes `subtotal`, `tax_amount`, `total`; sets `is_valid` |
| `fix_items` | Calls LLM to correct invalid entries (negative quantities, missing descriptions, etc.); increments `retry_count` |
| `generate_invoice` | Calls LLM to produce a complete, coherent invoice including invoice number, itemized table, and payment terms |
| `format_output` | Calls `search_{collection}` for company branding/terms; calls `generate_pdf` to render the invoice as a PDF file; calls `upload_file` to write it to object storage; stores the download URL and filename in state |

**Routing conditions:**

```python
def route_after_extract(state: InvoiceState) -> str:
    return "validate" if state["is_complete"] else "request_info"

def route_after_validate(state: InvoiceState) -> str:
    if state["is_valid"]:
        return "generate_invoice"
    if state["retry_count"] < state["max_retries"]:
        return "fix_items"
    return "generate_invoice"   # proceed best-effort after exhausting retries

def route_after_fix(state: InvoiceState) -> str:
    return "validate"
```

**Tools available to nodes:**
- `extract_details` node: `search_{collection}` (saved client/product templates)
- `validate` node: `calculate_totals` (from `tools/invoice_tools.py`)
- `format_output` node: `generate_pdf`, `upload_file` (from `tools/invoice_tools.py`), `search_{collection}`

**`agent_config` fields:**
```json
{
  "default_currency": "USD",
  "default_tax_rate": 0.0,
  "invoice_number_prefix": "INV-",
  "payment_terms_days": 30,
  "pdf_template": "default",
  "storage_bucket": "invoices",
  "file_url_expiry_seconds": 3600
}
```

---

## Streaming Integration

The `AgentStreamingService` already filters for `StreamEvent.CHAT_MODEL_STREAM` events, which works for any `StateGraph` topology — LangGraph emits the same event shape regardless of whether the graph was built with `create_react_agent` or a custom builder. No streaming changes are required beyond updating `build_graph` to use the factory:

```python
# rag/src/services/agent_streaming.py  (updated build_graph)
@staticmethod
async def build_graph(uow: UnitOfWork, agent_id: uuid.UUID) -> CompiledStateGraph:
    agent = await AgentStreamingService.load_agent(uow, agent_id)
    llm = AgentStreamingService._init_llm(agent.llm)
    await ensure_initialized()
    return AgentGraphFactory.create(
        agent_type=AgentType(agent.agent_type),
        llm=llm,
        collection_names=[c.name for c in agent.collections],
        prompt=agent.prompt,
        checkpointer=get_checkpointer(),
        agent_config=agent.tool_calls or {},
    )
```

Each agent's "output" node (`explain`, `cite_sources`, `interpret`, `format_output`) is the node that streams tokens to the user. Intermediate nodes (`plan`, `solve`, `web_search`, `run_code`) can optionally emit structured status events using `StreamEvent.TOOL_START` / `TOOL_END` for frontend progress indicators.

The `InvoiceAgent`'s `format_output` node does not stream text tokens — instead it emits a single `StreamEvent.TOOL_END` event carrying `{"file_url": "…", "file_name": "INV-0042_Acme_Corp.pdf"}` as its output payload. The frontend receives this event and renders a download button rather than a chat bubble.

---

## Implementation Order

| Step | Task | Notes |
|------|------|-------|
| 1 | Move `make_vector_search_tool` → `tools/vector_search.py` | Re-export from `tool_calls.py` for backwards compat |
| 2 | Add `AgentType` enum + DB migration | Add `agent_type` column, default `"general"` |
| 3 | Update schemas + `AgentService` | `agent_type` + `agent_config` in create/update/read |
| 4 | Implement `AgentGraphFactory` | Wire existing `BaseAgentGraph` as `GENERAL` |
| 5 | Implement `ResearcherAgentGraph` | Tavily integration + `fetch_page` tool |
| 6 | Implement `ProgrammingAgentGraph` + `tools/code_execution.py` | Security-critical; sandbox first |
| 7 | Implement `MathAgentGraph` + `tools/math_tools.py` | SymPy integration |
 | 8 | Implement `InvoiceAgentGraph` + `tools/invoice_tools.py` | `calculate_totals` + `render_invoice` utilities |
| 9 | Update `AgentStreamingService.build_graph` | Switch to factory |
| 10 | Frontend — agent type selector in agent creation UI | `AgentType` dropdown + config form |

---

## Security Considerations

- **Web fetch** (`ResearcherAgent`): Validate and sanitize all URLs before fetching. Block private/internal IP ranges (127.0.0.0/8, 10.0.0.0/8, 169.254.0.0/16, etc.) to prevent SSRF. Enforce character limits on fetched content.
- **SymPy evaluation** (`MathAgent`): Always wrap SymPy calls in a timeout (e.g., `concurrent.futures.ThreadPoolExecutor` with a deadline) to prevent DoS from expressions like `factorial(10**6)`.
- **Invoice amounts** (`InvoiceAgent`): Validate that all monetary values are non-negative numbers within a reasonable upper bound before arithmetic. Never pass raw user-supplied strings directly into arithmetic to prevent injection into template rendering.

---

## Open Questions

1. **Search API key storage**: Should `TAVILY_API_KEY` live in `.env` globally, or follow the LLM pattern (encrypted per-agent in DB)? Per-agent is more flexible for multi-tenant deployments.
2. **Custom state checkpoint schema**: Each agent uses a different `TypedDict` state. LangGraph checkpoints the full state as JSONB, so this works transparently — but schema migrations between agent versions need care.
3. **Invoice output storage**: Should generated invoices be persisted to the DB / object storage for later retrieval, or returned only as a streaming response? Persistence enables a history view in the frontend.
4. **Agent composition / supervisor**: Once all four agents are stable, a natural next step is a `SupervisorAgent` that routes incoming requests to the appropriate specialist agent (LangGraph multi-agent pattern with `Command` routing).
