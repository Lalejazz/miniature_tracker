"""Data models for the miniature tracker application."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class PaintingStatus(str, Enum):
    """Enum for miniature painting status progression."""
    
    WANT_TO_BUY = "want_to_buy"
    PURCHASED = "purchased"
    ASSEMBLED = "assembled"
    PRIMED = "primed"
    GAME_READY = "game_ready"
    PARADE_READY = "parade_ready"


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
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 