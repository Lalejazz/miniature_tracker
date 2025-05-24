"""Tests for CRUD operations."""

import json
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from app.crud import MiniatureDB
from app.models import MiniatureCreate, PaintingStatus


class TestMiniatureDB:
    """Test cases for MiniatureDB class."""

    @pytest.fixture
    def temp_db_file(self) -> Path:
        """Create a temporary database file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('[]')  # Initialize with empty array
        temp_file.close()
        return Path(temp_file.name)

    @pytest.fixture
    def db(self, temp_db_file: Path) -> MiniatureDB:
        """Create a MiniatureDB instance with temporary file."""
        return MiniatureDB(str(temp_db_file))

    def test_create_miniature(self, db: MiniatureDB) -> None:
        """Test creating a new miniature."""
        miniature_data = MiniatureCreate(
            name="Test Marine",
            faction="Space Marines",
            model_type="Troops"
        )
        
        created = db.create(miniature_data)
        
        assert created.name == "Test Marine"
        assert created.faction == "Space Marines"
        assert created.model_type == "Troops"
        assert created.status == PaintingStatus.WANT_TO_BUY
        assert created.id is not None
        assert created.created_at is not None

    def test_get_all_miniatures_empty(self, db: MiniatureDB) -> None:
        """Test getting all miniatures from empty database."""
        miniatures = db.get_all()
        assert miniatures == []

    def test_get_all_miniatures_with_data(self, db: MiniatureDB) -> None:
        """Test getting all miniatures with data."""
        # Create test data
        miniature1 = MiniatureCreate(name="Test1", faction="Faction1", model_type="Type1")
        miniature2 = MiniatureCreate(name="Test2", faction="Faction2", model_type="Type2")
        
        created1 = db.create(miniature1)
        created2 = db.create(miniature2)
        
        all_miniatures = db.get_all()
        
        assert len(all_miniatures) == 2
        assert created1 in all_miniatures
        assert created2 in all_miniatures

    def test_get_miniature_by_id(self, db: MiniatureDB) -> None:
        """Test getting a miniature by ID."""
        miniature_data = MiniatureCreate(
            name="Test Marine",
            faction="Space Marines", 
            model_type="Troops"
        )
        
        created = db.create(miniature_data)
        retrieved = db.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name

    def test_get_nonexistent_miniature(self, db: MiniatureDB) -> None:
        """Test getting a miniature that doesn't exist."""
        fake_id = uuid4()
        result = db.get_by_id(fake_id)
        assert result is None

    def test_update_miniature(self, db: MiniatureDB) -> None:
        """Test updating an existing miniature."""
        # Create miniature
        miniature_data = MiniatureCreate(
            name="Test Marine",
            faction="Space Marines",
            model_type="Troops"
        )
        created = db.create(miniature_data)
        
        # Update it
        from app.models import MiniatureUpdate
        update_data = MiniatureUpdate(
            status=PaintingStatus.ASSEMBLED,
            notes="Assembled and ready for priming"
        )
        
        updated = db.update(created.id, update_data)
        
        assert updated is not None
        assert updated.id == created.id
        assert updated.status == PaintingStatus.ASSEMBLED
        assert updated.notes == "Assembled and ready for priming"
        assert updated.name == "Test Marine"  # Unchanged field

    def test_update_nonexistent_miniature(self, db: MiniatureDB) -> None:
        """Test updating a miniature that doesn't exist."""
        from app.models import MiniatureUpdate
        fake_id = uuid4()
        update_data = MiniatureUpdate(status=PaintingStatus.ASSEMBLED)
        
        result = db.update(fake_id, update_data)
        assert result is None

    def test_delete_miniature(self, db: MiniatureDB) -> None:
        """Test deleting a miniature."""
        # Create miniature
        miniature_data = MiniatureCreate(
            name="Test Marine",
            faction="Space Marines",
            model_type="Troops"
        )
        created = db.create(miniature_data)
        
        # Delete it
        success = db.delete(created.id)
        assert success is True
        
        # Verify it's gone
        retrieved = db.get_by_id(created.id)
        assert retrieved is None

    def test_delete_nonexistent_miniature(self, db: MiniatureDB) -> None:
        """Test deleting a miniature that doesn't exist."""
        fake_id = uuid4()
        success = db.delete(fake_id)
        assert success is False

    def test_persistence(self, temp_db_file: Path) -> None:
        """Test that data persists between database instances."""
        # Create first DB instance and add data
        db1 = MiniatureDB(str(temp_db_file))
        miniature_data = MiniatureCreate(
            name="Persistent Marine",
            faction="Space Marines",
            model_type="Troops"
        )
        created = db1.create(miniature_data)
        
        # Create second DB instance and verify data exists
        db2 = MiniatureDB(str(temp_db_file))
        retrieved = db2.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.name == "Persistent Marine" 