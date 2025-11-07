from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None
    role: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    role: str
    balance: float
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
