"""Authentication routes."""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth_dependencies import get_current_active_user, get_user_db
from app.auth_models import User, UserCreate, LoginRequest, Token
from app.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.user_crud import UserDB

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate,
    user_db: UserDB = Depends(get_user_db)
) -> User:
    """Register a new user."""
    try:
        user = user_db.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login_user(
    login_request: LoginRequest,
    user_db: UserDB = Depends(get_user_db)
) -> Token:
    """Login user and return access token."""
    user = user_db.authenticate_user(login_request.email, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_db: UserDB = Depends(get_user_db)
) -> Token:
    """OAuth2 compatible login endpoint (using username as email)."""
    user = user_db.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user information."""
    return current_user


@router.get("/users", response_model=List[User])
def get_all_users(
    current_user: User = Depends(get_current_active_user),
    user_db: UserDB = Depends(get_user_db)
) -> List[User]:
    """Get all users (for admin/testing purposes)."""
    return user_db.get_all_users() 