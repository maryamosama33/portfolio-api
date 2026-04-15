from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from beanie import Document
from pydantic import Field


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    is_deleted: bool = False

    @classmethod
    def _build_filter(cls, query: Any | None = None) -> Any:
        if query is None:
            return {"is_deleted": False}

        if isinstance(query, dict):
            if "is_deleted" in query:
                return query
            return {"$and": [query, {"is_deleted": False}]}

        return {"$and": [query, {"is_deleted": False}]}

    @classmethod
    def find_all(cls, include_deleted: bool = False):
        if include_deleted:
            return super().find_all()
        return super().find_many({"is_deleted": False})

    @classmethod
    def find_many(cls, query: Any | None = None, include_deleted: bool = False, **kwargs):
        if include_deleted:
            return super().find_many(query, **kwargs)
        return super().find_many(cls._build_filter(query), **kwargs)

    @classmethod
    def find_one(cls, query: Any | None = None, include_deleted: bool = False, **kwargs):
        if include_deleted:
            return super().find_one(query, **kwargs)
        return super().find_one(cls._build_filter(query), **kwargs)

    @classmethod
    async def get(cls, *args: Any, include_deleted: bool = False, **kwargs: Any):
        document = await super().get(*args, **kwargs)
        if include_deleted or not document or not getattr(document, "is_deleted", False):
            return document
        return None

    async def soft_delete(self, deleted_by: Optional[str] = None):
        if self.is_deleted:
            return self

        now = datetime.now(timezone.utc)
        update_data = {
            "$set": {
                "is_deleted": True,
                "deleted_at": now,
                "deleted_by": deleted_by,
                "updated_at": now,
                "updated_by": deleted_by,
            }
        }
        await self.update(update_data)

        self.is_deleted = True
        self.deleted_at = now
        self.deleted_by = deleted_by
        self.updated_at = now
        self.updated_by = deleted_by
        return self

    async def delete(self, deleted_by: Optional[str] = None, **kwargs: Any):
        return await self.soft_delete(deleted_by=deleted_by)
        return self
