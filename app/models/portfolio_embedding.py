from datetime import datetime
from typing import Literal

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.base import utcnow

SourceType = Literal["project", "skill", "experience"]


class PortfolioEmbedding(Document):
    """One embedded chunk of the portfolio, used for RAG search by the chatbot."""

    source_type: SourceType
    source_id: PydanticObjectId
    text: str
    embedding: list[float]
    model: str
    updated_at: datetime = Field(default_factory=utcnow)

    class Settings:
        name = "portfolio_embeddings"
        indexes = [
            pymongo.IndexModel(
                [("source_type", pymongo.ASCENDING), ("source_id", pymongo.ASCENDING)],
                unique=True,
            )
        ]
