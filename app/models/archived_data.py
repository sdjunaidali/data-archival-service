from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.connection import Base

class ArchivedData(Base):
    __tablename__ = "archived_data"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)
    archived_at = Column(DateTime(timezone=True), server_default=func.now())