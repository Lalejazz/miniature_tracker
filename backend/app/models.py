"""Data models for the miniature tracker application."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class PaintingStatus(str, Enum):
    """Enum for miniature painting status progression."""
    
    WANT_TO_BUY = "want_to_buy"
    PURCHASED = "purchased"
    ASSEMBLED = "assembled"
    PRIMED = "primed"
    GAME_READY = "game_ready"
    PARADE_READY = "parade_ready"


class StatusLogEntry(BaseModel):
    """Model for status change log entry."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    from_status: Optional[PaintingStatus] = None  # None for initial status
    to_status: PaintingStatus
    date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = Field(None, max_length=500)
    is_manual: bool = False  # True if manually added, False if automatic
    created_at: datetime = Field(default_factory=datetime.now)


class StatusLogEntryCreate(BaseModel):
    """Model for creating a new status log entry."""
    
    from_status: Optional[PaintingStatus] = None
    to_status: PaintingStatus
    date: datetime
    notes: Optional[str] = Field(None, max_length=500)
    is_manual: bool = True


class StatusLogEntryUpdate(BaseModel):
    """Model for updating a status log entry."""
    
    date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class PasswordResetToken(BaseModel):
    """Model for password reset token."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    token: str = Field(default_factory=lambda: uuid4().hex)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class PasswordResetRequest(BaseModel):
    """Model for requesting a password reset."""
    
    email: EmailStr


class PasswordReset(BaseModel):
    """Model for resetting password with token."""
    
    token: str
    new_password: str = Field(..., min_length=8)


class MiniatureBase(BaseModel):
    """Base model for miniature data."""
    
    name: str = Field(..., min_length=1, max_length=200)
    faction: str = Field(..., min_length=1, max_length=100)
    model_type: str = Field(..., min_length=1, max_length=100)
    status: PaintingStatus = PaintingStatus.WANT_TO_BUY
    notes: Optional[str] = Field(None, max_length=1000)


class MiniatureCreate(MiniatureBase):
    """Model for creating a new miniature."""
    pass


class MiniatureUpdate(BaseModel):
    """Model for updating an existing miniature."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    faction: Optional[str] = Field(None, min_length=1, max_length=100)
    model_type: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[PaintingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)


class Miniature(MiniatureBase):
    """Complete miniature model with metadata."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # Owner of this miniature
    status_history: List[StatusLogEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 