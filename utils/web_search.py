"""
utils/web_search.py — Web search utility for the Category Wiki Agent.

Uses the Parallel AI API (parallel-web package) to perform live web searches
when the LLM signals it needs more information to enrich the wiki.

Usage:
    from utils.web_search import web_search, format_results_for_llm

The LLM signals a search need using the tag in its output:
    [WEB_SEARCH] your query here [/WEB_SEARCH]

The result is formatted back and injected into the next LLM call.
"""
import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from parallel import Parallel

# Load .env from project root (same folder as this util)
load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)


def web_search(query: str, additional_queries: list = None, max_chars: int = 5000) -> dict:
    """
    Perform a web search using Parallel AI.

    Args:
        query: Primary search query.
        additional_queries: Optional extra queries to broaden the search.
        max_chars: Max characters per result excerpt.

    Returns:
        dict with keys: query, results (list of title/url/excerpt), count, error (if any)
    """
    try:
        api_key = os.environ.get("PARALLEL_API_KEY", "")
        if not api_key:
            return {"query": query, "results": [], "count": 0,
                    "error": "PARALLEL_API_KEY not set in environment"}

        client = Parallel(api_key=api_key)

        search_queries = [query]
        if additional_queries:
            search_queries += additional_queries

        logger.info("🔎  WEB SEARCH  │ query=%s", query)

        search = client.beta.search(
            objective=query,
            search_queries=search_queries,
            mode="fast",
            excerpts={"max_chars_per_result": max_chars},
        )

        results = []
        for r in search.results:
            results.append({
                "title":   getattr(r, "title",   ""),
                "url":     getattr(r, "url",     ""),
                "excerpt": getattr(r, "excerpt", str(r)),
            })

        logger.info("🔎  WEB SEARCH  │ found %d results", len(results))
        return {"query": query, "results": results, "count": len(results)}

    except Exception as e:
        logger.warning("🔎  WEB SEARCH  │ FAILED: %s", str(e))
        return {"query": query, "results": [], "count": 0, "error": str(e)}


def format_results_for_llm(search_result: dict) -> str:
    """
    Format web search results into a clean text block for LLM injection.
    """
    if search_result.get("error") or not search_result.get("results"):
        return f"[WEB SEARCH FAILED: {search_result.get('error', 'No results found')}]"

    lines = [f"--- WEB SEARCH RESULTS for: '{search_result['query']}' ---"]
    for i, r in enumerate(search_result["results"], 1):
        lines.append(f"\n[{i}] {r['title']}")
        lines.append(f"URL: {r['url']}")
        lines.append(f"{r['excerpt']}")
    lines.append("\n--- END WEB SEARCH RESULTS ---")
    return "\n".join(lines)


def extract_search_queries(text: str) -> list[dict]:
    """
    Scan LLM output for <WEB_SEARCH>...</WEB_SEARCH> XML tags.
    """
    import xml.etree.ElementTree as ET
    queries = []
    
    xml_matches = re.findall(r'<WEB_SEARCH>(.*?)</WEB_SEARCH>', text, re.DOTALL | re.IGNORECASE)
    for match in xml_matches:
        try:
            root = ET.fromstring(f"<root>{match}</root>")
            rationale = (root.findtext("rationale") or "Need more data for wiki enrichment").strip()
            query = (root.findtext("query") or "").strip()
            if query:
                queries.append({'rationale': rationale, 'query': query})
        except Exception:
            lines = match.strip().split('\n')
            q = lines[-1].replace("<query>", "").replace("</query>", "").strip()
            if q:
                queries.append({'rationale': 'Parse error recovered', 'query': q})

    old_matches = re.findall(r'\[WEB_SEARCH\](.*?)\[/WEB_SEARCH\]', text, re.DOTALL | re.IGNORECASE)
    for m in old_matches:
        if m.strip():
            queries.append({'rationale': 'Legacy query tag', 'query': m.strip()})
            
    return queries

def extract_search_reasoning(text: str) -> dict:
    """Extract LLM post-search reasoning from augmented prompt response."""
    import xml.etree.ElementTree as ET
    match = re.search(r'<WEB_SEARCH_REASONING>(.*?)</WEB_SEARCH_REASONING>', text, re.DOTALL)
    if not match:
        return {}
    try:
        root = ET.fromstring(f"<root>{match.group(1)}</root>")
        inferred = (root.findtext("inferred") or "").strip()
        updates = (root.findtext("updates") or "").strip()
        return {"inferred": inferred, "updates": updates}
    except Exception:
        return {"inferred": "Parse error", "updates": "Parse error"}


if __name__ == "__main__":
    result = web_search("Industrial product category specifications and pricing India B2B")
    print(format_results_for_llm(result))
