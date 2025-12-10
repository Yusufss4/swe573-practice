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
    display_name: str | None = None
    description: str | None = None
    profile_image: str | None = None
    profile_image_type: str | None = None
    role: str
    balance: float
    location_lat: float | None = None
    location_lon: float | None = None
    location_name: str | None = None
    social_blog: str | None = None
    social_instagram: str | None = None
    social_facebook: str | None = None
    social_twitter: str | None = None
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    """Public user information for displaying in offers/needs."""
    id: int
    username: str
    display_name: str | None = None
    full_name: str | None = None
    profile_image: str | None = None
    profile_image_type: str | None = None
    is_suspended: bool | None = None  # For moderation responses
    is_banned: bool | None = None  # For moderation responses
    completed_exchanges: int | None = None  # Number of completed exchanges
    average_rating: float | None = None  # Average rating (0-5)
    
    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Request schema for updating user profile."""
    full_name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    profile_image: str | None = Field(None, max_length=500)
    profile_image_type: str | None = Field(None, pattern="^(preset|custom)$")
    location_lat: float | None = None
    location_lon: float | None = None
    location_name: str | None = Field(None, max_length=255)
    social_blog: str | None = Field(None, max_length=255)
    social_instagram: str | None = Field(None, max_length=100)
    social_facebook: str | None = Field(None, max_length=100)
    social_twitter: str | None = Field(None, max_length=100)
    tags: list[str] | None = None  # List of tag names


class UserTagResponse(BaseModel):
    """Response schema for user tags."""
    tag_name: str
    
    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    """Response schema for user profile with tags."""
    id: int
    email: str
    username: str
    full_name: str | None
    description: str | None
    profile_image: str | None
    profile_image_type: str
    role: str
    balance: float
    location_lat: float | None
    location_lon: float | None
    location_name: str | None
    social_blog: str | None
    social_instagram: str | None
    social_facebook: str | None
    social_twitter: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tags: list[str]
    
    model_config = {"from_attributes": True}
