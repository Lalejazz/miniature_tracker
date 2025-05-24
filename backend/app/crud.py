"""CRUD operations for miniature data."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.models import (
    Miniature, MiniatureCreate, MiniatureUpdate, 
    StatusLogEntry, StatusLogEntryCreate, StatusLogEntryUpdate,
    PasswordResetToken
)
from app.database import get_database


class MiniatureDB:
    """Miniature database operations using database abstraction layer."""
    
    def __init__(self, reset_tokens_file: str = "data/reset_tokens.json") -> None:
        """Initialize the database with database abstraction layer."""
        self.db = get_database()
        # Keep reset tokens in file storage for now (can be migrated later if needed)
        self.reset_tokens_file = Path(reset_tokens_file)
        self.reset_tokens_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize reset tokens file if it doesn't exist
        if not self.reset_tokens_file.exists():
            self._save_reset_tokens([])
    
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
    
    async def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        await self._ensure_db_initialized()
        return await self.db.get_all_miniatures(user_id)
    
    async def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        await self._ensure_db_initialized()
        return await self.db.get_miniature(miniature_id, user_id)
    
    async def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        await self._ensure_db_initialized()
        return await self.db.create_miniature(miniature, user_id)
    
    async def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        await self._ensure_db_initialized()
        return await self.db.update_miniature(miniature_id, updates, user_id)
    
    async def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        await self._ensure_db_initialized()
        return await self.db.delete_miniature(miniature_id, user_id)
    
    async def add_status_log_entry(self, miniature_id: UUID, log_entry: StatusLogEntryCreate, user_id: UUID) -> Optional[Miniature]:
        """Add a manual status log entry to a miniature."""
        await self._ensure_db_initialized()
        return await self.db.add_status_log_entry(
            miniature_id, 
            log_entry.from_status, 
            log_entry.to_status, 
            log_entry.notes, 
            user_id
        )
    
    async def update_status_log_entry(self, miniature_id: UUID, log_entry_id: UUID, updates: StatusLogEntryUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update a status log entry."""
        # This method would need to be implemented in the database layer
        # For now, return None as it's not critical functionality
        return None
    
    async def delete_status_log_entry(self, miniature_id: UUID, log_entry_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Delete a status log entry."""
        # This method would need to be implemented in the database layer
        # For now, return None as it's not critical functionality
        return None
    
    # Password Reset Token Methods (kept as file storage for now)
    
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