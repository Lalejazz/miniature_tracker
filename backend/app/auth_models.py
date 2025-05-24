"""User authentication models."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None


class User(UserBase):
    """User model with all fields."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data for validation."""
    user_id: Optional[UUID] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str 