from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models import DOCUMENT_MODELS


async def init_db() -> AsyncMongoClient:
    """Connect to MongoDB and register all Beanie documents.

    Returns the client so callers (the API lifespan, Celery tasks) can close it.
    """
    client = AsyncMongoClient(settings.mongo_uri)
    await init_beanie(database=client[settings.db_name], document_models=DOCUMENT_MODELS)
    return client
