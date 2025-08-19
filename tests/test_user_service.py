from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bson import ObjectId

from app.schemas.user import UserRole
from app.services.user_service import (get_user_by_id, get_user_role,
                                       is_user_admin, register_user)


class TestUserService:
    """Test cases for user service functions."""

    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID."""
        return str(ObjectId())

    @pytest.fixture
    def mock_user_data(self):
        """Mock user data."""
        return {
            "_id": ObjectId(),
            "email": "test@example.com",
            "hashed_password": "hashed_password_123",
            "createdAt": datetime.utcnow(),
            "role": "admin",
        }

    @pytest.fixture
    def sample_user_credentials(self):
        """Sample user credentials for testing."""
        return {
            "email": "test@example.com",
            "password": "secure_password",
            "role": UserRole.ADMIN,
        }

    @pytest.mark.asyncio
    async def test_register_user_success(self, sample_user_credentials):
        """Test successful user registration."""
        mock_user_id = ObjectId()

        with patch(
            "app.services.user_service.get_user_collection"
        ) as mock_get_collection, patch(
            "app.services.user_service.hash_password", return_value="hashed_password"
        ), patch(
            "app.database.create_user", return_value=mock_user_id
        ):
            mock_collection = Mock()
            mock_get_collection.return_value = mock_collection

            result = await register_user(
                sample_user_credentials["email"],
                sample_user_credentials["password"],
                sample_user_credentials["role"].value,
            )

        assert result == mock_user_id

    @pytest.mark.asyncio
    async def test_register_user_failure(self, sample_user_credentials):
        """Test user registration failure."""
        with patch(
            "app.services.user_service.get_user_collection"
        ) as mock_get_collection, patch(
            "app.services.user_service.hash_password", return_value="hashed_password"
        ), patch(
            "app.database.create_user", return_value=None
        ):
            mock_collection = Mock()
            mock_get_collection.return_value = mock_collection

            with pytest.raises(Exception, match="Failed to create user"):
                await register_user(
                    sample_user_credentials["email"],
                    sample_user_credentials["password"],
                    sample_user_credentials["role"].value,
                )

    @pytest.mark.asyncio
    async def test_register_user_default_role(self, sample_user_credentials):
        """Test user registration with default role."""
        mock_user_id = ObjectId()

        with patch(
            "app.services.user_service.get_user_collection"
        ) as mock_get_collection, patch(
            "app.services.user_service.hash_password", return_value="hashed_password"
        ), patch(
            "app.database.create_user", return_value=mock_user_id
        ):
            mock_collection = Mock()
            mock_get_collection.return_value = mock_collection

            result = await register_user(
                sample_user_credentials["email"], sample_user_credentials["password"]
            )

        assert result == mock_user_id

    @pytest.mark.asyncio
    async def test_is_user_admin_true(self, mock_user_id):
        """Test admin role check when user is admin."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "admin@example.com",
            "role": "admin",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await is_user_admin(mock_user_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_admin_false(self, mock_user_id):
        """Test admin role check when user is not admin."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "user@example.com",
            "role": "user",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await is_user_admin(mock_user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_admin_user_not_found(self, mock_user_id):
        """Test admin role check when user doesn't exist."""
        with patch("app.database.get_user_by_id", return_value=None):
            result = await is_user_admin(mock_user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_admin_no_role_field(self, mock_user_id):
        """Test admin role check when user has no role field."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "user@example.com",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await is_user_admin(mock_user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_role_success(self, mock_user_id):
        """Test successful user role retrieval."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "admin@example.com",
            "role": "admin",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await get_user_role(mock_user_id)

        assert result == "admin"

    @pytest.mark.asyncio
    async def test_get_user_role_user_not_found(self, mock_user_id):
        """Test user role retrieval when user doesn't exist."""
        with patch("app.database.get_user_by_id", return_value=None):
            result = await get_user_role(mock_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_role_no_role_field(self, mock_user_id):
        """Test user role retrieval when user has no role field."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "user@example.com",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await get_user_role(mock_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_user_id):
        """Test successful user retrieval by ID."""
        mock_user_data = {
            "_id": ObjectId(mock_user_id),
            "email": "test@example.com",
            "role": "admin",
            "createdAt": datetime.utcnow(),
        }

        with patch("app.database.get_user_by_id", return_value=mock_user_data):
            result = await get_user_by_id(mock_user_id)

        assert result == mock_user_data

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_user_id):
        """Test user retrieval when user doesn't exist."""
        with patch("app.database.get_user_by_id", return_value=None):
            result = await get_user_by_id(mock_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_role_enum_values(self):
        """Test UserRole enum values."""
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"

    @pytest.mark.asyncio
    async def test_admin_role_edge_cases(self, mock_user_id):
        """Test admin role check edge cases."""
        # Test with different role values
        test_cases = [
            {"role": "ADMIN", "expected": False},  # Case sensitive
            {"role": "Admin", "expected": False},  # Case sensitive
            {"role": "user", "expected": False},  # Regular user
            {"role": "", "expected": False},  # Empty string
            {"role": None, "expected": False},  # None value
        ]

        for test_case in test_cases:
            mock_user_data = {
                "_id": ObjectId(mock_user_id),
                "email": "test@example.com",
                "role": test_case["role"],
                "createdAt": datetime.utcnow(),
            }

            with patch("app.database.get_user_by_id", return_value=mock_user_data):
                result = await is_user_admin(mock_user_id)

            assert (
                result == test_case["expected"]
            ), f"Failed for role: {test_case['role']}"

    @pytest.mark.asyncio
    async def test_user_registration_validation(self):
        """Test user registration input validation."""
        # Test with invalid email
        with pytest.raises(Exception):
            await register_user("invalid_email", "password", "user")

        # Test with empty password
        with pytest.raises(Exception):
            await register_user("test@example.com", "", "user")

        # Test with None password
        with pytest.raises(Exception):
            await register_user("test@example.com", None, "user")

    @pytest.mark.asyncio
    async def test_password_hashing_integration(self, sample_user_credentials):
        """Test password hashing integration."""
        mock_user_id = ObjectId()

        with patch(
            "app.services.user_service.get_user_collection"
        ) as mock_get_collection, patch(
            "app.services.user_service.hash_password"
        ) as mock_hash, patch(
            "app.database.create_user", return_value=mock_user_id
        ):
            mock_collection = Mock()
            mock_get_collection.return_value = mock_collection
            mock_hash.return_value = "hashed_password_123"

            await register_user(
                sample_user_credentials["email"],
                sample_user_credentials["password"],
                sample_user_credentials["role"].value,
            )

            # Verify password was hashed
            mock_hash.assert_called_once_with(sample_user_credentials["password"])


if __name__ == "__main__":
    pytest.main([__file__])
