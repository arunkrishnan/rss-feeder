from celery import Celery
from datetime import timedelta

from app.core.config import settings

beat_schedule = {
    "feed_refresh_job": {
        "task": "app.scheduler.tasks.refresh_all_feed",
        "schedule": timedelta(minutes=settings.FEED_REFRESH_INTERVAL),
    },
}


def create_celery_app():
    celery_app = Celery(
        "tasks",
        broker=settings.CELERY_BROKER_URL,
        backend=f"db+{settings.SQLALCHEMY_DATABASE_URI}",
    )
    celery_app.conf.beat_schedule = beat_schedule
    celery_app.conf.task_routes = {"app.workers.scheduler.refresh_feed": "job1"}
    celery_app.conf.task_default_queue = "job1"
    return celery_app


celery_app = create_celery_app()
