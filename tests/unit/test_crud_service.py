import pytest
from beanie import PydanticObjectId

from app.core.exceptions import NotFoundError
from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.services import crud_service
from app.services.crud_service import CrudService

PROJECT_ID = PydanticObjectId("65f000000000000000000001")


def make_project(**overrides) -> Project:
    fields = {"id": PROJECT_ID, "name": "Portfolio API", "description": "Backend", "tech_stack": ["FastAPI"]}
    return Project.model_construct(**{**fields, **overrides})


class FakeRepo:
    def __init__(self, doc: Project | None = None):
        self.doc = doc
        self.calls: list[str] = []

    async def create(self, data, user_id=None):
        self.calls.append("create")
        self.doc = make_project(**data.model_dump(), created_by=user_id)
        return self.doc

    async def paginate(self, skip, limit, filters=None):
        self.calls.append(f"paginate:{skip}:{limit}")
        return ([self.doc] if self.doc else []), 12

    async def get(self, doc_id):
        self.calls.append("get")
        return self.doc

    async def update(self, doc_id, data, user_id=None):
        self.calls.append("update")
        if self.doc:
            self.doc = make_project(**data.model_dump())
        return self.doc

    async def soft_delete(self, doc_id, user_id=None):
        self.calls.append("soft_delete")
        return self.doc


@pytest.fixture
def index_calls(monkeypatch):
    calls = []

    async def fake_index(doc):
        calls.append(("index", doc.id))

    async def fake_remove(source_type, source_id):
        calls.append(("remove", source_type, source_id))

    monkeypatch.setattr(crud_service.portfolio_index, "index_document", fake_index)
    monkeypatch.setattr(crud_service.portfolio_index, "remove_document", fake_remove)
    return calls


async def test_paginate_computes_meta_and_skip():
    repo = FakeRepo(make_project())
    result = await CrudService("project", repo).paginate(page=2, size=5)

    assert repo.calls == ["paginate:5:5"]
    assert result["meta"] == {"total": 12, "page": 2, "size": 5, "pages": 3}
    assert result["items"][0]["name"] == "Portfolio API"


async def test_get_is_served_from_cache_on_second_call():
    repo = FakeRepo(make_project())
    service = CrudService("project", repo)

    first = await service.get(PROJECT_ID)
    second = await service.get(PROJECT_ID)

    assert first == second
    assert repo.calls == ["get"]


async def test_get_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        await CrudService("project", FakeRepo(None)).get(PROJECT_ID)


async def test_update_invalidates_cache_and_reindexes(index_calls):
    repo = FakeRepo(make_project())
    service = CrudService("project", repo)
    await service.get(PROJECT_ID)  # warm the cache
    await service.paginate(1, 10)

    await service.update(PROJECT_ID, ProjectCreate(name="Renamed", description="d", tech_stack=[]))

    assert (await service.get(PROJECT_ID))["name"] == "Renamed"
    assert repo.calls.count("get") == 2  # cache was dropped
    assert index_calls == [("index", PROJECT_ID)]


async def test_update_missing_raises_not_found(index_calls):
    with pytest.raises(NotFoundError):
        await CrudService("project", FakeRepo(None)).update(
            PROJECT_ID, ProjectCreate(name="x", description="y", tech_stack=[])
        )
    assert index_calls == []


async def test_create_still_succeeds_when_indexing_fails(monkeypatch):
    async def broken_index(doc):
        raise RuntimeError("Gemini is down")

    monkeypatch.setattr(crud_service.portfolio_index, "index_document", broken_index)
    result = await CrudService("project", FakeRepo()).create(
        ProjectCreate(name="New", description="d", tech_stack=[]), user_id="admin"
    )
    assert result["name"] == "New"
    assert result["created_by"] == "admin"


async def test_delete_removes_item_from_search_index(index_calls):
    await CrudService("project", FakeRepo(make_project())).delete(PROJECT_ID, user_id="admin")
    assert index_calls == [("remove", "project", PROJECT_ID)]


async def test_delete_missing_raises_not_found(index_calls):
    with pytest.raises(NotFoundError):
        await CrudService("project", FakeRepo(None)).delete(PROJECT_ID)
