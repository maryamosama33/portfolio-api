from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BaseDocument(Document):
    """Common audit and soft-delete fields for every portfolio collection."""

    created_at: datetime = Field(default_factory=utcnow)
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    is_deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    class Settings:
        keep_nulls = False

    async def soft_delete(self, deleted_by: str | None = None):
        now = utcnow()
        self.is_deleted = True
        self.deleted_at = now
        self.deleted_by = deleted_by
        self.updated_at = now
        await self.save()
        return self
