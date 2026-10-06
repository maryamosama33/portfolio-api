from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceRead
from app.schemas.pagination import PaginatedResponse
from app.services.crud_service import CrudService

router = APIRouter(prefix="/experiences", tags=["Experiences"])
service = CrudService("experience", ExperienceRepository())


@router.get("", response_model=PaginatedResponse[ExperienceRead])
async def list_experiences(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    company: str | None = Query(None, description="Case-insensitive exact company name"),
):
    return await service.paginate(
        page,
        size,
        filters=ExperienceRepository.company_filter(company),
        cache_filters={"company": company},
    )


@router.get("/{experience_id}", response_model=ExperienceRead)
async def get_experience(experience_id: PydanticObjectId):
    return await service.get(experience_id)


@router.post("", response_model=ExperienceRead, status_code=status.HTTP_201_CREATED)
async def create_experience(experience: ExperienceCreate, user: CurrentUser):
    return await service.create(experience, user_id=user)


@router.put("/{experience_id}", response_model=ExperienceRead)
async def update_experience(experience_id: PydanticObjectId, experience: ExperienceCreate, user: CurrentUser):
    return await service.update(experience_id, experience, user_id=user)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(experience_id: PydanticObjectId, user: CurrentUser):
    await service.delete(experience_id, user_id=user)
