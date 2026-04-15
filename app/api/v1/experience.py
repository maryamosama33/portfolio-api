from beanie import PydanticObjectId
from fastapi import APIRouter, Header, Query
from app.services.experience_service import ExperienceService
from app.schemas.pagination import PaginatedResponse
from app.schemas.experience import ExperienceCreate, ExperienceRead

router = APIRouter()
service = ExperienceService()

@router.post("/experience")
async def create_experience(
    experience: ExperienceCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.create_experience(experience, user_id=x_user_id)

@router.get("/experiences", response_model=PaginatedResponse[ExperienceRead])
async def get_experiences(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    company: str | None = Query(None),
):
    return await service.get_experiences(page, size, company)

@router.get("/experience/{experience_id}")
async def get_experience(experience_id: PydanticObjectId):
    return await service.get_experience(experience_id)

@router.put("/experience/{experience_id}")
async def update_experience(
    experience_id: PydanticObjectId,
    experience: ExperienceCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.update_experience(experience_id, experience, user_id=x_user_id)

@router.delete("/experience/{experience_id}")
async def delete_experience(
    experience_id: PydanticObjectId,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.delete_experience(experience_id, user_id=x_user_id)