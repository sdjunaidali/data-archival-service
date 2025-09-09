from pydantic import BaseModel
from typing import Optional

class ConfigRequest(BaseModel):
    table_name: str
    archive_after_days: int
    delete_after_days: int
    custom_criteria: Optional[str] = None

class ConfigResponse(ConfigRequest):
    id: int
    class Config:
        from_attributes = True