"""CRUD operations for miniature data."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.models import Miniature, MiniatureCreate, MiniatureUpdate


class MiniatureDB:
    """Simple JSON file-based database for miniatures."""
    
    def __init__(self, db_file: str = "data/miniatures.json") -> None:
        """Initialize the database with a JSON file path."""
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.db_file.exists():
            self._save_data([])
    
    def _load_data(self) -> List[dict]:
        """Load data from JSON file."""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[dict]) -> None:
        """Save data to JSON file."""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _data_to_miniature(self, data: dict) -> Miniature:
        """Convert raw dict data to Miniature model."""
        # Convert string IDs back to UUID objects
        data['id'] = UUID(data['id'])
        
        # Handle missing user_id field for backward compatibility
        if 'user_id' not in data:
            # For old data without user_id, we'll need to skip it or assign a default
            # For now, we'll skip these records during user-filtered queries
            # You could also assign a default user_id here if needed
            return None
        
        data['user_id'] = UUID(data['user_id'])
        
        # Convert ISO string dates back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return Miniature(**data)
    
    def _miniature_to_data(self, miniature: Miniature) -> dict:
        """Convert Miniature model to dict for JSON storage."""
        data = miniature.model_dump()
        
        # Convert UUID and datetime to strings for JSON serialization
        data['id'] = str(data['id'])
        data['user_id'] = str(data['user_id'])
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    def create(self, miniature_data: MiniatureCreate, user_id: UUID) -> Miniature:
        """Create a new miniature for a specific user."""
        # Create new miniature with generated metadata and user_id
        miniature_dict = miniature_data.model_dump()
        miniature_dict['user_id'] = user_id
        new_miniature = Miniature(**miniature_dict)
        
        # Load existing data
        data: List[dict] = self._load_data()
        
        # Add new miniature
        data.append(self._miniature_to_data(new_miniature))
        
        # Save and return
        self._save_data(data)
        return new_miniature
    
    def get_all(self, user_id: Optional[UUID] = None) -> List[Miniature]:
        """Get all miniatures, optionally filtered by user."""
        data = self._load_data()
        miniatures = []
        
        for item in data:
            miniature = self._data_to_miniature(item)
            if miniature is not None:  # Skip old data without user_id
                miniatures.append(miniature)
        
        if user_id:
            miniatures = [m for m in miniatures if str(m.user_id) == str(user_id)]
        
        return miniatures
    
    def get_by_id(self, miniature_id: UUID, user_id: Optional[UUID] = None) -> Optional[Miniature]:
        """Get a miniature by ID, optionally checking user ownership."""
        data = self._load_data()
        
        for item in data:
            if item['id'] == str(miniature_id):
                miniature = self._data_to_miniature(item)
                
                # Skip if old data without user_id
                if miniature is None:
                    continue
                
                # Check user ownership if user_id provided
                if user_id and str(miniature.user_id) != str(user_id):
                    return None
                
                return miniature
        
        return None
    
    def update(self, miniature_id: UUID, update_data: MiniatureUpdate, user_id: Optional[UUID] = None) -> Optional[Miniature]:
        """Update an existing miniature, checking user ownership."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if item['id'] == str(miniature_id):
                # Convert to miniature object
                current = self._data_to_miniature(item)
                
                # Skip if old data without user_id
                if current is None:
                    continue
                
                # Check user ownership if user_id provided
                if user_id and str(current.user_id) != str(user_id):
                    return None
                
                # Apply updates (only non-None values)
                update_dict = update_data.model_dump(exclude_unset=True)
                for field, value in update_dict.items():
                    setattr(current, field, value)
                
                # Update timestamp
                current.updated_at = datetime.now()
                
                # Save back to data
                data[i] = self._miniature_to_data(current)
                self._save_data(data)
                
                return current
        
        return None
    
    def delete(self, miniature_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """Delete a miniature by ID, checking user ownership."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if item['id'] == str(miniature_id):
                # Check user ownership if user_id provided
                if user_id:
                    # Convert to miniature to check user_id
                    miniature = self._data_to_miniature(item)
                    
                    # Skip if old data without user_id
                    if miniature is None:
                        continue
                        
                    if str(miniature.user_id) != str(user_id):
                        return False
                
                data.pop(i)
                self._save_data(data)
                return True
        
        return False 