import os

import bcrypt

# Settings are read at import time, so configure the environment before importing the app.
TEST_ADMIN_PASSWORD = "test-password"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
os.environ.setdefault(
    "ADMIN_PASSWORD_HASH", bcrypt.hashpw(TEST_ADMIN_PASSWORD.encode(), bcrypt.gensalt(4)).decode()
)
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")

import fakeredis  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core import redis as redis_module  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Every test gets an empty in-memory Redis."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(redis_module, "redis_client", fake)
    return fake


@pytest.fixture
def client():
    # No `with` block, so the lifespan (MongoDB connection) doesn't run.
    # Tests using this fixture stub out the service layer.
    return TestClient(app)


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/token", data={"username": "admin", "password": TEST_ADMIN_PASSWORD}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
