from app.api.v1 import jobs
from app.core.exceptions import AIServiceError
from app.schemas.job import JobAnalysis

JOB_DESCRIPTION = "We are hiring a junior backend engineer with Python, FastAPI and MongoDB. " * 2


def test_list_jobs_passes_min_score_filter(client, monkeypatch):
    seen = {}

    async def list_matches(min_score, limit):
        seen.update(min_score=min_score, limit=limit)
        return [{
            "_id": "65f000000000000000000002", "title": "Backend Dev", "url": "https://x/1",
            "source": "x", "search_query": "q", "match_score": 91,
        }]

    monkeypatch.setattr(jobs.JobRepository, "list_matches", list_matches)
    response = client.get("/api/v1/jobs?min_score=70&limit=10")

    assert response.status_code == 200
    assert seen == {"min_score": 70, "limit": 10}
    assert response.json()[0]["match_score"] == 91


def test_list_jobs_rejects_out_of_range_score(client):
    assert client.get("/api/v1/jobs?min_score=150").status_code == 422


def test_analyze_returns_fit_and_cv_bullets(client, auth_headers, monkeypatch):
    async def analyze(description):
        return JobAnalysis(
            score=78, matched_skills=["Python", "FastAPI"], missing_skills=["AWS"],
            reason="Solid backend fit", cv_bullets=["Built X", "Designed Y", "Shipped Z"],
        )

    monkeypatch.setattr(jobs.job_service, "analyze_job_description", analyze)
    response = client.post("/api/v1/jobs/analyze", json={"description": JOB_DESCRIPTION}, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 78
    assert body["missing_skills"] == ["AWS"]
    assert len(body["cv_bullets"]) == 3


def test_analyze_rejects_too_short_description(client, auth_headers):
    response = client.post("/api/v1/jobs/analyze", json={"description": "Python dev"}, headers=auth_headers)
    assert response.status_code == 422


def test_ai_outage_returns_503(client, auth_headers, monkeypatch):
    async def analyze(description):
        raise AIServiceError("Gemini request failed")

    monkeypatch.setattr(jobs.job_service, "analyze_job_description", analyze)
    response = client.post("/api/v1/jobs/analyze", json={"description": JOB_DESCRIPTION}, headers=auth_headers)

    assert response.status_code == 503
    assert response.json()["code"] == "AI_SERVICE_UNAVAILABLE"
