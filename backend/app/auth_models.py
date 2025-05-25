"""Authentication models for the miniature tracker application."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    oauth_provider: Optional[str] = Field(None, description="OAuth provider (google, facebook)")
    oauth_id: Optional[str] = Field(None, description="OAuth provider user ID")


class UserCreate(UserBase):
    """Model for creating a new user."""
    
    password: Optional[str] = Field(None, min_length=8, description="Password (required for non-OAuth users)")
    
    def model_post_init(self, __context) -> None:
        """Validate that either password or OAuth is provided."""
        if not self.oauth_provider and not self.password:
            raise ValueError("Password is required for non-OAuth users")
        if self.oauth_provider and self.password:
            raise ValueError("Password should not be provided for OAuth users")


class UserUpdate(BaseModel):
    """Model for updating user information."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class User(UserBase):
    """User model for API responses."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserInDB(User):
    """User model for database storage."""
    
    hashed_password: Optional[str] = Field(None, description="Hashed password (null for OAuth users)")


class LoginRequest(BaseModel):
    """Model for login request."""
    
    email: EmailStr
    password: str


class OAuthUserInfo(BaseModel):
    """Model for OAuth user information."""
    
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str
    provider_id: str


class Token(BaseModel):
    """Token model."""
    
    access_token: str
    token_type: str = "bearer" 