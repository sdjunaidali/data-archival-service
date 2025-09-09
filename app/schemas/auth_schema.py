from typing import Annotated, List, Optional
from pydantic import BaseModel, StringConstraints

Username = Annotated[str, StringConstraints(min_length=2)]
Password = Annotated[str, StringConstraints(min_length=6)]

class UserCreate(BaseModel):
    username: Username
    password: Password
    #role: str
    #permissions: Optional[List[str]] = None

class UserLogin(BaseModel):
    username: Username
    password: Password

class Token(BaseModel):
    access_token: str
    token_type: str