from datetime import datetime

from beanie import PydanticObjectId

from app.models.skill import Skill
from app.schemas.skill import SkillCreate

class SkillRepository:
    async def create_skill(self, skill: SkillCreate, user_id: str | None = None):
        skill_doc = Skill(
            **skill.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await skill_doc.insert()

    async def get_skills(self, skip: int, limit: int):
        query = Skill.find_all()
        items = await query.skip(skip).limit(limit).to_list()
        total = await Skill.find_all().count()
        return items, total
    

    async def get_skill_by_id(self, skill_id: PydanticObjectId, include_deleted: bool = False):
        return await Skill.get(skill_id, include_deleted=include_deleted)

    async def update_skill(self, skill_id: PydanticObjectId, skill: SkillCreate, user_id: str | None = None):
        skill_doc = await Skill.get(skill_id)

        if not skill_doc:
            return None

        await skill_doc.set(
            {
                **skill.model_dump(),
                "updated_at": datetime.utcnow(),
                "updated_by": user_id,
            }
        )
        return skill_doc

    async def delete_skill(self, skill_id: PydanticObjectId, user_id: str | None = None):
        skill_doc = await Skill.get(skill_id)

        if not skill_doc:
            return None

        return await skill_doc.delete(deleted_by=user_id)