from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.admin import router, verify_admin_token
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate
from app.schemas.user import UserCreate

# Create a test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAdminRouter:
    """Test cases for admin router endpoints."""

    @pytest.fixture
    def mock_admin_token(self):
        """Mock admin JWT token."""
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_admin_token"

    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID."""
        return str(ObjectId())

    @pytest.fixture
    def sample_api_key_data(self):
        """Sample API key creation data."""
        return {
            "name": "Test API Key",
            "scopes": ["read", "write"],
            "expires_in_days": 30,
        }

    @pytest.fixture
    def sample_user_data(self):
        """Sample user creation data."""
        return {
            "email": "test@example.com",
            "password": "secure_password",
            "role": "user",
        }

    @pytest.mark.asyncio
    async def test_verify_admin_token_success(self, mock_user_id):
        """Test successful admin token verification."""
        with patch(
            "app.services.user_service.decode_access_token", return_value=mock_user_id
        ), patch("app.services.user_service.is_user_admin", return_value=True):
            result = await verify_admin_token(mock_user_id)
            assert result == mock_user_id

    @pytest.mark.asyncio
    async def test_verify_admin_token_not_admin(self, mock_user_id):
        """Test admin token verification when user is not admin."""
        with patch(
            "app.services.user_service.decode_access_token", return_value=mock_user_id
        ), patch("app.services.user_service.is_user_admin", return_value=False):
            with pytest.raises(Exception, match="Admin access required"):
                await verify_admin_token(mock_user_id)

    def test_create_api_key_success(self, mock_admin_token, sample_api_key_data):
        """Test successful API key creation."""
        mock_response = {
            "key_id": str(ObjectId()),
            "name": sample_api_key_data["name"],
            "api_key": "ak_test123",
            "scopes": sample_api_key_data["scopes"],
            "expires_at": None,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }

        with patch(
            "app.services.api_key_service.generate_api_key", return_value=mock_response
        ):
            response = client.post(
                "/admin/api-keys",
                json=sample_api_key_data,
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_api_key_data["name"]
        assert data["api_key"].startswith("ak_")

    def test_create_api_key_unauthorized(self, sample_api_key_data):
        """Test API key creation without authorization."""
        response = client.post("/admin/api-keys", json=sample_api_key_data)

        assert response.status_code == 401

    def test_list_api_keys_success(self, mock_admin_token):
        """Test successful API key listing."""
        mock_keys = [
            {
                "key_id": str(ObjectId()),
                "name": "Key 1",
                "scopes": ["read"],
                "created_at": datetime.utcnow(),
                "expires_at": None,
                "is_active": True,
                "last_used": None,
            }
        ]

        with patch(
            "app.services.api_key_service.list_api_keys", return_value=mock_keys
        ):
            response = client.get(
                "/admin/api-keys",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "api_keys" in data
        assert len(data["api_keys"]) == 1

    def test_get_api_key_info_success(self, mock_admin_token):
        """Test successful API key info retrieval."""
        key_id = str(ObjectId())
        mock_key_info = {
            "key_id": key_id,
            "name": "Test Key",
            "scopes": ["read"],
            "created_at": datetime.utcnow(),
            "expires_at": None,
            "is_active": True,
            "last_used": None,
        }

        with patch(
            "app.services.api_key_service.get_api_key_by_id", return_value=mock_key_info
        ):
            response = client.get(
                f"/admin/api-keys/{key_id}",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Key"

    def test_get_api_key_info_not_found(self, mock_admin_token):
        """Test API key info retrieval when key doesn't exist."""
        key_id = str(ObjectId())

        with patch("app.services.api_key_service.get_api_key_by_id", return_value=None):
            response = client.get(
                f"/admin/api-keys/{key_id}",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 404

    def test_update_api_key_success(self, mock_admin_token):
        """Test successful API key update."""
        key_id = str(ObjectId())
        updates = APIKeyUpdate(name="Updated Key", scopes=["read", "write"])

        with patch("app.services.api_key_service.update_api_key", return_value=True):
            response = client.put(
                f"/admin/api-keys/{key_id}",
                json=updates.dict(exclude_none=True),
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API key updated successfully"

    def test_update_api_key_no_changes(self, mock_admin_token):
        """Test API key update when no changes are made."""
        key_id = str(ObjectId())
        updates = APIKeyUpdate(name="Updated Key")

        with patch("app.services.api_key_service.update_api_key", return_value=False):
            response = client.put(
                f"/admin/api-keys/{key_id}",
                json=updates.dict(exclude_none=True),
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 404

    def test_deactivate_api_key_success(self, mock_admin_token):
        """Test successful API key deactivation."""
        key_id = str(ObjectId())

        with patch(
            "app.services.api_key_service.deactivate_api_key", return_value=True
        ):
            response = client.patch(
                f"/admin/api-keys/{key_id}/deactivate",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API key deactivated successfully"

    def test_deactivate_api_key_not_found(self, mock_admin_token):
        """Test API key deactivation when key doesn't exist."""
        key_id = str(ObjectId())

        with patch(
            "app.services.api_key_service.deactivate_api_key", return_value=False
        ):
            response = client.patch(
                f"/admin/api-keys/{key_id}/deactivate",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 404

    def test_delete_api_key_success(self, mock_admin_token):
        """Test successful API key deletion."""
        key_id = str(ObjectId())

        with patch("app.services.api_key_service.delete_api_key", return_value=True):
            response = client.delete(
                f"/admin/api-keys/{key_id}",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API key deleted successfully"

    def test_delete_api_key_not_found(self, mock_admin_token):
        """Test API key deletion when key doesn't exist."""
        key_id = str(ObjectId())

        with patch("app.services.api_key_service.delete_api_key", return_value=False):
            response = client.delete(
                f"/admin/api-keys/{key_id}",
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 404

    def test_create_user_admin_success(self, mock_admin_token, sample_user_data):
        """Test successful user creation by admin."""
        mock_user_id = str(ObjectId())

        with patch(
            "app.services.user_service.register_user", return_value=mock_user_id
        ):
            response = client.post(
                "/admin/users",
                json=sample_user_data,
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user_id"] == mock_user_id

    def test_create_user_admin_failure(self, mock_admin_token, sample_user_data):
        """Test user creation failure."""
        with patch(
            "app.services.user_service.register_user",
            side_effect=Exception("User creation failed"),
        ):
            response = client.post(
                "/admin/users",
                json=sample_user_data,
                headers={"Authorization": f"Bearer {mock_admin_token}"},
            )

        assert response.status_code == 500
        data = response.json()
        assert "Failed to create user" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__])
