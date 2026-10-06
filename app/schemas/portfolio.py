from pydantic import BaseModel

from app.models.portfolio_embedding import SourceType


class PortfolioSearchHit(BaseModel):
    source_type: SourceType
    source_id: str
    text: str
    score: float  # cosine similarity, higher is more relevant


class PortfolioSearchResponse(BaseModel):
    query: str
    results: list[PortfolioSearchHit]


class ReindexResult(BaseModel):
    indexed: int
