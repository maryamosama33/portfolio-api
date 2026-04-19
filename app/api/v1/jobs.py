from fastapi import APIRouter, HTTPException
from app.tasks.job_matcher import fetch_jobs
from app.services.job_service import JobService
from pydantic import BaseModel

router = APIRouter(prefix="/jobs")


class JobSearchResponse(BaseModel):
    task_id: str
    message: str


@router.post("/match", response_model=JobSearchResponse)
async def match_jobs():
    task = fetch_jobs.delay()
    return {
        "task_id": task.id,
        "message": "Job search started. Use task_id to check progress.",
    }


@router.get("/search-status/{task_id}")
async def get_search_status(task_id: str):
    from app.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.successful() else None,
    }


@router.get("/recent")
async def get_recent_jobs(limit: int = 20):
    jobs = await JobService.get_recent_jobs(limit=limit)
    return {
        "count": len(jobs),
        "jobs": jobs,
    }


@router.post("/search-now")
async def search_jobs_now():
    result = await JobService.fetch_and_match_jobs()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("")
async def list_jobs(limit: int = 50):
    from app.repositories.job_repository import JobRepository
    
    jobs = await JobRepository.find_recent_jobs(limit=limit)
    return {
        "count": len(jobs),
        "jobs": [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "url": job.url,
                "matched_skills": job.matched_skills,
                "search_query": job.search_query,
                "created_at": job.created_at,
            }
            for job in jobs
        ],
    }
