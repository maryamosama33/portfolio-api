"""Finding job postings on the web with Tavily."""

import asyncio
import logging
from dataclasses import dataclass
from functools import lru_cache

from tavily import AsyncTavilyClient

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.services.portfolio_service import PortfolioSnapshot

logger = logging.getLogger(__name__)

MAX_QUERIES = 4
EXTRACT_BATCH_SIZE = 20  # Tavily's per-request URL limit


@dataclass
class SearchHit:
    url: str
    title: str
    snippet: str
    query: str


@lru_cache
def _client() -> AsyncTavilyClient:
    if not settings.tavily_api_key:
        raise AIServiceError("TAVILY_API_KEY is not configured")
    return AsyncTavilyClient(api_key=settings.tavily_api_key)


def build_search_queries(snapshot: PortfolioSnapshot, location: str | None = None) -> list[str]:
    """A few short, focused queries beat one long one: search engines match short intent better.

    e.g. ["Python FastAPI developer job Egypt", "Docker MongoDB developer job Egypt",
          "Backend Intern Python job Egypt"]
    """
    location = settings.job_search_location if location is None else location
    skills = snapshot.top_skills(6)
    if not skills:
        return []

    candidates = [
        f"{' '.join(skills[i:i + 2])} developer job" for i in range(0, len(skills), 2)
    ]
    if snapshot.experiences:
        latest = max(snapshot.experiences, key=lambda e: e.created_at)
        candidates.insert(1, f"{latest.title} {skills[0]} job")

    queries: list[str] = []
    for query in candidates:
        query = " ".join(f"{query} {location}".split())
        if query not in queries:
            queries.append(query)
    return queries[:MAX_QUERIES]


async def _search_one(query: str) -> list[SearchHit]:
    try:
        response = await _client().search(
            query=query,
            max_results=settings.job_search_results_per_query,
            include_domains=settings.job_search_domain_list or None,
        )
    except AIServiceError:
        raise
    except Exception:
        logger.warning("Tavily search failed for %r", query, exc_info=True)
        return []
    return [
        SearchHit(url=r["url"], title=r.get("title", ""), snippet=r.get("content", ""), query=query)
        for r in response.get("results", [])
        if r.get("url")
    ]


async def search_jobs(queries: list[str]) -> list[SearchHit]:
    """Run all queries concurrently and merge results, dropping duplicate URLs."""
    results = await asyncio.gather(*(_search_one(q) for q in queries))
    unique: dict[str, SearchHit] = {}
    for hits in results:
        for hit in hits:
            unique.setdefault(hit.url, hit)
    return list(unique.values())


async def extract_full_text(urls: list[str]) -> dict[str, str]:
    """Fetch the full page text for each URL. Missing URLs failed to extract."""
    texts: dict[str, str] = {}
    for start in range(0, len(urls), EXTRACT_BATCH_SIZE):
        batch = urls[start:start + EXTRACT_BATCH_SIZE]
        try:
            response = await _client().extract(urls=batch, format="text")
        except AIServiceError:
            raise
        except Exception:
            logger.warning("Tavily extract failed for %d URLs", len(batch), exc_info=True)
            continue
        for result in response.get("results", []):
            if result.get("raw_content"):
                texts[result["url"]] = result["raw_content"]
        if failed := response.get("failed_results"):
            logger.info("Tavily could not extract %d URLs; using snippets", len(failed))
    return texts
