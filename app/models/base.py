from beanie import Document
from datetime import datetime, timezone
from pydantic import Field
from typing import Optional


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    class Settings:
        keep_nulls = False

    async def soft_delete(self, deleted_by: Optional[str] = None):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by
        self.updated_at = datetime.now(timezone.utc)

        await self.save()
        return self