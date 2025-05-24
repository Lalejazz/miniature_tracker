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


class MiniatureDB:
    """Simple JSON file-based database for miniatures."""
    
    def __init__(self, db_file: str = "data/miniatures.json", reset_tokens_file: str = "data/reset_tokens.json") -> None:
        """Initialize the database with JSON file paths."""
        self.db_file = Path(db_file)
        self.reset_tokens_file = Path(reset_tokens_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.reset_tokens_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.db_file.exists():
            self._save_data([])
        if not self.reset_tokens_file.exists():
            self._save_reset_tokens([])
    
    def _load_data(self) -> List[dict]:
        """Load miniatures data from JSON file."""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[dict]) -> None:
        """Save miniatures data to JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
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
    
    def get_all_miniatures(self, user_id: UUID) -> List[Miniature]:
        """Get all miniatures for a user."""
        data = self._load_data()
        user_miniatures = [
            item for item in data 
            if item.get('user_id') == str(user_id)
        ]
        return [Miniature.model_validate(item) for item in user_miniatures]
    
    def get_miniature(self, miniature_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Get a specific miniature by ID for a user."""
        data = self._load_data()
        for item in data:
            if (item.get('id') == str(miniature_id) and 
                item.get('user_id') == str(user_id)):
                return Miniature.model_validate(item)
        return None
    
    def create_miniature(self, miniature: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature."""
        data = self._load_data()
        
        # Create new miniature with initial status log entry
        new_miniature = Miniature(
            **miniature.model_dump(),
            user_id=user_id,
            status_history=[
                StatusLogEntry(
                    to_status=miniature.status,
                    is_manual=False
                )
            ]
        )
        
        data.append(new_miniature.model_dump())
        self._save_data(data)
        return new_miniature
    
    def update_miniature(self, miniature_id: UUID, updates: MiniatureUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update an existing miniature."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if (item.get('id') == str(miniature_id) and 
                item.get('user_id') == str(user_id)):
                
                # Load current miniature
                current = Miniature.model_validate(item)
                
                # Prepare update data
                update_data = updates.model_dump(exclude_unset=True)
                if not update_data:
                    return current
                
                # Check if status is changing
                old_status = current.status
                new_status = update_data.get('status', old_status)
                
                # Update the miniature
                updated_data = current.model_dump()
                updated_data.update(update_data)
                updated_data['updated_at'] = datetime.now().isoformat()
                
                # Add status log entry if status changed
                if old_status != new_status:
                    status_history = updated_data.get('status_history', [])
                    status_history.append(
                        StatusLogEntry(
                            from_status=old_status,
                            to_status=new_status,
                            is_manual=False
                        ).model_dump()
                    )
                    updated_data['status_history'] = status_history
                
                data[i] = updated_data
                self._save_data(data)
                return Miniature.model_validate(updated_data)
        
        return None
    
    def delete_miniature(self, miniature_id: UUID, user_id: UUID) -> bool:
        """Delete a miniature."""
        data = self._load_data()
        original_length = len(data)
        
        data = [
            item for item in data 
            if not (item.get('id') == str(miniature_id) and 
                   item.get('user_id') == str(user_id))
        ]
        
        if len(data) < original_length:
            self._save_data(data)
            return True
        return False
    
    def add_status_log_entry(self, miniature_id: UUID, log_entry: StatusLogEntryCreate, user_id: UUID) -> Optional[Miniature]:
        """Add a manual status log entry to a miniature."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if (item.get('id') == str(miniature_id) and 
                item.get('user_id') == str(user_id)):
                
                current = Miniature.model_validate(item)
                
                # Create new log entry
                new_entry = StatusLogEntry(**log_entry.model_dump())
                
                # Add to status history
                updated_data = current.model_dump()
                status_history = updated_data.get('status_history', [])
                status_history.append(new_entry.model_dump())
                updated_data['status_history'] = status_history
                updated_data['updated_at'] = datetime.now().isoformat()
                
                # Update current status if this is the latest entry
                updated_data['status'] = log_entry.to_status
                
                data[i] = updated_data
                self._save_data(data)
                return Miniature.model_validate(updated_data)
        
        return None
    
    def update_status_log_entry(self, miniature_id: UUID, log_entry_id: UUID, updates: StatusLogEntryUpdate, user_id: UUID) -> Optional[Miniature]:
        """Update a status log entry."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if (item.get('id') == str(miniature_id) and 
                item.get('user_id') == str(user_id)):
                
                current = Miniature.model_validate(item)
                updated_data = current.model_dump()
                status_history = updated_data.get('status_history', [])
                
                # Find and update the log entry
                for j, log_entry in enumerate(status_history):
                    if log_entry.get('id') == str(log_entry_id):
                        update_data = updates.model_dump(exclude_unset=True)
                        if update_data:
                            status_history[j].update(update_data)
                            updated_data['status_history'] = status_history
                            updated_data['updated_at'] = datetime.now().isoformat()
                            
                            data[i] = updated_data
                            self._save_data(data)
                            return Miniature.model_validate(updated_data)
                break
        
        return None
    
    def delete_status_log_entry(self, miniature_id: UUID, log_entry_id: UUID, user_id: UUID) -> Optional[Miniature]:
        """Delete a status log entry."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if (item.get('id') == str(miniature_id) and 
                item.get('user_id') == str(user_id)):
                
                current = Miniature.model_validate(item)
                updated_data = current.model_dump()
                status_history = updated_data.get('status_history', [])
                
                # Remove the log entry
                original_length = len(status_history)
                status_history = [
                    entry for entry in status_history 
                    if entry.get('id') != str(log_entry_id)
                ]
                
                if len(status_history) < original_length:
                    updated_data['status_history'] = status_history
                    updated_data['updated_at'] = datetime.now().isoformat()
                    
                    data[i] = updated_data
                    self._save_data(data)
                    return Miniature.model_validate(updated_data)
                break
        
        return None
    
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