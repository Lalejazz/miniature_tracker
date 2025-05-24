"""User CRUD operations."""

import json
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.auth_models import User, UserCreate, UserInDB, UserUpdate
from app.auth_utils import get_password_hash, verify_password


class UserDB:
    """User database operations using JSON file storage."""
    
    def __init__(self, data_file: str = "data/users.json"):
        """Initialize user database."""
        self.data_file = os.path.join(os.path.dirname(__file__), "..", data_file)
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """Ensure the data file and directory exist."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
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
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin function)."""
        users = self._load_users()
        user_list = []
        for user_data in users:
            user_dict = user_data.copy()
            user_dict.pop("hashed_password", None)  # Don't return passwords
            user_list.append(User(**user_dict))
        return user_list 