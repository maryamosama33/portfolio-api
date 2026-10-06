from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, examples=["Portfolio API"])
    description: str = Field(min_length=1)
    tech_stack: list[str] = Field(examples=[["Python", "FastAPI", "MongoDB"]])


class ProjectRead(ProjectCreate, ReadBase):
    pass
