"""Thin async wrapper around the Gemini API (google-genai SDK)."""

import logging
from functools import lru_cache
from typing import Literal, TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

SchemaT = TypeVar("SchemaT", bound=BaseModel)
EmbeddingTask = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]


@lru_cache
def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise AIServiceError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=settings.gemini_api_key)


async def generate_structured(prompt: str, schema: type[SchemaT]) -> SchemaT:
    """Ask Gemini for JSON that is guaranteed to validate against `schema`."""
    try:
        response = await _client().aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.2,  # scoring should be stable, not creative
            ),
        )
    except errors.APIError as exc:
        logger.error("Gemini generate_content failed: %s", exc)
        raise AIServiceError(f"Gemini request failed: {exc.message}") from exc

    if isinstance(response.parsed, schema):
        return response.parsed
    # The SDK leaves `parsed` empty if the JSON didn't validate; surface why.
    try:
        return schema.model_validate_json(response.text or "")
    except ValidationError as exc:
        logger.error("Gemini returned invalid %s: %s", schema.__name__, response.text)
        raise AIServiceError(f"Gemini returned an invalid {schema.__name__}") from exc


async def embed(texts: list[str], task: EmbeddingTask) -> list[list[float]]:
    """Embed a batch of texts. Documents and queries use different task types."""
    if not texts:
        return []
    try:
        response = await _client().aio.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task),
        )
    except errors.APIError as exc:
        logger.error("Gemini embed_content failed: %s", exc)
        raise AIServiceError(f"Gemini embedding failed: {exc.message}") from exc
    return [e.values or [] for e in response.embeddings or []]
