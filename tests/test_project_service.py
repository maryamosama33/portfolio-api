import pytest
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate
from app.core.exceptions import ProjectNotFoundError

@pytest.mark.asyncio
async def test_create_project_happy_path(monkeypatch):
    service = ProjectService()

    class MockRepo:
        async def create_project(self, project_create, user_id=None):
            return {"name": project_create.name}
    service.repo = MockRepo()

    project_input = ProjectCreate(
    name="Test Project",
    description="A sample project",
    tech_stack=["Python", "FastAPI"]
    )
    result = await service.create_project(project_input)
    assert result["name"] == "Test Project"

@pytest.mark.asyncio
async def test_get_project_not_found(monkeypatch):
    service = ProjectService()

    class MockRepo:
        async def get_project_by_id(self, project_id):
            return None
    service.repo = MockRepo()

    with pytest.raises(ProjectNotFoundError):
        await service.get_project("nonexistent_id")