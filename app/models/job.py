from datetime import datetime
from typing import Annotated

from beanie import Indexed

from app.models.base import BaseDocument


class Job(BaseDocument):
    """A job posting found by the job matcher and scored against the portfolio."""

    title: str
    company: str | None = None
    url: Annotated[str, Indexed(unique=True)]
    source: str  # domain the posting came from, e.g. "linkedin.com"
    snippet: str = ""  # search-result excerpt
    content: str | None = None  # full posting text from Tavily extract
    search_query: str

    match_score: Annotated[float | None, Indexed()] = None
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    match_reason: str | None = None
    scored_at: datetime | None = None
