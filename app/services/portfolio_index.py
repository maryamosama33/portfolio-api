"""Vector index over the portfolio, so the chatbot retrieves only relevant items (RAG).

Each project, skill and experience is embedded with Gemini when it's written and stored
in the `portfolio_embeddings` collection. Search embeds the query and ranks by cosine
similarity in Python, which is plenty for a portfolio-sized corpus (tens of documents).
At larger scale this would move to MongoDB Atlas `$vectorSearch`.
"""

import logging
import math

from beanie import PydanticObjectId

from app.core.config import settings
from app.models.base import BaseDocument, utcnow
from app.models.experience import Experience
from app.models.portfolio_embedding import PortfolioEmbedding, SourceType
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.portfolio import PortfolioSearchHit
from app.services.ai import gemini
from app.services.portfolio_service import load_snapshot

logger = logging.getLogger(__name__)


def document_text(doc: BaseDocument) -> tuple[SourceType, str]:
    """The text that represents a portfolio item in the index."""
    match doc:
        case Project():
            return "project", (
                f"Project: {doc.name}\nTech stack: {', '.join(doc.tech_stack)}\n{doc.description}"
            )
        case Skill():
            return "skill", f"Skill: {doc.name} (level: {doc.level})"
        case Experience():
            return "experience", f"Experience: {doc.title} at {doc.company}\n{doc.description}"
    raise TypeError(f"{type(doc).__name__} is not indexable")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


async def _upsert(source_type: SourceType, source_id: PydanticObjectId, text: str, vector: list[float]):
    existing = await PortfolioEmbedding.find_one(
        {"source_type": source_type, "source_id": source_id}
    )
    if existing:
        await existing.set(
            {"text": text, "embedding": vector, "model": settings.gemini_embedding_model, "updated_at": utcnow()}
        )
    else:
        await PortfolioEmbedding(
            source_type=source_type,
            source_id=source_id,
            text=text,
            embedding=vector,
            model=settings.gemini_embedding_model,
        ).insert()


async def index_document(doc: BaseDocument) -> None:
    source_type, text = document_text(doc)
    [vector] = await gemini.embed([text], task="RETRIEVAL_DOCUMENT")
    await _upsert(source_type, doc.id, text, vector)


async def remove_document(source_type: SourceType, source_id: PydanticObjectId) -> None:
    await PortfolioEmbedding.find({"source_type": source_type, "source_id": source_id}).delete()


async def reindex_all() -> int:
    """Rebuild the whole index, e.g. after importing data or changing embedding model."""
    snapshot = await load_snapshot()
    docs: list[BaseDocument] = [*snapshot.projects, *snapshot.skills, *snapshot.experiences]
    entries = [(doc.id, *document_text(doc)) for doc in docs]
    vectors = await gemini.embed([text for _, _, text in entries], task="RETRIEVAL_DOCUMENT")

    await PortfolioEmbedding.find_all().delete()
    for (doc_id, source_type, text), vector in zip(entries, vectors):
        await _upsert(source_type, doc_id, text, vector)
    logger.info("Reindexed %d portfolio documents", len(entries))
    return len(entries)


async def search(query: str, k: int = 5) -> list[PortfolioSearchHit]:
    [query_vector] = await gemini.embed([query], task="RETRIEVAL_QUERY")
    chunks = await PortfolioEmbedding.find({"model": settings.gemini_embedding_model}).to_list()
    scored = sorted(
        ((cosine_similarity(query_vector, c.embedding), c) for c in chunks),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return [
        PortfolioSearchHit(
            source_type=c.source_type, source_id=str(c.source_id), text=c.text, score=round(score, 4)
        )
        for score, c in scored[:k]
    ]
