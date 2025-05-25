"""Authentication routes."""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth_dependencies import get_current_active_user, get_user_db
from app.auth_models import User, UserCreate, LoginRequest, Token, EmailVerificationRequest, EmailVerificationConfirm
from app.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.user_crud import UserDB
from app.models import PasswordResetRequest, PasswordReset
from app.email_service import email_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    user_db: UserDB = Depends(get_user_db)
) -> dict:
    """Register a new user and send email verification."""
    try:
        # Create user (email not verified yet)
        user = await user_db.create_user(user_create)
        
        # Create email verification token
        verification_token = user_db.create_email_verification_token(user.id)
        
        # Send verification email
        email_sent = await email_service.send_email_verification_email(
            user.email, 
            user.username,
            verification_token.token
        )
        
        if not email_sent:
            # Log error but don't fail registration
            print(f"Failed to send verification email to {user.email}")
        
        return {
            "message": "Registration successful! Please check your email to verify your account.",
            "user_id": str(user.id),
            "email_sent": email_sent
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification: EmailVerificationConfirm,
    user_db: UserDB = Depends(get_user_db)
) -> dict:
    """Verify user's email address with token."""
    # Get verification token
    token_data = user_db.get_email_verification_token(verification.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Mark user's email as verified
    success = await user_db.verify_user_email(token_data.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )
    
    # Mark token as used
    user_db.use_email_verification_token(verification.token)
    
    return {"message": "Email verified successfully! You can now log in."}


@router.post("/resend-verification", response_model=dict)
async def resend_verification_email(
    request: EmailVerificationRequest,
    user_db: UserDB = Depends(get_user_db)
) -> dict:
    """Resend email verification email."""
    # Get user by email
    user = await user_db.get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If an account with that email exists and is not verified, a verification email has been sent."}
    
    # Check if already verified
    if user.is_email_verified:
        return {"message": "Email is already verified."}
    
    # Create new verification token
    verification_token = user_db.create_email_verification_token(user.id)
    
    # Send verification email
    email_sent = await email_service.send_email_verification_email(
        user.email, 
        user.username,
        verification_token.token
    )
    
    if not email_sent:
        print(f"Failed to resend verification email to {user.email}")
    
    return {"message": "If an account with that email exists and is not verified, a verification email has been sent."}


@router.post("/login", response_model=Token)
async def login_user(
    credentials: LoginRequest,
    user_db: UserDB = Depends(get_user_db)
) -> Token:
    """Login user and return access token."""
    user = await user_db.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email address before logging in. Check your email for a verification link.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_db: UserDB = Depends(get_user_db)
) -> Token:
    """OAuth2 compatible token endpoint."""
    user = await user_db.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email address before logging in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user information."""
    return current_user


@router.get("/users", response_model=List[User])
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
    user_db: UserDB = Depends(get_user_db)
) -> List[User]:
    """Get all users (admin endpoint)."""
    return await user_db.get_all_users()


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    user_db: UserDB = Depends(get_user_db)
) -> dict:
    """Request a password reset email."""
    # Always return success to prevent email enumeration
    # but only send email if user exists
    user = await user_db.get_user_by_email(request.email)
    
    if user:
        # Create password reset token
        reset_token = user_db.create_password_reset_token(user.id)
        
        # Send password reset email
        email_sent = await email_service.send_password_reset_email(
            request.email, 
            reset_token.token
        )
        
        if not email_sent:
            # Log error but don't expose it to user
            print(f"Failed to send password reset email to {request.email}")
    
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    request: PasswordReset,
    user_db: UserDB = Depends(get_user_db)
) -> dict:
    """Reset password using token."""
    # Validate token
    token_data = user_db.get_password_reset_token(request.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    success = await user_db.update_user_password(token_data.user_id, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    # Mark token as used
    user_db.use_password_reset_token(request.token)
    
    return {"message": "Password has been reset successfully"} 