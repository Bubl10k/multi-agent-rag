from pydantic import BaseModel


class PlanQueriesOutput(BaseModel):
    search_queries: list[str]
    local_context: str
    search_round: int
    max_search_rounds: int


class WebSearchOutput(BaseModel):
    search_results: list[dict]


class FetchPagesOutput(BaseModel):
    fetched_pages: list[dict]


class SynthesizeOutput(BaseModel):
    draft_answer: str
    needs_more_info: bool
    search_round: int


class CiteSourcesOutput(BaseModel):
    final_answer: str
    sources: list[str]
