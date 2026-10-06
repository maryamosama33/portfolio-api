from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser
from app.repositories.project_repository import ProjectRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.crud_service import CrudService

router = APIRouter(prefix="/projects", tags=["Projects"])
service = CrudService("project", ProjectRepository())


@router.get("", response_model=PaginatedResponse[ProjectRead])
async def list_projects(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50)):
    return await service.paginate(page, size)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: PydanticObjectId):
    return await service.get(project_id)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, user: CurrentUser):
    return await service.create(project, user_id=user)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: PydanticObjectId, project: ProjectCreate, user: CurrentUser):
    return await service.update(project_id, project, user_id=user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: PydanticObjectId, user: CurrentUser):
    await service.delete(project_id, user_id=user)
