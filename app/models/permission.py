from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.connection import Base

class UserTablePermission(Base):
    __tablename__ = "user_table_permissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    table_name = Column(String(255), nullable=False)