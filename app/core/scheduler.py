from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES
from app.core.archival import archive_and_delete_job, purge_expired_archives
from app.core.settings import settings

_scheduler: AsyncIOScheduler | None = None

def _on_job_event(event):
    job_id = getattr(event, "job_id", "?")
    print(f"[APScheduler] event={event.code} job={job_id}")

def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler

    jobstores = {"default": SQLAlchemyJobStore(url=str(settings.archive_database_url))}
    executors = {"default": ThreadPoolExecutor(max_workers=4)}
    job_defaults = {
        "coalesce": True,
        "max_instances": 1,          # prevent overlapping archival runs
        "misfire_grace_time": 300,   # seconds
    }

    sch = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone="UTC",
    )

    # Dispatcher-like tick every 5 minutes
    sch.add_job(
        archive_and_delete_job,
        IntervalTrigger(minutes=5),
        id="archival_tick",
        replace_existing=True,
    )

    # Purge daily at 02:00 UTC
    sch.add_job(
        purge_expired_archives,
        CronTrigger(hour=2, minute=0),
        id="purge_daily",
        replace_existing=True,
    )

    sch.add_listener(_on_job_event, EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES)
    sch.start()
    print("[APScheduler] started with jobs:", [j.id for j in sch.get_jobs()])
    _scheduler = sch
    return sch

def test_job_callable():
    from datetime import datetime
    print(f"[APScheduler] test job fired at {datetime.utcnow().isoformat()}")

def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        
def get_scheduler():
    return _scheduler

def get_job_summaries():
    sch = get_scheduler()
    if not sch:
        return []
    result = []
    for job in sch.get_jobs():
        result.append({
            "id": job.id,
            "name": job.name,
            "trigger": str(job.trigger),
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "func": f"{job.func.__module__}.{job.func.__name__}",
        })
    return result