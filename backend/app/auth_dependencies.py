"""Authentication dependencies for FastAPI."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth_models import User
from app.auth_utils import verify_token
from app.user_crud import UserDB

# HTTP Bearer token scheme
security = HTTPBearer()


def get_user_db() -> UserDB:
    """Dependency to get user database instance."""
    return UserDB()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_db: UserDB = Depends(get_user_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    token_data = verify_token(credentials.credentials)
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    # Get user from database - use async method directly
    user = await user_db._get_user_by_id_async(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (checks if user is active)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_user_id(
    current_user: User = Depends(get_current_active_user)
) -> UUID:
    """Get current user ID from authenticated user."""
    return current_user.id 