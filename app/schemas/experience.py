from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


class ExperienceCreate(BaseModel):
    title: str = Field(min_length=1, examples=["Backend Developer Intern"])
    company: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ExperienceRead(ExperienceCreate, ReadBase):
    pass
