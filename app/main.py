from fastapi import FastAPI, Response, status
from sqlalchemy import text
from app.api.auth_routes import router as auth_router
from app.api.config_routes import router as config_router
from app.api.archival_routes import router as archival_router
from app.db.connection import Base, dispose_engines, source_engine, archive_engine

app = FastAPI(title="Fortinet Data Archival Service")

# Ensure tables exist for dev. In production, rely on Alembic migrations.
Base.metadata.create_all(bind=source_engine)
Base.metadata.create_all(bind=archive_engine)

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}

@app.get("/ready", tags=["system"])
def ready():
    try:
        with source_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        with archive_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return Response(
            content='{"status":"not-ready"}',
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

app.include_router(auth_router)
app.include_router(config_router)
app.include_router(archival_router)

@app.on_event("shutdown")
def on_shutdown():
    dispose_engines()