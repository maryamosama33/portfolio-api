from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field


class ReadBase(BaseModel):
    """Fields every stored resource exposes in API responses."""

    # Mongo stores `_id`; the API exposes it as `id`.
    id: str = Field(validation_alias=AliasChoices("_id", "id"))
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
