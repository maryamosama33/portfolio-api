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
from app.core.exceptions import ExperienceNotFoundError
from app.core.redis import redis_client
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate


class ExperienceService:

    def __init__(self):
        self.repo = ExperienceRepository()

    async def create_experience(self, experience: ExperienceCreate, user_id: str | None = None):
        new_experience = await self.repo.create_experience(experience, user_id=user_id)
        invalidate_list_cache("experiences")
        return new_experience

    async def get_experiences(self, page: int = 1, size: int = 10, company: str | None = None):
        cache_key = make_list_cache_key("experiences", page, size, company)
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        skip = (page - 1) * size
        experiences, total = await self.repo.get_experiences(skip, size, company)

        response = {
            "items": jsonable_encoder(experiences),
            "meta": {
                "total": total,
                "page": page,
                "size": size,
                "pages": math.ceil(total / size) if total else 0,
            },
        }

        set_cached_resource(cache_key, response)
        return response

    async def get_experience(self, experience_id: PydanticObjectId):
        cache_key = f"experience:{experience_id}"
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        experience = await self.repo.get_experience_by_id(experience_id)
        if not experience:
            raise ExperienceNotFoundError(experience_id)

        data = jsonable_encoder(experience)
        set_cached_resource(cache_key, data)
        return data

    async def update_experience(self, experience_id: PydanticObjectId, experience: ExperienceCreate, user_id: str | None = None):
        updated = await self.repo.update_experience(experience_id, experience, user_id=user_id)
        invalidate_list_cache("experiences")
        redis_client.delete(f"experience:{experience_id}")
        return updated

    async def delete_experience(self, experience_id: PydanticObjectId, user_id: str | None = None):
        deleted = await self.repo.delete_experience(experience_id, user_id=user_id)
        invalidate_list_cache("experiences")
        redis_client.delete(f"experience:{experience_id}")
        return deleted