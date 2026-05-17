import asyncio
import logging

from langchain_core.tools import StructuredTool

from rag.src.db.vector_store import VectorStore

logger = logging.getLogger(__name__)


def make_vector_search_tool(
    collection_name: str,
    k: int = 4,
    score_threshold: float = 0.5,
) -> StructuredTool:
    async def _search(query: str) -> str:
        docs_with_score = await asyncio.to_thread(
            VectorStore(collection_name=collection_name).search_with_score,
            query,
            k,
        )
        results = [doc.page_content for doc, score in docs_with_score if score > score_threshold]
        if results:
            logger.debug("Retrieved %d chunks from '%s'", len(results), collection_name)
        return "\n\n---\n\n".join(results) if results else "No relevant documents found."

    return StructuredTool.from_function(
        coroutine=_search,
        name=f"search_{collection_name}",
        description=f"Search the '{collection_name}' knowledge base for relevant documents.",
    )
