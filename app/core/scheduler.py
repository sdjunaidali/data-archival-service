from celery import Celery
from celery.schedules import crontab
from app.core.settings import settings
from app.core.archival import archive_and_delete_job

celery_app = Celery("archival", broker=settings.celery_broker_url)

@celery_app.task
def run_archival():
    archive_and_delete_job()

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "daily-archival-2am": {
        "task": "app.core.scheduler.run_archival",
        "schedule": crontab(hour=2, minute=0),
    }
}