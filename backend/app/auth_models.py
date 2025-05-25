"""Authentication models for the miniature tracker application."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_email_verified: bool = False
    oauth_provider: Optional[str] = Field(None, description="OAuth provider (google, facebook)")
    oauth_id: Optional[str] = Field(None, description="OAuth provider user ID")


class UserCreate(UserBase):
    """Model for creating a new user."""
    
    password: Optional[str] = Field(None, min_length=8, description="Password (required for non-OAuth users)")
    accept_terms: bool = Field(..., description="User must accept terms and conditions")
    
    def model_post_init(self, __context) -> None:
        """Validate that either password or OAuth is provided."""
        if not self.oauth_provider and not self.password:
            raise ValueError("Password is required for non-OAuth users")
        if self.oauth_provider and self.password:
            raise ValueError("Password should not be provided for OAuth users")
        if not self.accept_terms:
            raise ValueError("You must accept the terms and conditions to register")


class UserUpdate(BaseModel):
    """Model for updating user information."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None


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


class TokenData(BaseModel):
    """Token data model for JWT payload."""
    
    user_id: UUID
    username: Optional[str] = None


class EmailVerificationToken(BaseModel):
    """Email verification token model."""
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    token: str = Field(default_factory=lambda: uuid4().hex)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class EmailVerificationRequest(BaseModel):
    """Request to resend email verification."""
    
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Confirm email verification with token."""
    
    token: str