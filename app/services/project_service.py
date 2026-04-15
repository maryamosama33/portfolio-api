import json
import math
from beanie import PydanticObjectId
from fastapi.encoders import jsonable_encoder

from app.core.cache import (
    get_cached_resource,
    invalidate_list_cache,
    make_list_cache_key,
    set_cached_resource,
)
from app.core.exceptions import ProjectNotFoundError
from app.core.redis import redis_client
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:

    def __init__(self):
        self.repo = ProjectRepository()

    async def create_project(self, project_create: ProjectCreate, user_id: str | None = None):
        project = await self.repo.create_project(project_create, user_id=user_id)
        invalidate_list_cache("projects")
        return project

    async def get_projects(self, page: int = 1, size: int = 10):
        cache_key = make_list_cache_key("projects", page, size)
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        skip = (page - 1) * size
        projects, total = await self.repo.get_projects(skip, size)

        response = {
            "items": jsonable_encoder(projects),
            "meta": {
                "total": total,
                "page": page,
                "size": size,
                "pages": math.ceil(total / size) if total else 0,
            },
        }

        set_cached_resource(cache_key, response)
        return response

    async def get_project(self, project_id: PydanticObjectId):
        cache_key = f"project:{project_id}"
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        project = await self.repo.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        data = jsonable_encoder(project)
        set_cached_resource(cache_key, data)
        return data

    async def update_project(self, project_id: PydanticObjectId, project: ProjectCreate, user_id: str | None = None):
        updated = await self.repo.update_project(project_id, project, user_id=user_id)
        invalidate_list_cache("projects")
        redis_client.delete(f"project:{project_id}")
        return updated

    async def delete_project(self, project_id: PydanticObjectId, user_id: str | None = None):
        deleted = await self.repo.delete_project(project_id, user_id=user_id)
        invalidate_list_cache("projects")
        redis_client.delete(f"project:{project_id}")
        return deleted