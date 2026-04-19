from app.models.base import BaseDocument
from typing import Optional


class Job(BaseDocument):
    title: str
    company: str
    url: str
    snippet: str
    source: str
    matched_skills: list[str] = []
    match_score: Optional[float] = None
    search_query: str
