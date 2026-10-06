from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


# --- LLM structured-output schemas (sent to Gemini as `response_schema`) ---

class MatchResult(BaseModel):
    """How well a job fits the portfolio owner."""

    score: int = Field(ge=0, le=100, description="Overall fit from 0 (no fit) to 100 (perfect fit).")
    matched_skills: list[str] = Field(description="Skills the job asks for that the candidate has.")
    missing_skills: list[str] = Field(description="Skills the job asks for that the candidate lacks.")
    reason: str = Field(description="One sentence explaining the score.")


class JobPostingMatch(MatchResult):
    """A match result for a scraped posting, plus fields extracted from the page."""

    title: str | None = Field(None, description="The job title as written in the posting.")
    company: str | None = Field(None, description="The hiring company, if stated.")


class JobAnalysis(MatchResult):
    """A match result plus CV bullets tailored to one job description."""

    cv_bullets: list[str] = Field(
        min_length=3,
        max_length=3,
        description="Three CV bullet points, grounded in the candidate's real projects and experience, "
        "rewritten to emphasise what this job asks for.",
    )


# --- API schemas ---

class JobRead(ReadBase):
    title: str
    company: str | None = None
    url: str
    source: str
    snippet: str = ""
    search_query: str
    match_score: float | None = None
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    match_reason: str | None = None
    scored_at: datetime | None = None


class JobSearchStarted(BaseModel):
    task_id: str
    message: str


class JobSearchStatus(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


class JobAnalyzeRequest(BaseModel):
    description: str = Field(
        min_length=50,
        max_length=20_000,
        description="The full job description text, pasted from the posting.",
    )
