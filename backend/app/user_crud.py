"""User CRUD operations."""

import json
import os
import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.auth_models import User, UserCreate, UserInDB, UserUpdate
from app.auth_utils import get_password_hash, verify_password
from app.models import PasswordResetToken
from app.database import get_database


class UserDB:
    """User database operations using the database abstraction layer."""
    
    def __init__(self, reset_tokens_file: str = "data/reset_tokens.json"):
        """Initialize user database."""
        self.db = get_database()
        self.reset_tokens_file = os.path.join(os.path.dirname(__file__), "..", reset_tokens_file)
        self._ensure_reset_tokens_file()
    
    def _ensure_reset_tokens_file(self) -> None:
        """Ensure the reset tokens file exists."""
        os.makedirs(os.path.dirname(self.reset_tokens_file), exist_ok=True)
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, 'w') as f:
                json.dump([], f)
    
    async def _ensure_db_initialized(self):
        """Ensure database is initialized."""
        await self.db.initialize()
    
    def _load_reset_tokens(self) -> List[dict]:
        """Load password reset tokens from JSON file."""
        try:
            with open(self.reset_tokens_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_reset_tokens(self, tokens: List[dict]) -> None:
        """Save password reset tokens to JSON file."""
        with open(self.reset_tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2, default=str)
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        return asyncio.run(self._get_user_by_email_async(email))
    
    async def _get_user_by_email_async(self, email: str) -> Optional[UserInDB]:
        """Get user by email (async version)."""
        await self._ensure_db_initialized()
        return await self.db.get_user_by_email(email)
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return asyncio.run(self._get_user_by_id_async(user_id))
    
    async def _get_user_by_id_async(self, user_id: UUID) -> Optional[User]:
        """Get user by ID (async version)."""
        await self._ensure_db_initialized()
        return await self.db.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username."""
        return asyncio.run(self._get_user_by_username_async(username))
    
    async def _get_user_by_username_async(self, username: str) -> Optional[UserInDB]:
        """Get user by username (async version)."""
        await self._ensure_db_initialized()
        users = await self.db.get_all_users()
        for user in users:
            user_in_db = await self.db.get_user_by_email(user.email)
            if user_in_db and user_in_db.username == username:
                return user_in_db
        return None
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        return asyncio.run(self._create_user_async(user_create))
    
    async def _create_user_async(self, user_create: UserCreate) -> User:
        """Create a new user (async version)."""
        await self._ensure_db_initialized()
        return await self.db.create_user(user_create)
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        return asyncio.run(self._update_user_async(user_id, user_update))
    
    async def _update_user_async(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update an existing user (async version)."""
        await self._ensure_db_initialized()
        return await self.db.update_user(user_id, user_update)
    
    def update_user_password(self, user_id: UUID, new_password: str) -> bool:
        """Update user's password."""
        user_update = UserUpdate(hashed_password=get_password_hash(new_password))
        result = self.update_user(user_id, user_update)
        return result is not None
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin function)."""
        return asyncio.run(self._get_all_users_async())
    
    async def _get_all_users_async(self) -> List[User]:
        """Get all users (async version)."""
        await self._ensure_db_initialized()
        return await self.db.get_all_users()
    
    # Password Reset Token Methods
    
    def create_password_reset_token(self, user_id: UUID) -> PasswordResetToken:
        """Create a new password reset token."""
        tokens = self._load_reset_tokens()
        
        # Invalidate any existing tokens for this user
        for token_data in tokens:
            if token_data.get('user_id') == str(user_id):
                token_data['used'] = True
        
        # Create new token
        new_token = PasswordResetToken(user_id=user_id)
        tokens.append(new_token.model_dump())
        self._save_reset_tokens(tokens)
        
        return new_token
    
    def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get a password reset token by token string."""
        tokens = self._load_reset_tokens()
        
        for token_data in tokens:
            if token_data.get('token') == token:
                reset_token = PasswordResetToken.model_validate(token_data)
                
                # Check if token is valid (not used and not expired)
                if not reset_token.used and reset_token.expires_at > datetime.now():
                    return reset_token
                break
        
        return None
    
    def use_password_reset_token(self, token: str) -> bool:
        """Mark a password reset token as used."""
        tokens = self._load_reset_tokens()
        
        for token_data in tokens:
            if token_data.get('token') == token:
                token_data['used'] = True
                self._save_reset_tokens(tokens)
                return True
        
        return False
    
    def cleanup_expired_tokens(self) -> None:
        """Remove expired password reset tokens."""
        tokens = self._load_reset_tokens()
        current_time = datetime.now()
        
        # Filter out expired tokens
        valid_tokens = [
            token for token in tokens
            if datetime.fromisoformat(token.get('expires_at', '1900-01-01T00:00:00')) > current_time
        ]
        
        if len(valid_tokens) != len(tokens):
            self._save_reset_tokens(valid_tokens) 