import pytest

from app.services.experience_service import ExperienceService
from app.services.project_service import ProjectService

@pytest.mark.asyncio
async def test_get_projects_returns_pagination_meta(monkeypatch):
    service = ProjectService()

    async def mock_get_projects(skip, limit):
        assert skip == 5
        assert limit == 5
        return [
            {"id": "1", "name": "Project A", "description": "Desc", "tech_stack": ["Python"]},
            {"id": "2", "name": "Project B", "description": "Desc", "tech_stack": ["FastAPI"]},
        ], 12

    service.repo.get_projects = mock_get_projects
    monkeypatch.setattr("app.core.cache.get_cached_resource", lambda key: None)
    monkeypatch.setattr("app.core.cache.set_cached_resource", lambda key, data: None)

    response = await service.get_projects(page=2, size=5)

    assert response["meta"]["total"] == 12
    assert response["meta"]["page"] == 2
    assert response["meta"]["size"] == 5
    assert response["meta"]["pages"] == 3
    assert len(response["items"]) == 2

@pytest.mark.asyncio
async def test_get_experiences_filters_by_company_case_insensitive(monkeypatch):
    service = ExperienceService()

    async def mock_get_experiences(skip, limit, company):
        assert skip == 0
        assert limit == 10
        assert company == "Acme Corp"
        return [
            {"id": "1", "title": "Dev", "company": "Acme Corp", "description": "Work"}
        ], 1

    service.repo.get_experiences = mock_get_experiences
    monkeypatch.setattr("app.core.cache.get_cached_resource", lambda key: None)
    monkeypatch.setattr("app.core.cache.set_cached_resource", lambda key, data: None)

    response = await service.get_experiences(page=1, size=10, company="Acme Corp")

    assert response["meta"]["total"] == 1
    assert response["meta"]["page"] == 1
    assert response["meta"]["size"] == 10
    assert response["meta"]["pages"] == 1
    assert len(response["items"]) == 1
    assert response["items"][0]["company"] == "Acme Corp"
