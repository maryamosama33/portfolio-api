import logging
import math
from typing import Any, Generic, TypeVar

from beanie import PydanticObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.core import cache
from app.core.exceptions import NotFoundError
from app.models.base import BaseDocument
from app.repositories.base import BaseRepository
from app.services import portfolio_index

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=BaseDocument)


class CrudService(Generic[ModelT]):
    """Cached CRUD for one portfolio resource that keeps the RAG index in sync.

    Reads go through Redis; writes invalidate the cache and re-embed the item.
    Returns JSON-ready dicts so cached and uncached responses are identical.
    """

    def __init__(self, resource: str, repo: BaseRepository[ModelT]):
        self.resource = resource  # singular, e.g. "project"
        self.repo = repo

    async def create(self, data: BaseModel, user_id: str | None = None) -> dict:
        doc = await self.repo.create(data, user_id=user_id)
        cache.invalidate(self.resource)
        await self._index(doc)
        return jsonable_encoder(doc)

    async def paginate(
        self,
        page: int,
        size: int,
        filters: dict[str, Any] | None = None,
        cache_filters: dict[str, str | None] | None = None,
    ) -> dict:
        key = cache.make_list_cache_key(self.resource, page, size, **(cache_filters or {}))
        if (cached := cache.get_cached(key)) is not None:
            return cached

        items, total = await self.repo.paginate(skip=(page - 1) * size, limit=size, filters=filters)
        response = {
            "items": jsonable_encoder(items),
            "meta": {"total": total, "page": page, "size": size, "pages": math.ceil(total / size)},
        }
        cache.set_cached(key, response)
        return response

    async def get(self, doc_id: PydanticObjectId) -> dict:
        key = cache.make_item_cache_key(self.resource, doc_id)
        if (cached := cache.get_cached(key)) is not None:
            return cached

        doc = await self.repo.get(doc_id)
        if not doc:
            raise NotFoundError(self.resource, doc_id)
        data = jsonable_encoder(doc)
        cache.set_cached(key, data)
        return data

    async def update(self, doc_id: PydanticObjectId, data: BaseModel, user_id: str | None = None) -> dict:
        doc = await self.repo.update(doc_id, data, user_id=user_id)
        if not doc:
            raise NotFoundError(self.resource, doc_id)
        cache.invalidate(self.resource, doc_id)
        await self._index(doc)
        return jsonable_encoder(doc)

    async def delete(self, doc_id: PydanticObjectId, user_id: str | None = None) -> None:
        doc = await self.repo.soft_delete(doc_id, user_id=user_id)
        if not doc:
            raise NotFoundError(self.resource, doc_id)
        cache.invalidate(self.resource, doc_id)
        await portfolio_index.remove_document(self.resource, doc_id)

    async def _index(self, doc: ModelT) -> None:
        # Best effort: a Gemini outage must not block editing the portfolio.
        # POST /portfolio/reindex repairs anything missed.
        try:
            await portfolio_index.index_document(doc)
        except Exception:
            logger.warning("Could not index %s %s for search", self.resource, doc.id, exc_info=True)
