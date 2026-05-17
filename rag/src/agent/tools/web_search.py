import asyncio
import ipaddress
import logging
import re
import urllib.parse

import httpx
from langchain_core.tools import StructuredTool
from tavily import TavilyClient

logger = logging.getLogger(__name__)

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def _is_private_host(hostname: str) -> bool:
    try:
        addr = ipaddress.ip_address(hostname)
        return addr.is_loopback or addr.is_link_local or any(addr in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        return False


async def _fetch_page(url: str, max_chars: int = 8000) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return "Error: Only http/https URLs are allowed."
    if _is_private_host(parsed.hostname or ""):
        return "Error: Access to private/internal addresses is not allowed."

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "RAG-Researcher/1.0"})
            resp.raise_for_status()
            content = resp.text
    except Exception as exc:
        return f"Error fetching page: {exc}"

    content = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<[^>]+>", " ", content)
    content = re.sub(r"\s+", " ", content).strip()
    return content[:max_chars]


async def _tavily_search(query: str, api_key: str, max_results: int = 5) -> list[dict]:
    try:
        client = TavilyClient(api_key=api_key)
        results = await asyncio.to_thread(client.search, query, max_results=max_results)
        return [
            {
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "snippet": r.get("content", ""),
                "score": r.get("score", 0.0),
            }
            for r in results.get("results", [])
        ]
    except Exception as exc:
        logger.warning("Tavily search error: %s", exc)
        return []


def make_web_search_tool(api_key: str, max_results: int = 5) -> StructuredTool:
    async def _search(query: str) -> str:
        results = await _tavily_search(query, api_key=api_key, max_results=max_results)
        if not results:
            return "No results found."
        return "\n\n".join(f"[{r['title']}]({r['url']})\n{r['snippet']}" for r in results)

    return StructuredTool.from_function(
        coroutine=_search,
        name="web_search",
        description="Search the web for current information. Returns titles, URLs, and snippets.",
    )


def make_fetch_page_tool(max_chars: int = 8000) -> StructuredTool:
    async def _fetch(url: str) -> str:
        return await _fetch_page(url, max_chars=max_chars)

    return StructuredTool.from_function(
        coroutine=_fetch,
        name="fetch_page",
        description="Fetch the plain text content of a web page by its URL.",
    )
