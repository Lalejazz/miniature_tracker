"""Tests for data models."""

import pytest
from datetime import datetime
from uuid import UUID

from app.models import Miniature, MiniatureCreate, MiniatureUpdate, PaintingStatus


class TestPaintingStatus:
    """Test cases for PaintingStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """Test that all expected painting statuses are defined."""
        expected_statuses = [
            "want_to_buy",
            "purchased", 
            "assembled",
            "primed",
            "game_ready",
            "parade_ready"
        ]
        
        actual_statuses = [status.value for status in PaintingStatus]
        assert actual_statuses == expected_statuses


class TestMiniatureCreate:
    """Test cases for MiniatureCreate model."""

    def test_create_valid_miniature(self) -> None:
        """Test creating a valid miniature."""
        miniature_data = {
            "name": "Space Marine Captain",
            "faction": "Ultramarines",
            "model_type": "Character",
        }
        
        miniature = MiniatureCreate(**miniature_data)
        
        assert miniature.name == "Space Marine Captain"
        assert miniature.faction == "Ultramarines"
        assert miniature.model_type == "Character"
        assert miniature.status == PaintingStatus.WANT_TO_BUY
        assert miniature.notes is None

    def test_create_with_all_fields(self) -> None:
        """Test creating miniature with all optional fields."""
        miniature_data = {
            "name": "Ork Warboss",
            "faction": "Orks",
            "model_type": "HQ",
            "status": PaintingStatus.ASSEMBLED,
            "notes": "Need to add more dakka"
        }
        
        miniature = MiniatureCreate(**miniature_data)
        
        assert miniature.status == PaintingStatus.ASSEMBLED
        assert miniature.notes == "Need to add more dakka"

    def test_name_validation(self) -> None:
        """Test name field validation."""
        # Empty name should fail
        with pytest.raises(ValueError):
            MiniatureCreate(name="", faction="Test", model_type="Test")
        
        # Too long name should fail
        with pytest.raises(ValueError):
            MiniatureCreate(
                name="x" * 201, 
                faction="Test", 
                model_type="Test"
            )

    def test_required_fields(self) -> None:
        """Test that required fields are enforced."""
        with pytest.raises(ValueError):
            MiniatureCreate(faction="Test", model_type="Test")  # Missing name


class TestMiniatureUpdate:
    """Test cases for MiniatureUpdate model."""

    def test_update_all_fields_optional(self) -> None:
        """Test that all fields are optional for updates."""
        update = MiniatureUpdate()
        
        assert update.name is None
        assert update.faction is None
        assert update.model_type is None
        assert update.status is None
        assert update.notes is None

    def test_partial_update(self) -> None:
        """Test updating only some fields."""
        update = MiniatureUpdate(
            status=PaintingStatus.PRIMED,
            notes="Applied grey primer"
        )
        
        assert update.status == PaintingStatus.PRIMED
        assert update.notes == "Applied grey primer"
        assert update.name is None


class TestMiniature:
    """Test cases for complete Miniature model."""

    def test_create_complete_miniature(self) -> None:
        """Test creating a complete miniature with metadata."""
        miniature_data = {
            "name": "Tactical Squad",
            "faction": "Space Marines",
            "model_type": "Troops"
        }
        
        miniature = Miniature(**miniature_data)
        
        assert isinstance(miniature.id, UUID)
        assert isinstance(miniature.created_at, datetime)
        assert isinstance(miniature.updated_at, datetime)
        assert miniature.name == "Tactical Squad"

    def test_auto_generated_fields(self) -> None:
        """Test that UUID and timestamps are auto-generated."""
        miniature1 = Miniature(
            name="Test1", 
            faction="Test", 
            model_type="Test"
        )
        miniature2 = Miniature(
            name="Test2", 
            faction="Test", 
            model_type="Test"
        )
        
        # Each miniature should have unique ID
        assert miniature1.id != miniature2.id
        
        # Timestamps should be close but might be different
        time_diff = abs(
            (miniature1.created_at - miniature2.created_at).total_seconds()
        )
        assert time_diff < 1.0  # Less than 1 second difference 