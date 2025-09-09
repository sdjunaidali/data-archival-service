from sqlalchemy import Column, Integer, String, Text
from app.db.connection import Base

class ArchivalConfig(Base):
    __tablename__ = "archival_config"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), unique=True, nullable=False)
    archive_after_days = Column(Integer, nullable=False)
    delete_after_days = Column(Integer, nullable=False)
    custom_criteria = Column(Text, nullable=True)