from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

celery_app = Celery(
    "portfolio",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.job_matcher"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=60 * 60 * 24,
    beat_schedule={
        "search-and-match-jobs-every-2-hours": {
            "task": "app.tasks.job_matcher.search_and_match_jobs",
            "schedule": crontab(minute=0, hour="*/2"),
        },
    },
)
