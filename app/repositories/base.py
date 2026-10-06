from typing import Any, Generic, TypeVar

from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.base import BaseDocument, utcnow

ModelT = TypeVar("ModelT", bound=BaseDocument)


class BaseRepository(Generic[ModelT]):
    """CRUD over one collection. Soft-deleted documents are invisible to every read."""

    model: type[ModelT]

    def _active(self, filters: dict[str, Any] | None = None):
        return self.model.find({"is_deleted": {"$ne": True}, **(filters or {})})

    async def create(self, data: BaseModel, user_id: str | None = None) -> ModelT:
        doc = self.model(**data.model_dump(), created_by=user_id, updated_by=user_id)
        return await doc.insert()

    async def paginate(
        self, skip: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[ModelT], int]:
        query = self._active(filters)
        total = await query.count()
        items = await query.sort("-created_at").skip(skip).limit(limit).to_list()
        return items, total

    async def list_all(self) -> list[ModelT]:
        return await self._active().to_list()

    async def get(self, doc_id: PydanticObjectId) -> ModelT | None:
        return await self._active({"_id": doc_id}).first_or_none()

    async def update(
        self, doc_id: PydanticObjectId, data: BaseModel, user_id: str | None = None
    ) -> ModelT | None:
        doc = await self.get(doc_id)
        if not doc:
            return None
        await doc.set({**data.model_dump(), "updated_at": utcnow(), "updated_by": user_id})
        return doc

    async def soft_delete(self, doc_id: PydanticObjectId, user_id: str | None = None) -> ModelT | None:
        doc = await self.get(doc_id)
        if not doc:
            return None
        return await doc.soft_delete(deleted_by=user_id)
