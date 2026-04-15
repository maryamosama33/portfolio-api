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
from app.core.exceptions import SkillNotFoundError
from app.core.redis import redis_client
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate


class SkillService:

    def __init__(self):
        self.repo = SkillRepository()

    async def create_skill(self, skill: SkillCreate, user_id: str | None = None):
        new_skill = await self.repo.create_skill(skill, user_id=user_id)
        invalidate_list_cache("skills")
        return new_skill

    async def get_skills(self, page: int = 1, size: int = 10):
        cache_key = make_list_cache_key("skills", page, size)
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        skip = (page - 1) * size
        skills, total = await self.repo.get_skills(skip, size)

        response = {
            "items": jsonable_encoder(skills),
            "meta": {
                "total": total,
                "page": page,
                "size": size,
                "pages": math.ceil(total / size) if total else 0,
            },
        }

        set_cached_resource(cache_key, response)
        return response

    async def get_skill(self, skill_id: PydanticObjectId):
        cache_key = f"skill:{skill_id}"
        cached = get_cached_resource(cache_key)
        if cached:
            return cached

        skill = await self.repo.get_skill_by_id(skill_id)
        if not skill:
            raise SkillNotFoundError(skill_id)

        data = jsonable_encoder(skill)
        set_cached_resource(cache_key, data)
        return data

    async def update_skill(self, skill_id: PydanticObjectId, skill: SkillCreate, user_id: str | None = None):
        updated = await self.repo.update_skill(skill_id, skill, user_id=user_id)
        invalidate_list_cache("skills")
        redis_client.delete(f"skill:{skill_id}")
        return updated

    async def delete_skill(self, skill_id: PydanticObjectId, user_id: str | None = None):
        deleted = await self.repo.delete_skill(skill_id, user_id=user_id)
        invalidate_list_cache("skills")
        redis_client.delete(f"skill:{skill_id}")
        return deleted