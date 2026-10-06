from datetime import datetime, timezone

from app.models.experience import Experience
from app.models.skill import Skill
from app.services import job_search
from app.services.job_search import build_search_queries
from app.services.portfolio_service import PortfolioSnapshot


def skill(name: str, level: str) -> Skill:
    return Skill.model_construct(name=name, level=level)


def snapshot(skills=(), experiences=()) -> PortfolioSnapshot:
    return PortfolioSnapshot(skills=list(skills), projects=[], experiences=list(experiences))


def test_top_skills_rank_by_level():
    snap = snapshot([skill("Docker", "Beginner"), skill("Python", "Expert"), skill("FastAPI", "Advanced")])
    assert snap.top_skills(2) == ["Python", "FastAPI"]


def test_queries_pair_top_skills_and_add_location():
    snap = snapshot([
        skill("Python", "Expert"), skill("FastAPI", "Advanced"),
        skill("MongoDB", "Intermediate"), skill("Docker", "Intermediate"),
    ])
    assert build_search_queries(snap, location="Egypt") == [
        "Python FastAPI developer job Egypt",
        "MongoDB Docker developer job Egypt",
    ]


def test_queries_include_latest_experience_title():
    old = Experience.model_construct(
        title="Intern", company="A", description="", created_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
    )
    new = Experience.model_construct(
        title="Backend Developer", company="B", description="", created_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )
    snap = snapshot([skill("Python", "Expert"), skill("FastAPI", "Advanced")], [old, new])
    queries = build_search_queries(snap, location="")
    assert queries[1] == "Backend Developer Python job"


def test_queries_are_capped_and_unique():
    snap = snapshot([skill(f"Skill{i}", "Advanced") for i in range(10)], [
        Experience.model_construct(title="Engineer", company="X", description="", created_at=datetime.now(timezone.utc))
    ])
    queries = build_search_queries(snap, location="Remote")
    assert len(queries) == job_search.MAX_QUERIES
    assert len(set(queries)) == len(queries)


def test_no_skills_means_no_queries():
    assert build_search_queries(snapshot(), location="Egypt") == []


class FakeTavily:
    def __init__(self):
        self.extract_batches: list[list[str]] = []

    async def search(self, query, **kwargs):
        if query == "broken":
            raise RuntimeError("rate limited")
        return {"results": [
            {"url": "https://jobs.example/shared", "title": "Shared", "content": f"from {query}"},
            {"url": f"https://jobs.example/{query}", "title": query, "content": "snippet"},
        ]}

    async def extract(self, urls, **kwargs):
        self.extract_batches.append(urls)
        return {
            "results": [{"url": u, "raw_content": f"full text of {u}"} for u in urls if "bad" not in u],
            "failed_results": [{"url": u} for u in urls if "bad" in u],
        }


async def test_search_merges_queries_and_dedupes_urls(monkeypatch):
    monkeypatch.setattr(job_search, "_client", lambda: FakeTavily())
    hits = await job_search.search_jobs(["a", "broken", "b"])

    assert [h.url for h in hits] == [
        "https://jobs.example/shared", "https://jobs.example/a", "https://jobs.example/b",
    ]
    assert hits[0].snippet == "from a"  # first query to find a URL wins


async def test_extract_batches_urls_and_skips_failures(monkeypatch):
    fake = FakeTavily()
    monkeypatch.setattr(job_search, "_client", lambda: fake)
    urls = [f"https://jobs.example/{i}" for i in range(25)] + ["https://jobs.example/bad"]

    texts = await job_search.extract_full_text(urls)

    assert [len(b) for b in fake.extract_batches] == [20, 6]
    assert len(texts) == 25
    assert "https://jobs.example/bad" not in texts
