"""Tests for FastAPI endpoints."""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db
from app.crud import MiniatureDB
from app.models import PaintingStatus


class TestMiniatureAPI:
    """Test cases for miniature API endpoints."""

    @pytest.fixture
    def temp_db_file(self) -> Path:
        """Create a temporary database file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('[]')  # Initialize with empty array
        temp_file.close()
        return Path(temp_file.name)

    @pytest.fixture
    def client(self, temp_db_file: Path) -> TestClient:
        """Create test client with temporary database."""
        def override_get_db() -> MiniatureDB:
            return MiniatureDB(str(temp_db_file))
        
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_create_miniature(self, client: TestClient) -> None:
        """Test creating a new miniature via API."""
        miniature_data = {
            "name": "Space Marine Captain",
            "faction": "Ultramarines",
            "model_type": "Character",
            "status": "want_to_buy"
        }
        
        response = client.post("/miniatures", json=miniature_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Space Marine Captain"
        assert data["faction"] == "Ultramarines"
        assert data["status"] == "want_to_buy"
        assert "id" in data
        assert "created_at" in data

    def test_create_miniature_minimal_data(self, client: TestClient) -> None:
        """Test creating miniature with minimal required fields."""
        miniature_data = {
            "name": "Ork Boy",
            "faction": "Orks",
            "model_type": "Troops"
        }
        
        response = client.post("/miniatures", json=miniature_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "want_to_buy"  # Default status

    def test_create_miniature_validation_error(self, client: TestClient) -> None:
        """Test validation errors when creating miniature."""
        # Missing required field
        invalid_data = {
            "faction": "Space Marines",
            "model_type": "Character"
            # Missing name
        }
        
        response = client.post("/miniatures", json=invalid_data)
        assert response.status_code == 422

    def test_get_all_miniatures_empty(self, client: TestClient) -> None:
        """Test getting all miniatures when database is empty."""
        response = client.get("/miniatures")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_miniatures_with_data(self, client: TestClient) -> None:
        """Test getting all miniatures with existing data."""
        # Create test data
        test_miniatures = [
            {
                "name": "Space Marine",
                "faction": "Ultramarines",
                "model_type": "Troops"
            },
            {
                "name": "Ork Warboss",
                "faction": "Orks",
                "model_type": "HQ"
            }
        ]
        
        created_ids = []
        for miniature_data in test_miniatures:
            response = client.post("/miniatures", json=miniature_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Get all miniatures
        response = client.get("/miniatures")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert all(item["id"] in created_ids for item in data)

    def test_get_miniature_by_id(self, client: TestClient) -> None:
        """Test getting a specific miniature by ID."""
        # Create a miniature first
        miniature_data = {
            "name": "Test Marine",
            "faction": "Space Marines",
            "model_type": "Troops"
        }
        
        create_response = client.post("/miniatures", json=miniature_data)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # Get the miniature by ID
        response = client.get(f"/miniatures/{created_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_id
        assert data["name"] == "Test Marine"

    def test_get_nonexistent_miniature(self, client: TestClient) -> None:
        """Test getting a miniature that doesn't exist."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/miniatures/{fake_id}")
        assert response.status_code == 404

    def test_update_miniature(self, client: TestClient) -> None:
        """Test updating an existing miniature."""
        # Create a miniature first
        miniature_data = {
            "name": "Test Marine",
            "faction": "Space Marines",
            "model_type": "Troops"
        }
        
        create_response = client.post("/miniatures", json=miniature_data)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # Update the miniature
        update_data = {
            "status": "assembled",
            "notes": "Assembled and ready for priming"
        }
        
        response = client.put(f"/miniatures/{created_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "assembled"
        assert data["notes"] == "Assembled and ready for priming"
        assert data["name"] == "Test Marine"  # Unchanged

    def test_update_nonexistent_miniature(self, client: TestClient) -> None:
        """Test updating a miniature that doesn't exist."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        update_data = {"status": "assembled"}
        
        response = client.put(f"/miniatures/{fake_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_miniature(self, client: TestClient) -> None:
        """Test deleting a miniature."""
        # Create a miniature first
        miniature_data = {
            "name": "Test Marine",
            "faction": "Space Marines",
            "model_type": "Troops"
        }
        
        create_response = client.post("/miniatures", json=miniature_data)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # Delete the miniature
        response = client.delete(f"/miniatures/{created_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/miniatures/{created_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_miniature(self, client: TestClient) -> None:
        """Test deleting a miniature that doesn't exist."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.delete(f"/miniatures/{fake_id}")
        assert response.status_code == 404

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "miniature" in data["message"].lower() 