from fastapi import APIRouter, Query, status
from fastapi.encoders import jsonable_encoder

from app.api.deps import CurrentUser
from app.celery_app import celery_app
from app.repositories.job_repository import JobRepository
from app.schemas.job import (
    JobAnalysis,
    JobAnalyzeRequest,
    JobRead,
    JobSearchStarted,
    JobSearchStatus,
)
from app.services import job_service
from app.tasks.job_matcher import search_and_match_jobs

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=list[JobRead])
async def list_jobs(
    min_score: float | None = Query(None, ge=0, le=100, description="Only jobs scoring at least this"),
    limit: int = Query(50, ge=1, le=200),
):
    """Matched jobs, best fit first."""
    return jsonable_encoder(await JobRepository.list_matches(min_score=min_score, limit=limit))


@router.post("/search", response_model=JobSearchStarted, status_code=status.HTTP_202_ACCEPTED)
async def start_job_search(user: CurrentUser):
    """Queue a background search. It also runs every 2 hours via Celery beat."""
    task = search_and_match_jobs.delay()
    return JobSearchStarted(task_id=task.id, message="Job search started. Poll the status endpoint for results.")


@router.get("/search/{task_id}", response_model=JobSearchStatus)
async def get_job_search_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return JobSearchStatus(
        task_id=task_id,
        status=task.status,
        result=task.result if task.successful() else None,
    )


@router.post("/analyze", response_model=JobAnalysis)
async def analyze_job(request: JobAnalyzeRequest, user: CurrentUser):
    """Paste a job description and get a fit score, skill gaps and 3 tailored CV bullets."""
    return await job_service.analyze_job_description(request.description)
