import re
from datetime import datetime
from beanie import PydanticObjectId

from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate

class ExperienceRepository:
    async def create_experience(self, experience: ExperienceCreate, user_id: str | None = None):
        experience_doc = Experience(
            **experience.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await experience_doc.insert()

    async def get_experiences(self, skip: int, limit: int, company: str | None = None):
        if company:
            regex = rf"^{re.escape(company)}$"
            base_query = Experience.find_many(
                {"company": {"$regex": regex, "$options": "i"}}
            )
        else:
            base_query = Experience.find_all()

        total = await base_query.count()
        items = await base_query.skip(skip).limit(limit).to_list()
        return items, total
    
    async def get_experience_by_id(self, experience_id: PydanticObjectId, include_deleted: bool = False):
        return await Experience.get(experience_id, include_deleted=include_deleted)
    
    async def update_experience(self, experience_id: PydanticObjectId, experience: ExperienceCreate, user_id: str | None = None):
        experience_doc = await Experience.get(experience_id)

        if not experience_doc:
            return None

        await experience_doc.set(
            {
                **experience.model_dump(),
                "updated_at": datetime.utcnow(),
                "updated_by": user_id,
            }
        )
        return experience_doc
    
    async def delete_experience(self, experience_id: PydanticObjectId, user_id: str | None = None):
        experience_doc = await Experience.get(experience_id)

        if not experience_doc:
            return None

        return await experience_doc.delete(deleted_by=user_id)
