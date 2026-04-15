from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PageMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta
