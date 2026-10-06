"""The job matching pipeline: search -> dedupe -> extract -> score -> save."""

import asyncio
import logging
from urllib.parse import urlparse

from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.exceptions import AIServiceError, PortfolioIncompleteError
from app.models.base import utcnow
from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobAnalysis, JobPostingMatch
from app.services import job_search, matching
from app.services.job_search import SearchHit
from app.services.portfolio_service import load_snapshot

logger = logging.getLogger(__name__)

# Long pages are mostly navigation and footers; the posting itself fits well within this.
MAX_POSTING_CHARS = 12_000


class JobSearchSummary(BaseModel):
    queries: list[str]
    results_found: int
    new_jobs: int
    jobs_saved: int
    top_matches: list[dict]


def _domain(url: str) -> str:
    return urlparse(url).netloc.removeprefix("www.")


async def _score(
    hit: SearchHit, full_text: str | None, profile: str, limiter: asyncio.Semaphore
) -> tuple[SearchHit, str | None, JobPostingMatch | None]:
    posting = f"Title: {hit.title}\nURL: {hit.url}\n\n{full_text or hit.snippet}"[:MAX_POSTING_CHARS]
    async with limiter:
        try:
            return hit, full_text, await matching.score_job_posting(profile, posting)
        except AIServiceError as exc:
            logger.warning("Skipping %s, scoring failed: %s", hit.url, exc.detail)
            return hit, full_text, None


async def run_job_search() -> JobSearchSummary:
    snapshot = await load_snapshot()
    queries = job_search.build_search_queries(snapshot)
    if not queries:
        raise PortfolioIncompleteError("Add some skills to the portfolio before searching for jobs")

    hits = await job_search.search_jobs(queries)
    known = await JobRepository.existing_urls([h.url for h in hits])
    new_hits = [h for h in hits if h.url not in known]
    logger.info("Job search: %d results, %d new, from %d queries", len(hits), len(new_hits), len(queries))

    full_texts = await job_search.extract_full_text([h.url for h in new_hits])
    profile = snapshot.render_profile()
    limiter = asyncio.Semaphore(settings.job_scoring_concurrency)
    scored = await asyncio.gather(
        *(_score(h, full_texts.get(h.url), profile, limiter) for h in new_hits)
    )

    # Jobs that failed to score aren't saved, so the next run retries them.
    saved: list[Job] = []
    for hit, full_text, match in scored:
        if match is None:
            continue
        job = Job(
            title=match.title or hit.title,
            company=match.company,
            url=hit.url,
            source=_domain(hit.url),
            snippet=hit.snippet,
            content=full_text,
            search_query=hit.query,
            match_score=match.score,
            matched_skills=match.matched_skills,
            missing_skills=match.missing_skills,
            match_reason=match.reason,
            scored_at=utcnow(),
        )
        try:
            saved.append(await JobRepository.create(job))
        except DuplicateKeyError:  # another run saved it first
            continue

    saved.sort(key=lambda j: j.match_score or 0, reverse=True)
    return JobSearchSummary(
        queries=queries,
        results_found=len(hits),
        new_jobs=len(new_hits),
        jobs_saved=len(saved),
        top_matches=[
            {"title": j.title, "company": j.company, "url": j.url, "score": j.match_score}
            for j in saved[:5]
        ],
    )


async def analyze_job_description(description: str) -> JobAnalysis:
    snapshot = await load_snapshot()
    if snapshot.is_empty:
        raise PortfolioIncompleteError("The portfolio is empty, so there is nothing to match against")
    return await matching.analyze_job_description(snapshot.render_profile(), description)
