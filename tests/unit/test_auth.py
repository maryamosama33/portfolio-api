import jwt
import pytest

from app.api.v1 import projects
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token


def test_login_returns_bearer_token(client, auth_headers):
    assert auth_headers["Authorization"].startswith("Bearer ")


@pytest.mark.parametrize(
    "username,password",
    [("admin", "wrong-password"), ("someone-else", "test-password")],
)
def test_login_rejects_bad_credentials(client, username, password):
    response = client.post("/api/v1/auth/token", data={"username": username, "password": password})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method,path",
    [
        ("post", "/api/v1/projects"),
        ("put", "/api/v1/projects/65f000000000000000000000"),
        ("delete", "/api/v1/projects/65f000000000000000000000"),
        ("post", "/api/v1/skills"),
        ("post", "/api/v1/experiences"),
        ("post", "/api/v1/jobs/search"),
        ("post", "/api/v1/jobs/analyze"),
        ("post", "/api/v1/portfolio/reindex"),
    ],
)
def test_write_routes_require_token(client, method, path):
    response = client.request(method, path, json={})
    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.post(
        "/api/v1/projects",
        json={"name": "x", "description": "y", "tech_stack": []},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)
    token = create_access_token("admin")
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_read_routes_are_public(client, monkeypatch):
    async def fake_paginate(page, size, **kwargs):
        return {"items": [], "meta": {"total": 0, "page": page, "size": size, "pages": 0}}

    monkeypatch.setattr(projects.service, "paginate", fake_paginate)
    assert client.get("/api/v1/projects").status_code == 200


def test_authenticated_write_records_the_user(client, auth_headers, monkeypatch):
    seen = {}

    async def fake_create(data, user_id=None):
        seen["user_id"] = user_id
        return {"_id": "65f000000000000000000000", **data.model_dump()}

    monkeypatch.setattr(projects.service, "create", fake_create)
    response = client.post(
        "/api/v1/projects",
        json={"name": "Portfolio API", "description": "Backend", "tech_stack": ["FastAPI"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["id"] == "65f000000000000000000000"
    assert seen["user_id"] == "admin"
