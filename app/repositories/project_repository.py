from datetime import datetime

from beanie import PydanticObjectId

from app.models.project import Project
from app.schemas.project import ProjectCreate

class ProjectRepository:

    async def create_project(self, project_create: ProjectCreate, user_id: str | None = None):
        project = Project(
            **project_create.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await project.insert()

    async def get_projects(self, skip: int, limit: int):
        query = Project.find_all()
        items = await query.skip(skip).limit(limit).to_list()
        total = await Project.find_all().count()
        return items, total

    async def get_project_by_id(self, project_id: PydanticObjectId, include_deleted: bool = False):
        return await Project.get(project_id, include_deleted=include_deleted)
    
    async def update_project(self, project_id: PydanticObjectId, project: ProjectCreate, user_id: str | None = None):
        project_doc = await Project.get(project_id)

        if not project_doc:
            return None

        await project_doc.set(
            {
                **project.model_dump(),
                "updated_at": datetime.utcnow(),
                "updated_by": user_id,
            }
        )
        return project_doc

    async def delete_project(self, project_id: PydanticObjectId, user_id: str | None = None):
        project_doc = await Project.get(project_id)

        if not project_doc:
            return None

        return await project_doc.delete(deleted_by=user_id)
