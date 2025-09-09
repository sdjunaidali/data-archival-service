from fastapi import APIRouter, HTTPException
from app.schemas.auth_schema import UserCreate, UserLogin, Token
from app.core.security import create_user_account, authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
def signup(u: UserCreate):
    # force role to "user", ignore any role passed from client
    #u.role = "user"
    if not create_user_account(u):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "User created"}

@router.post("/login", response_model=Token)
def login(u: UserLogin):
    user = authenticate_user(u.username, u.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer"}