import asyncio
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from rag.src.agent.base import BaseAgentGraph
from rag.src.agent.enums import ResearcherNode
from rag.src.agent.schemes import (
    CiteSourcesOutput,
    FetchPagesOutput,
    PlanQueriesOutput,
    SynthesizeOutput,
    WebSearchOutput,
)
from rag.src.agent.states import ResearcherState
from rag.src.agent.tools.vector_search import make_vector_search_tool
from rag.src.agent.tools.web_search import _fetch_page, _tavily_search
from rag.src.agent.types import AgentType
from rag.src.common import settings

logger = logging.getLogger(__name__)


class ResearcherAgentGraph(BaseAgentGraph):
    def __init__(
        self,
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        agent_config: dict,
    ) -> None:
        self.llm = llm
        self.prompt = prompt
        self.tavily_api_key: str = settings.agent.TAVILY_API_KEY
        self.max_search_results: int = agent_config.get("max_search_results", 5)
        self.max_fetch_urls: int = agent_config.get("max_fetch_urls", 3)
        self.max_page_fetch_chars: int = agent_config.get("max_page_fetch_chars", 8000)
        self.max_search_rounds: int = agent_config.get("max_search_rounds", 2)
        self.search_tools: list[StructuredTool] = [make_vector_search_tool(name) for name in collection_names]
        self._prompts = self.get_all_nodes(AgentType.RESEARCHER)

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

    async def plan_queries(self, state: ResearcherState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )
        context = await self._gather_context(str(user_question))
        search_round = state.get("search_round", 0)

        hint = ""
        if search_round > 0:
            prior = state.get("search_queries", [])
            hint = (
                f"\n\nThis is research round {search_round + 1}. "
                f"Prior queries used: {prior}. "
                f"Generate refined or complementary queries to fill remaining gaps."
            )

        context_section = f"\n\nLocal knowledge base context:\n{context}" if context else ""
        content = self._render_prompt(
            self._prompts["plan_queries"],
            user_question=user_question,
            hint=hint,
            context_section=context_section,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        queries = [line.strip() for line in text.splitlines() if line.strip()][:3]

        return PlanQueriesOutput(
            search_queries=queries,
            local_context=context,
            search_round=search_round,
            max_search_rounds=self.max_search_rounds,
        ).model_dump()

    async def web_search(self, state: ResearcherState) -> dict:
        seen_urls: set[str] = {r["url"] for r in state.get("search_results", [])}
        new_results: list[dict] = []

        for query in state.get("search_queries", []):
            results = await _tavily_search(query, self.tavily_api_key, self.max_search_results)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    new_results.append(r)

        all_results = state.get("search_results", []) + new_results
        return WebSearchOutput(
            search_results=sorted(all_results, key=lambda x: x["score"], reverse=True),
        ).model_dump()

    async def fetch_pages(self, state: ResearcherState) -> dict:
        top_urls = [r["url"] for r in state.get("search_results", []) if r.get("url")]
        top_urls = top_urls[: self.max_fetch_urls]

        contents = await asyncio.gather(*[_fetch_page(url, self.max_page_fetch_chars) for url in top_urls])
        return FetchPagesOutput(
            fetched_pages=[{"url": url, "content": content} for url, content in zip(top_urls, contents, strict=False)],
        ).model_dump()

    async def synthesize(self, state: ResearcherState) -> dict:
        user_question = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            "",
        )

        web_content = "\n\n---\n\n".join(
            f"Source: {p['url']}\n{p['content'][:2000]}" for p in state.get("fetched_pages", [])
        )
        snippets = "\n\n".join(
            f"[{r['title']}]({r['url']}): {r['snippet']}" for r in state.get("search_results", [])[:5]
        )

        context_sections = ""
        if state.get("local_context"):
            context_sections += f"Local knowledge base:\n{state['local_context']}\n\n"
        if snippets:
            context_sections += f"Web search snippets:\n{snippets}\n\n"
        if web_content:
            context_sections += f"Full page content:\n{web_content}\n\n"
        content = self._render_prompt(
            self._prompts["synthesize"],
            user_question=user_question,
            context_sections=context_sections,
        )

        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        needs_more = "NEEDS_MORE_INFO" in text
        draft = text.replace("NEEDS_MORE_INFO", "").strip()

        return SynthesizeOutput(
            draft_answer=draft,
            needs_more_info=needs_more,
            search_round=state.get("search_round", 0) + 1,
        ).model_dump()

    async def cite_sources(self, state: ResearcherState) -> dict:
        sources = [r["url"] for r in state.get("search_results", []) if r.get("url")]
        sources_text = "\n".join(f"- {url}" for url in sources[:10])

        content = self._render_prompt(
            self._prompts["cite_sources"],
            draft_answer=state["draft_answer"],
            sources_text=sources_text,
        )
        response = await self.llm.ainvoke(
            [self._system_message(self.prompt, state.get("language")), HumanMessage(content=content)]
        )
        text = self._response_text(response.content)
        return {
            **CiteSourcesOutput(final_answer=text, sources=sources).model_dump(),
            "messages": [AIMessage(content=text)],
        }

    def route_after_synthesize(self, state: ResearcherState) -> ResearcherNode:
        if state.get("needs_more_info") and state.get("search_round", 0) < state.get(
            "max_search_rounds", self.max_search_rounds
        ):
            return ResearcherNode.PLAN_QUERIES
        return ResearcherNode.CITE_SOURCES

    def _build(self, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = StateGraph(ResearcherState)

        graph.add_node(ResearcherNode.PLAN_QUERIES, self.plan_queries)
        graph.add_node(ResearcherNode.WEB_SEARCH, self.web_search)
        graph.add_node(ResearcherNode.FETCH_PAGES, self.fetch_pages)
        graph.add_node(ResearcherNode.SYNTHESIZE, self.synthesize)
        graph.add_node(ResearcherNode.CITE_SOURCES, self.cite_sources)

        graph.set_entry_point(ResearcherNode.PLAN_QUERIES)
        graph.add_edge(ResearcherNode.PLAN_QUERIES, ResearcherNode.WEB_SEARCH)
        graph.add_edge(ResearcherNode.WEB_SEARCH, ResearcherNode.FETCH_PAGES)
        graph.add_edge(ResearcherNode.FETCH_PAGES, ResearcherNode.SYNTHESIZE)
        graph.add_conditional_edges(
            ResearcherNode.SYNTHESIZE,
            self.route_after_synthesize,
            {
                ResearcherNode.PLAN_QUERIES: ResearcherNode.PLAN_QUERIES,
                ResearcherNode.CITE_SOURCES: ResearcherNode.CITE_SOURCES,
            },
        )
        graph.add_edge(ResearcherNode.CITE_SOURCES, END)

        compiled = graph.compile(checkpointer=checkpointer)
        compiled.output_nodes = frozenset({ResearcherNode.CITE_SOURCES})
        return compiled

    @staticmethod
    def create_agent_graph(
        llm: BaseChatModel,
        collection_names: list[str],
        prompt: str,
        checkpointer: BaseCheckpointSaver,
        agent_config: dict | None = None,
    ) -> CompiledStateGraph:
        return ResearcherAgentGraph(llm, collection_names, prompt, agent_config)._build(checkpointer)
