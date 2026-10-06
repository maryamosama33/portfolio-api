import asyncio

from app.celery_app import celery_app
from app.core.database import init_db
from app.services.job_service import run_job_search


async def _run() -> dict:
    # The DB client is bound to the event loop it's created on, and every
    # asyncio.run() makes a new loop, so connect inside the same loop as the work.
    client = await init_db()
    try:
        summary = await run_job_search()
        return summary.model_dump()
    finally:
        await client.close()


@celery_app.task
def search_and_match_jobs() -> dict:
    return asyncio.run(_run())
