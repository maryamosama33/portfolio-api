from beanie import PydanticObjectId
from fastapi import APIRouter, Header, Query
from app.services.project_service import ProjectService
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()
service = ProjectService()

@router.post("/project")
async def create_project(
    project: ProjectCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.create_project(project, user_id=x_user_id)

@router.get("/projects", response_model=PaginatedResponse[ProjectRead])
async def get_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    return await service.get_projects(page, size)

@router.get("/project/{project_id}")
async def get_project(project_id: PydanticObjectId):
    return await service.get_project(project_id)

@router.put("/project/{project_id}")
async def update_project(
    project_id: PydanticObjectId,
    project: ProjectCreate,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.update_project(project_id, project, user_id=x_user_id)

@router.delete("/project/{project_id}")
async def delete_project(
    project_id: PydanticObjectId,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    return await service.delete_project(project_id, user_id=x_user_id)