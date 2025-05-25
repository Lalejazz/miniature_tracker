"""Player discovery and preferences routes."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_database, DatabaseInterface
from app.auth_dependencies import get_current_user_id
from app.models import (
    Game, UserPreferences, UserPreferencesCreate, UserPreferencesUpdate,
    PlayerSearchRequest, PlayerSearchResult
)

router = APIRouter(prefix="/player", tags=["player-discovery"])


@router.get("/games", response_model=List[Game])
async def get_games(
    db: DatabaseInterface = Depends(get_database)
) -> List[Game]:
    """Get all available games."""
    await db.initialize()
    return await db.get_all_games()


@router.post("/games", response_model=Game, status_code=status.HTTP_201_CREATED)
async def create_game(
    name: str,
    description: Optional[str] = None,
    db: DatabaseInterface = Depends(get_database),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Game:
    """Create a new game (admin functionality)."""
    await db.initialize()
    try:
        return await db.create_game(name, description)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    db: DatabaseInterface = Depends(get_database),
    current_user_id: UUID = Depends(get_current_user_id)
) -> UserPreferences:
    """Get current user's preferences."""
    await db.initialize()
    preferences = await db.get_user_preferences(current_user_id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    return preferences


@router.post("/preferences", response_model=UserPreferences, status_code=status.HTTP_201_CREATED)
async def create_user_preferences(
    preferences: UserPreferencesCreate,
    db: DatabaseInterface = Depends(get_database),
    current_user_id: UUID = Depends(get_current_user_id)
) -> UserPreferences:
    """Create user preferences."""
    await db.initialize()
    try:
        return await db.create_user_preferences(current_user_id, preferences)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    updates: UserPreferencesUpdate,
    db: DatabaseInterface = Depends(get_database),
    current_user_id: UUID = Depends(get_current_user_id)
) -> UserPreferences:
    """Update user preferences."""
    await db.initialize()
    updated_preferences = await db.update_user_preferences(current_user_id, updates)
    if not updated_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    return updated_preferences


@router.post("/search", response_model=List[PlayerSearchResult])
async def search_players(
    search_request: PlayerSearchRequest,
    db: DatabaseInterface = Depends(get_database),
    current_user_id: UUID = Depends(get_current_user_id)
) -> List[PlayerSearchResult]:
    """Search for players near you."""
    await db.initialize()
    return await db.search_players(search_request, current_user_id) 