from pydantic import BaseModel

class ArchiveRecord(BaseModel):
    data: str
    archived_at: str