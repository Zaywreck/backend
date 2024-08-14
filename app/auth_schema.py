from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: Optional[str]  # Optional for login
    email: Optional[str] = None
    password: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    username: Optional[str] = None  # Optional for registration

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
