from datetime import datetime

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    name: str
    level: str


class SkillRead(SkillCreate):
    id: str = Field(alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    is_deleted: bool = False

    class Config:
        populate_by_name = True