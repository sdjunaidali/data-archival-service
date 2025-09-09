from fastapi import APIRouter, Depends
from app.core.archival import fetch_archived_data
from app.core.security import get_current_active_user, is_admin_or_table_access
from app.schemas.archival_schema import ArchiveRecord

router = APIRouter(prefix="/archives", tags=["archives"])

@router.get("/{table_name}", response_model=list[ArchiveRecord])
def get_archives(table_name: str, user=Depends(get_current_active_user)):
    is_admin_or_table_access(user, table_name)
    return fetch_archived_data(table_name)