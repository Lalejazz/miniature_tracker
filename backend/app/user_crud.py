"""User CRUD operations."""

import json
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.auth_models import User, UserCreate, UserInDB, UserUpdate
from app.auth_utils import get_password_hash, verify_password
from app.models import PasswordResetToken


class UserDB:
    """User database operations using JSON file storage."""
    
    def __init__(self, data_file: str = "data/users.json", reset_tokens_file: str = "data/reset_tokens.json"):
        """Initialize user database."""
        self.data_file = os.path.join(os.path.dirname(__file__), "..", data_file)
        self.reset_tokens_file = os.path.join(os.path.dirname(__file__), "..", reset_tokens_file)
        self._ensure_data_files()
    
    def _ensure_data_files(self) -> None:
        """Ensure the data files and directory exist."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, 'w') as f:
                json.dump([], f)
    
    def _load_users(self) -> List[dict]:
        """Load users from JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: List[dict]) -> None:
        """Save users to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
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
        users = self._load_users()
        for user_data in users:
            if user_data.get("email") == email:
                return UserInDB(**user_data)
        return None
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("id") == str(user_id):
                # Return User (without hashed_password)
                user_dict = user_data.copy()
                user_dict.pop("hashed_password", None)
                return User(**user_dict)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("username") == username:
                return UserInDB(**user_data)
        return None
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        users = self._load_users()
        
        # Check if user already exists
        if any(u.get("email") == user_create.email for u in users):
            raise ValueError("User with this email already exists")
        
        if any(u.get("username") == user_create.username for u in users):
            raise ValueError("User with this username already exists")
        
        # Create user with hashed password
        user_in_db = UserInDB(
            **user_create.model_dump(exclude={"password"}),
            hashed_password=get_password_hash(user_create.password)
        )
        
        users.append(user_in_db.model_dump())
        self._save_users(users)
        
        # Return User (without hashed_password)
        return User(**user_in_db.model_dump(exclude={"hashed_password"}))
    
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
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                # Update fields
                update_data = user_update.model_dump(exclude_unset=True)
                if update_data:
                    user_data.update(update_data)
                    user_data["updated_at"] = datetime.utcnow().isoformat()
                    users[i] = user_data
                    self._save_users(users)
                
                # Return updated user (without hashed_password)
                user_dict = user_data.copy()
                user_dict.pop("hashed_password", None)
                return User(**user_dict)
        
        return None
    
    def update_user_password(self, user_id: UUID, new_password: str) -> bool:
        """Update user's password."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == str(user_id):
                user_data["hashed_password"] = get_password_hash(new_password)
                user_data["updated_at"] = datetime.utcnow().isoformat()
                users[i] = user_data
                self._save_users(users)
                return True
        
        return False
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin function)."""
        users = self._load_users()
        user_list = []
        for user_data in users:
            user_dict = user_data.copy()
            user_dict.pop("hashed_password", None)  # Don't return passwords
            user_list.append(User(**user_dict))
        return user_list
    
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
        
        active_tokens = [
            token for token in tokens
            if datetime.fromisoformat(token.get('expires_at', '')) > current_time
        ]
        
        if len(active_tokens) < len(tokens):
            self._save_reset_tokens(active_tokens) 