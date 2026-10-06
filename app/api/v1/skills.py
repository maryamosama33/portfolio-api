from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser
from app.repositories.skill_repository import SkillRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.skill import SkillCreate, SkillRead
from app.services.crud_service import CrudService

router = APIRouter(prefix="/skills", tags=["Skills"])
service = CrudService("skill", SkillRepository())


@router.get("", response_model=PaginatedResponse[SkillRead])
async def list_skills(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50)):
    return await service.paginate(page, size)


@router.get("/{skill_id}", response_model=SkillRead)
async def get_skill(skill_id: PydanticObjectId):
    return await service.get(skill_id)


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
async def create_skill(skill: SkillCreate, user: CurrentUser):
    return await service.create(skill, user_id=user)


@router.put("/{skill_id}", response_model=SkillRead)
async def update_skill(skill_id: PydanticObjectId, skill: SkillCreate, user: CurrentUser):
    return await service.update(skill_id, skill, user_id=user)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: PydanticObjectId, user: CurrentUser):
    await service.delete(skill_id, user_id=user)
