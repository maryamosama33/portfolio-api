from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, examples=["Python"])
    level: str = Field(min_length=1, examples=["Advanced"])


class SkillRead(SkillCreate, ReadBase):
    pass
