import pytest

from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService


@pytest.mark.asyncio
async def test_project_repository_delete_project_uses_soft_delete(monkeypatch):
    repo = ProjectRepository()

    class DummyProject:
        def __init__(self):
            self.deleted = False
            self.deleted_by = None

        async def delete(self, deleted_by=None):
            self.deleted = True
            self.deleted_by = deleted_by
            return self

    dummy = DummyProject()

    async def mock_get(project_id, include_deleted=False):
        assert project_id == "abc"
        assert include_deleted is False
        return dummy

    monkeypatch.setattr("app.repositories.project_repository.Project.get", mock_get)

    result = await repo.delete_project("abc", user_id="user123")

    assert result is dummy
    assert dummy.deleted is True
    assert dummy.deleted_by == "user123"


@pytest.mark.asyncio
async def test_project_service_delete_project_passes_user_id(monkeypatch):
    service = ProjectService()

    async def mock_delete_project(project_id, user_id=None):
        assert project_id == "abc"
        assert user_id == "user456"
        return {"deleted": True}

    service.repo.delete_project = mock_delete_project

    result = await service.delete_project("abc", user_id="user456")

    assert result == {"deleted": True}
