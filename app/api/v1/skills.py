from beanie import PydanticObjectId
from fastapi import APIRouter, Header, Query
from app.services.skill_service import SkillService
from app.schemas.pagination import PaginatedResponse
from app.schemas.skill import SkillCreate, SkillRead

router = APIRouter()
service = SkillService()

@router.post("/skill")
async def create_skill(
    skill: SkillCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.create_skill(skill, user_id=x_user_id)

@router.get("/skills", response_model=PaginatedResponse[SkillRead])
async def get_skills(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    return await service.get_skills(page, size)

@router.get("/skill/{skill_id}")
async def get_skill(skill_id: PydanticObjectId):
    return await service.get_skill(skill_id)

@router.put("/skill/{skill_id}")
async def update_skill(
    skill_id: PydanticObjectId,
    skill: SkillCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.update_skill(skill_id, skill, user_id=x_user_id)

@router.delete("/skill/{skill_id}")
async def delete_skill(
    skill_id: PydanticObjectId,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.delete_skill(skill_id, user_id=x_user_id)