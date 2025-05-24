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


# Player Discovery Models

class GameType(str, Enum):
    """Types of games players are interested in."""
    COMPETITIVE = "competitive"
    NARRATIVE = "narrative"
    BOTH = "both"


class Game(BaseModel):
    """Model for a wargame/tabletop game."""
    
    model_config = ConfigDict(
        json_encoders={
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class UserPreferencesCreate(BaseModel):
    """Model for creating user preferences."""
    
    games: List[UUID] = Field(description="List of game IDs the user plays")
    postcode: str = Field(min_length=3, max_length=20, description="User's postcode")
    game_types: List[GameType] = Field(description="Types of games user is interested in")
    bio: str = Field(max_length=160, description="Short bio about the user")


class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences."""
    
    games: Optional[List[UUID]] = None
    postcode: Optional[str] = Field(None, min_length=3, max_length=20)
    game_types: Optional[List[GameType]] = None
    bio: Optional[str] = Field(None, max_length=160)


class UserPreferences(BaseModel):
    """Model for user preferences."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    games: List[UUID] = Field(description="List of game IDs the user plays")
    postcode: str = Field(description="User's postcode")
    game_types: List[GameType] = Field(description="Types of games user is interested in")
    bio: str = Field(description="Short bio about the user")
    latitude: Optional[float] = Field(None, description="Calculated latitude from postcode")
    longitude: Optional[float] = Field(None, description="Calculated longitude from postcode")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PlayerSearchRequest(BaseModel):
    """Model for player search request."""
    
    games: Optional[List[UUID]] = Field(None, description="Filter by specific games")
    game_types: Optional[List[GameType]] = Field(None, description="Filter by game types")
    max_distance_km: int = Field(default=50, ge=1, le=500, description="Maximum distance in kilometers")


class PlayerSearchResult(BaseModel):
    """Model for player search result."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    user_id: UUID
    username: str
    games: List[Game] = Field(description="Games the player plays")
    game_types: List[GameType] = Field(description="Types of games player is interested in")
    bio: str
    distance_km: float = Field(description="Distance from searcher in kilometers")
    postcode: str = Field(description="Player's postcode (for privacy, might be partial)") 