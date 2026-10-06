import pytest

from app.core.exceptions import AIServiceError, PortfolioIncompleteError
from app.models.skill import Skill
from app.schemas.job import JobPostingMatch
from app.services import job_service
from app.services.job_search import SearchHit
from app.services.portfolio_service import PortfolioSnapshot

SNAPSHOT = PortfolioSnapshot(
    skills=[Skill.model_construct(name="Python", level="Expert"), Skill.model_construct(name="FastAPI", level="Advanced")],
    projects=[],
    experiences=[],
)


@pytest.fixture
def pipeline(monkeypatch):
    """Stub every external dependency of run_job_search and record what it saw."""
    state = {"saved": [], "scored_texts": {}}
    hits = [
        SearchHit("https://www.linkedin.com/jobs/1", "Backend Dev", "snippet 1", "q1"),
        SearchHit("https://wuzzuf.net/jobs/2", "Python Dev", "snippet 2", "q1"),
        SearchHit("https://indeed.com/jobs/known", "Old Job", "snippet", "q2"),
        SearchHit("https://indeed.com/jobs/flaky", "Flaky", "snippet", "q2"),
    ]

    async def load_snapshot():
        return SNAPSHOT

    async def search_jobs(queries):
        return hits

    async def existing_urls(urls):
        return {"https://indeed.com/jobs/known"}

    async def extract_full_text(urls):
        assert "https://indeed.com/jobs/known" not in urls  # known jobs aren't re-fetched
        return {"https://www.linkedin.com/jobs/1": "Full posting: Python, FastAPI, Kubernetes"}

    async def score_job_posting(profile, posting):
        assert "Python (Expert)" in profile
        url = posting.split("URL: ")[1].split("\n")[0]
        state["scored_texts"][url] = posting
        if "flaky" in url:
            raise AIServiceError("Gemini timeout")
        score = 88 if "linkedin" in url else 55
        return JobPostingMatch(
            score=score, matched_skills=["Python"], missing_skills=["Kubernetes"],
            reason="Strong Python match", title=None if "wuzzuf" in url else "Senior Backend Engineer",
            company="Acme",
        )

    async def create(job):
        state["saved"].append(job)
        return job

    monkeypatch.setattr(job_service, "load_snapshot", load_snapshot)
    monkeypatch.setattr(job_service.job_search, "search_jobs", search_jobs)
    monkeypatch.setattr(job_service.job_search, "extract_full_text", extract_full_text)
    monkeypatch.setattr(job_service.matching, "score_job_posting", score_job_posting)
    monkeypatch.setattr(job_service.JobRepository, "existing_urls", existing_urls)
    monkeypatch.setattr(job_service.JobRepository, "create", create)
    monkeypatch.setattr(job_service, "Job", lambda **kw: type("FakeJob", (), kw)())
    return state


async def test_pipeline_scores_and_saves_only_new_jobs(pipeline):
    summary = await job_service.run_job_search()

    assert summary.results_found == 4
    assert summary.new_jobs == 3  # the known URL was skipped
    assert summary.jobs_saved == 2  # the flaky one failed scoring and will be retried next run
    assert [m["score"] for m in summary.top_matches] == [88, 55]  # best match first


async def test_pipeline_saves_match_details(pipeline):
    await job_service.run_job_search()
    linkedin = next(j for j in pipeline["saved"] if "linkedin" in j.url)

    assert linkedin.match_score == 88
    assert linkedin.matched_skills == ["Python"]
    assert linkedin.missing_skills == ["Kubernetes"]
    assert linkedin.match_reason == "Strong Python match"
    assert linkedin.title == "Senior Backend Engineer"  # LLM-extracted title wins
    assert linkedin.source == "linkedin.com"
    assert linkedin.content == "Full posting: Python, FastAPI, Kubernetes"


async def test_pipeline_falls_back_to_snippet_and_search_title(pipeline):
    await job_service.run_job_search()
    wuzzuf = next(j for j in pipeline["saved"] if "wuzzuf" in j.url)

    assert "snippet 2" in pipeline["scored_texts"][wuzzuf.url]
    assert wuzzuf.content is None
    assert wuzzuf.title == "Python Dev"


async def test_pipeline_requires_skills(monkeypatch):
    async def empty():
        return PortfolioSnapshot(skills=[], projects=[], experiences=[])

    monkeypatch.setattr(job_service, "load_snapshot", empty)
    with pytest.raises(PortfolioIncompleteError):
        await job_service.run_job_search()
