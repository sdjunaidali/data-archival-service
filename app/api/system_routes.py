from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.scheduler import get_job_summaries, get_scheduler, test_job_callable
import uuid

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/scheduler/jobs")
def list_jobs():
    try:
        return {"jobs": get_job_summaries()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "list_jobs_failed", "detail": str(e)})

@router.post("/scheduler/test")
def trigger_test_job():
    try:
        sch = get_scheduler()
        if not sch:
            return JSONResponse(status_code=503, content={"scheduled": False, "detail": "scheduler not running"})
        job_id = f"test_{uuid.uuid4().hex[:8]}"
        # Top-level callable is serializable with SQLAlchemyJobStore
        sch.add_job(test_job_callable, id=job_id, replace_existing=False)
        return {"scheduled": True, "job_id": job_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"scheduled": False, "error": "schedule_failed", "detail": str(e)})