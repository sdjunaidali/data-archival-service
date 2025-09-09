from fastapi import FastAPI
from app.api.auth_routes import router as auth_router
from app.api.config_routes import router as config_router
from app.api.archival_routes import router as archival_router
from app.db.connection import Base, source_engine, archive_engine

app = FastAPI(title="Fortinet Data Archival Service")

# Ensure tables exist for dev. In production, rely on Alembic migrations.
Base.metadata.create_all(bind=source_engine)
Base.metadata.create_all(bind=archive_engine)

app.include_router(auth_router)
app.include_router(config_router)
app.include_router(archival_router)