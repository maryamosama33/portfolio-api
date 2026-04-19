from celery import Celery
import os
from celery.schedules import crontab

celery_app = Celery(
    "portfolio",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=["app.tasks"]
)
#celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery_app.conf.beat_schedule = {
    "fetch-jobs-every-2-hours": {
        "task": "app.tasks.job_matcher.fetch_jobs",
        "schedule": crontab(minute=0, hour="*/2"),
    },
}