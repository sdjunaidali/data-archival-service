from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.core.settings import settings

Base = declarative_base()

source_engine = create_engine(str(settings.source_database_url), pool_pre_ping=True)
archive_engine = create_engine(str(settings.archive_database_url), pool_pre_ping=True)

SourceSession = sessionmaker(bind=source_engine, autocommit=False, autoflush=False)
ArchiveSession = sessionmaker(bind=archive_engine, autocommit=False, autoflush=False)

def get_source_session(): 
    return SourceSession()

def get_archive_session(): 
    return ArchiveSession()

def dispose_engines():
    # Call on application shutdown
    source_engine.dispose()
    archive_engine.dispose()