import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings
from app.models.project import Project
from app.models.skill import Skill
from app.models.experience import Experience


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_settings():
    return Settings(
        mongo_uri="mongodb://localhost:27017/test_portfolio_db",
        db_name="test_portfolio_db"
    )


@pytest.fixture(scope="session")
async def test_database(test_settings):
    client = AsyncIOMotorClient(test_settings.mongo_uri)
    db = client[test_settings.db_name]

    await init_beanie(
        database=db,
        document_models=[Project, Skill, Experience],
        skip_indexes=True
    )

    yield db

    await client.drop_database(test_settings.db_name)
    client.close()


@pytest.fixture(scope="function")
async def clean_database(test_database):
    collections = await test_database.list_collection_names()
    for collection in collections:
        await test_database[collection].delete_many({})

    yield test_database


@pytest.fixture(scope="function")
def client(clean_database):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project description",
        "tech_stack": ["Python", "FastAPI", "MongoDB"]
    }


@pytest.fixture(scope="function")
async def sample_skill_data():
    """Sample skill data for testing."""
    return {
        "name": "Python",
        "level": "Advanced",
        "category": "Programming Language"
    }


@pytest.fixture(scope="function")
async def sample_experience_data():
    """Sample experience data for testing."""
    return {
        "title": "Software Developer",
        "company": "Test Company",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "description": "Test experience description",
        "technologies": ["Python", "FastAPI"]
    }