from datetime import datetime, timezone

import pytest
from pymongo.errors import DuplicateKeyError

from app.models.job import Job
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.job_repository import JobRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.experience import ExperienceCreate
from app.schemas.project import ProjectCreate

pytestmark = pytest.mark.integration


def project(name: str) -> ProjectCreate:
    return ProjectCreate(name=name, description=f"{name} description", tech_stack=["Python"])


async def test_soft_deleted_documents_are_hidden_but_kept(db):
    repo = ProjectRepository()
    keep = await repo.create(project("Keep"), user_id="admin")
    gone = await repo.create(project("Gone"), user_id="admin")

    deleted = await repo.soft_delete(gone.id, user_id="admin")

    assert deleted.is_deleted and deleted.deleted_by == "admin"
    assert await repo.get(gone.id) is None
    items, total = await repo.paginate(skip=0, limit=10)
    assert total == 1 and [p.id for p in items] == [keep.id]
    assert await repo.update(gone.id, project("Revived")) is None
    assert await db["Project"].count_documents({}) == 2  # still stored


async def test_audit_fields_are_persisted(db):
    repo = ProjectRepository()
    created = await repo.create(project("Audited"), user_id="admin")
    updated = await repo.update(created.id, project("Audited v2"), user_id="editor")

    stored = await repo.get(created.id)
    assert stored.created_by == "admin"
    assert stored.updated_by == "editor"
    assert updated.updated_at is not None


async def test_paginate_is_newest_first(db):
    repo = ProjectRepository()
    for name in ("first", "second", "third"):
        await repo.create(project(name))

    page, total = await repo.paginate(skip=1, limit=1)
    assert total == 3
    assert page[0].name == "second"


async def test_company_filter_is_case_insensitive_exact_match(db):
    repo = ExperienceRepository()
    await repo.create(ExperienceCreate(title="Dev", company="Acme Corp", description="x"))
    await repo.create(ExperienceCreate(title="Dev", company="Acme Corporation", description="x"))

    items, total = await repo.paginate(0, 10, filters=repo.company_filter("acme corp"))
    assert total == 1 and items[0].company == "Acme Corp"


def job(url: str, score: float | None, **kwargs) -> Job:
    return Job(title=url, url=url, source="example.com", search_query="q", match_score=score, **kwargs)


async def test_list_matches_sorts_by_score_and_filters(db):
    for url, score in [("https://a", 55), ("https://b", 92), ("https://c", None), ("https://d", 71)]:
        await JobRepository.create(job(url, score))
    deleted = await JobRepository.create(job("https://e", 99))
    await deleted.soft_delete()

    all_jobs = await JobRepository.list_matches(min_score=None, limit=10)
    assert [j.url for j in all_jobs] == ["https://b", "https://d", "https://a", "https://c"]

    good = await JobRepository.list_matches(min_score=70, limit=10)
    assert [j.match_score for j in good] == [92, 71]


async def test_job_urls_are_unique(db):
    await JobRepository.create(job("https://same", 50))
    assert await JobRepository.existing_urls(["https://same", "https://new"]) == {"https://same"}
    with pytest.raises(DuplicateKeyError):
        await JobRepository.create(job("https://same", 60, scored_at=datetime.now(timezone.utc)))
