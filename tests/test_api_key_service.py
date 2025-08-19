import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bson import ObjectId

from app.services.api_key_service import (deactivate_api_key, delete_api_key,
                                          generate_api_key,
                                          get_api_key_by_id, list_api_keys,
                                          update_api_key, verify_api_key)


class TestAPIKeyService:
    """Test cases for API key service functions."""

    @pytest.fixture
    def mock_collection(self):
        """Mock MongoDB collection for testing."""
        collection = Mock()
        collection.insert_one = AsyncMock()
        collection.find_one = AsyncMock()
        collection.find = AsyncMock()
        collection.update_one = AsyncMock()
        collection.delete_one = AsyncMock()
        return collection

    @pytest.fixture
    def sample_key_data(self):
        """Sample API key data for testing."""
        return {
            "name": "Test API Key",
            "scopes": ["read", "write"],
            "expires_in_days": 30,
        }

    @pytest.mark.asyncio
    async def test_generate_api_key_success(self, mock_collection, sample_key_data):
        """Test successful API key generation."""
        # Mock the collection
        mock_collection.insert_one.return_value.inserted_id = ObjectId()

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await generate_api_key(
                sample_key_data["name"],
                sample_key_data["scopes"],
                sample_key_data["expires_in_days"],
            )

        # Verify the result structure
        assert "key_id" in result
        assert "api_key" in result
        assert result["name"] == sample_key_data["name"]
        assert result["scopes"] == sample_key_data["scopes"]
        assert result["is_active"] is True
        assert result["api_key"].startswith("ak_")

        # Verify database was called
        mock_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_api_key_no_expiration(
        self, mock_collection, sample_key_data
    ):
        """Test API key generation without expiration."""
        mock_collection.insert_one.return_value.inserted_id = ObjectId()

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await generate_api_key(
                sample_key_data["name"], sample_key_data["scopes"]
            )

        assert result["expires_at"] is None
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_verify_api_key_success(self, mock_collection):
        """Test successful API key verification."""
        # Mock API key data
        mock_key_data = {
            "_id": ObjectId(),
            "name": "Test Key",
            "scopes": ["read", "write"],
            "is_active": True,
            "expires_at": None,
            "created_at": datetime.utcnow(),
        }

        mock_collection.find_one.return_value = mock_key_data
        mock_collection.update_one.return_value.modified_count = 1

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await verify_api_key("ak_test123")

        assert result["name"] == "Test Key"
        assert result["scopes"] == ["read", "write"]
        assert (
            result["is_admin"] is False
        )  # This field doesn't exist in the actual response

    @pytest.mark.asyncio
    async def test_verify_api_key_invalid_format(self, mock_collection):
        """Test API key verification with invalid format."""
        with pytest.raises(Exception, match="Invalid API key format"):
            await verify_api_key("invalid_key")

    @pytest.mark.asyncio
    async def test_verify_api_key_not_found(self, mock_collection):
        """Test API key verification when key doesn't exist."""
        mock_collection.find_one.return_value = None

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            with pytest.raises(Exception, match="Invalid API key"):
                await verify_api_key("ak_test123")

    @pytest.mark.asyncio
    async def test_verify_api_key_inactive(self, mock_collection):
        """Test API key verification when key is inactive."""
        mock_key_data = {
            "_id": ObjectId(),
            "name": "Test Key",
            "scopes": ["read"],
            "is_active": False,
            "expires_at": None,
            "created_at": datetime.utcnow(),
        }

        mock_collection.find_one.return_value = mock_key_data

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            with pytest.raises(Exception, match="API key is inactive"):
                await verify_api_key("ak_test123")

    @pytest.mark.asyncio
    async def test_verify_api_key_expired(self, mock_collection):
        """Test API key verification when key is expired."""
        expired_time = datetime.utcnow() - timedelta(days=1)
        mock_key_data = {
            "_id": ObjectId(),
            "name": "Test Key",
            "scopes": ["read"],
            "is_active": True,
            "expires_at": expired_time,
            "created_at": datetime.utcnow(),
        }

        mock_collection.find_one.return_value = mock_key_data

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            with pytest.raises(Exception, match="API key expired"):
                await verify_api_key("ak_test123")

    @pytest.mark.asyncio
    async def test_get_api_key_by_id_success(self, mock_collection):
        """Test successful API key retrieval by ID."""
        key_id = str(ObjectId())
        mock_key_data = {
            "_id": ObjectId(key_id),
            "name": "Test Key",
            "scopes": ["read"],
            "created_at": datetime.utcnow(),
            "expires_at": None,
            "is_active": True,
            "last_used": None,
        }

        mock_collection.find_one.return_value = mock_key_data

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await get_api_key_by_id(key_id)

        assert result["name"] == "Test Key"
        assert result["scopes"] == ["read"]
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_api_key_by_id_not_found(self, mock_collection):
        """Test API key retrieval when ID doesn't exist."""
        key_id = str(ObjectId())
        mock_collection.find_one.return_value = None

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await get_api_key_by_id(key_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_list_api_keys_success(self, mock_collection):
        """Test successful API key listing."""
        mock_keys = [
            {
                "_id": ObjectId(),
                "name": "Key 1",
                "scopes": ["read"],
                "created_at": datetime.utcnow(),
                "expires_at": None,
                "is_active": True,
                "last_used": None,
            },
            {
                "_id": ObjectId(),
                "name": "Key 2",
                "scopes": ["read", "write"],
                "created_at": datetime.utcnow(),
                "expires_at": None,
                "is_active": False,
                "last_used": None,
            },
        ]

        mock_cursor = Mock()
        mock_cursor.__aiter__ = Mock(return_value=iter(mock_keys))
        mock_collection.find.return_value = mock_cursor

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await list_api_keys()

        assert len(result) == 2
        assert result[0]["name"] == "Key 1"
        assert result[1]["name"] == "Key 2"

    @pytest.mark.asyncio
    async def test_update_api_key_success(self, mock_collection):
        """Test successful API key update."""
        key_id = str(ObjectId())
        updates = {"name": "Updated Key", "scopes": ["read", "write"]}

        mock_collection.update_one.return_value.modified_count = 1

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await update_api_key(key_id, updates)

        assert result is True
        mock_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_api_key_no_changes(self, mock_collection):
        """Test API key update when no changes are made."""
        key_id = str(ObjectId())
        updates = {"name": "Updated Key"}

        mock_collection.update_one.return_value.modified_count = 0

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await update_api_key(key_id, updates)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_api_key_invalid_fields(self, mock_collection):
        """Test API key update with invalid fields."""
        key_id = str(ObjectId())
        updates = {"invalid_field": "value", "name": "Valid Update"}

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await update_api_key(key_id, updates)

        # Should only update valid fields
        assert result is True
        # Verify only valid fields were passed to update
        call_args = mock_collection.update_one.call_args
        update_data = call_args[0][1]["$set"]
        assert "invalid_field" not in update_data
        assert "name" in update_data

    @pytest.mark.asyncio
    async def test_deactivate_api_key(self, mock_collection):
        """Test API key deactivation."""
        key_id = str(ObjectId())

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await deactivate_api_key(key_id)

        # This should call update_api_key with is_active: False
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_api_key_success(self, mock_collection):
        """Test successful API key deletion."""
        key_id = str(ObjectId())
        mock_collection.delete_one.return_value.deleted_count = 1

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await delete_api_key(key_id)

        assert result is True
        mock_collection.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_api_key_not_found(self, mock_collection):
        """Test API key deletion when key doesn't exist."""
        key_id = str(ObjectId())
        mock_collection.delete_one.return_value.deleted_count = 0

        with patch(
            "app.services.api_key_service.get_api_key_collection",
            return_value=mock_collection,
        ):
            result = await delete_api_key(key_id)

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
