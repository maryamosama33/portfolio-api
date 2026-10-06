from fastapi import APIRouter, Query

from app.api.deps import CurrentUser
from app.schemas.portfolio import PortfolioSearchResponse, ReindexResult
from app.services import portfolio_index

router = APIRouter(prefix="/portfolio", tags=["Portfolio search (RAG)"])


@router.get("/search", response_model=PortfolioSearchResponse)
async def search_portfolio(
    q: str = Query(min_length=2, max_length=500, description="Natural-language question"),
    k: int = Query(5, ge=1, le=20),
):
    """Semantic search over projects, skills and experience. Used by the chatbot."""
    return PortfolioSearchResponse(query=q, results=await portfolio_index.search(q, k))


@router.post("/reindex", response_model=ReindexResult)
async def reindex_portfolio(user: CurrentUser):
    """Re-embed every portfolio item. Run once after upgrading, or after changing embedding model."""
    return ReindexResult(indexed=await portfolio_index.reindex_all())
