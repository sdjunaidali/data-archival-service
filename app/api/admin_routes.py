# app/api/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.core.security import require_admin
from app.db.connection import get_source_session
from app.models.user import User
from app.models.permission import UserTablePermission

router = APIRouter(prefix="/admin", tags=["admin"])

class PermissionUpdate(BaseModel):
    username: str = Field(..., min_length=2)
    add: List[str] = []
    remove: List[str] = []

@router.post("/permissions", dependencies=[Depends(require_admin)])
def update_permissions(payload: PermissionUpdate, db=Depends(get_source_session)):
    username = payload.username.lower().strip()
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    # Add permissions
    for t in payload.add:
        exists = (
            db.query(UserTablePermission)
              .filter(UserTablePermission.user_id == u.id, UserTablePermission.table_name == t)
              .first()
        )
        if not exists:
            db.add(UserTablePermission(user_id=u.id, table_name=t))

    # Remove permissions
    if payload.remove:
        (db.query(UserTablePermission)
           .filter(UserTablePermission.user_id == u.id, UserTablePermission.table_name.in_(payload.remove))
           .delete(synchronize_session=False))

    db.commit()
    return {"status": "ok"}