from app.celery_app import celery_app
from app.services.job_service import JobService
import asyncio

from app.core.database import init_db


@celery_app.task
def fetch_jobs():
    async def runner():
        await init_db() 
        return await JobService.fetch_and_match_jobs()

    return asyncio.run(runner())