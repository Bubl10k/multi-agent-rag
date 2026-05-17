from enum import StrEnum


class ProgrammingNode(StrEnum):
    PLAN = "plan"
    WRITE_CODE = "write_code"
    EXECUTE = "execute"
    REVIEW = "review"
    EXPLAIN = "explain"
    EXPLAIN_FAILURE = "explain_failure"


class MathNode(StrEnum):
    PARSE_PROBLEM = "parse_problem"
    CLARIFY = "clarify"
    SOLVE = "solve"
    VERIFY = "verify"
    EXPLAIN = "explain"
    EXPLAIN_FAILURE = "explain_failure"


class ResearcherNode(StrEnum):
    PLAN_QUERIES = "plan_queries"
    WEB_SEARCH = "web_search"
    FETCH_PAGES = "fetch_pages"
    SYNTHESIZE = "synthesize"
    CITE_SOURCES = "cite_sources"


class InvoiceNode(StrEnum):
    EXTRACT_DETAILS = "extract_details"
    REQUEST_INFO = "request_info"
    VALIDATE = "validate"
    FIX_ITEMS = "fix_items"
    GENERATE_INVOICE = "generate_invoice"
    FORMAT_OUTPUT = "format_output"
