"""Integration tests run against a real MongoDB (a service container in CI).

Locally: `docker compose up -d mongodb`, then `pytest`. They're skipped if MongoDB is
unreachable, unless REQUIRE_MONGO=1 (set in CI so a broken service fails the build).
"""

import os

import pytest
from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.models import DOCUMENT_MODELS

TEST_MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017")
TEST_DB_NAME = "portfolio_test"


@pytest.fixture
async def db():
    client = AsyncMongoClient(TEST_MONGO_URI, serverSelectionTimeoutMS=1500)
    try:
        await client.admin.command("ping")
    except ServerSelectionTimeoutError:
        await client.close()
        if os.getenv("REQUIRE_MONGO") == "1":
            raise
        pytest.skip(f"MongoDB not reachable at {TEST_MONGO_URI}")

    await client.drop_database(TEST_DB_NAME)
    await init_beanie(database=client[TEST_DB_NAME], document_models=DOCUMENT_MODELS)
    yield client[TEST_DB_NAME]
    await client.drop_database(TEST_DB_NAME)
    await client.close()
