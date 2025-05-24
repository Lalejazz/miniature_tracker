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
        
        # Convert ISO string dates back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return Miniature(**data)
    
    def _miniature_to_data(self, miniature: Miniature) -> dict:
        """Convert Miniature model to dict for JSON storage."""
        data = miniature.model_dump()
        
        # Convert UUID and datetime to strings for JSON serialization
        data['id'] = str(data['id'])
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    def create(self, miniature_data: MiniatureCreate) -> Miniature:
        """Create a new miniature."""
        # Create new miniature with generated metadata
        new_miniature = Miniature(**miniature_data.model_dump())
        
        # Load existing data
        data: List[dict] = self._load_data()
        
        # Add new miniature
        data.append(self._miniature_to_data(new_miniature))
        
        # Save and return
        self._save_data(data)
        return new_miniature
    
    def get_all(self) -> List[Miniature]:
        """Get all miniatures."""
        data = self._load_data()
        return [self._data_to_miniature(item) for item in data]
    
    def get_by_id(self, miniature_id: UUID) -> Optional[Miniature]:
        """Get a miniature by ID."""
        data = self._load_data()
        
        for item in data:
            if item['id'] == str(miniature_id):
                return self._data_to_miniature(item)
        
        return None
    
    def update(self, miniature_id: UUID, update_data: MiniatureUpdate) -> Optional[Miniature]:
        """Update an existing miniature."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if item['id'] == str(miniature_id):
                # Convert to miniature object
                current = self._data_to_miniature(item)
                
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
    
    def delete(self, miniature_id: UUID) -> bool:
        """Delete a miniature by ID."""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if item['id'] == str(miniature_id):
                data.pop(i)
                self._save_data(data)
                return True
        
        return False 