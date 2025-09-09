from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Path
from datetime import datetime, timedelta
from app.db.connection import get_source_session
from app.models.user import User
from app.models.permission import UserTablePermission
from app.core.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALG = "HS256"

def create_user_account(user_create):
    db = get_source_session()
    if db.query(User).filter(User.username == user_create.username).first():
        db.close()
        return False
    u = User(username=user_create.username, 
             password_hash=pwd.hash(user_create.password),
             role="user",  # enforce regular user
    )
    db.add(u); db.commit(); db.refresh(u)
    #if user_create.role == "user" and user_create.permissions:
    #    for t in user_create.permissions:
    #        db.add(UserTablePermission(user_id=u.id, table_name=t))
    #    db.commit()
    db.close()
    return True

def authenticate_user(username, password):
    db = get_source_session()
    u = db.query(User).filter(User.username == username).first()
    db.close()
    if not u or not pwd.verify(password, u.password_hash):
        return None
    return u

def create_access_token(user):
    db = get_source_session()
    try:
        if user.role == "user":
            # Option A: scalars() returns list[str] directly (SQLAlchemy 1.4/2.x)
            perms_rows = (
                db.query(UserTablePermission.table_name)
                  .filter(UserTablePermission.user_id == user.id)
                  .all()
            )
            perms = [row[0] for row in perms_rows]
        else:
            perms = []  # admins don’t need explicit table list in token
    finally:
        db.close()

    payload = {
        "sub": str(user.username),        # ensure str
        "role": str(user.role),
        "permissions": list(perms),       # ensure list[str]
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALG)

#def create_access_token(user):
#    db = get_source_session()
#    perms = []
#    if user.role == "user":
#        perms = [t for t in db.query(UserTablePermission.table_name).filter(UserTablePermission.user_id == user.id).all()]
#    db.close()
#    payload = {"sub": user.username, "role": user.role, "permissions": perms, "exp": datetime.utcnow() + timedelta(hours=8)}
#    return jwt.encode(payload, settings.secret_key, algorithm=ALG)

def get_current_active_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALG])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def is_admin_or_table_access(user, table_name: str):
    if user["role"] == "admin":
        return True
    if table_name in user.get("permissions", []):
        return True
    raise HTTPException(status_code=403, detail="Forbidden")

def require_admin(user=Depends(get_current_active_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

def require_table_access_factory():
    def dep(table_name: str = Path(...), user=Depends(get_current_active_user)):
        if user.get("role") == "admin":
            return
        if table_name not in set(user.get("permissions", [])):
            raise HTTPException(status_code=403, detail="Forbidden")
    return dep