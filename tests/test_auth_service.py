from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth_service import (get_current_user_or_api_key,
                                       require_any_auth, require_api_key_auth,
                                       require_user_auth)


class TestAuthService:
    """Test cases for authentication service functions."""

    @pytest.fixture
    def mock_jwt_token(self):
        """Mock JWT token."""
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_jwt_token"

    @pytest.fixture
    def mock_api_key(self):
        """Mock API key."""
        return "ak_test123456789"

    @pytest.fixture
    def mock_credentials(self):
        """Mock HTTP authorization credentials."""
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        return credentials

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_jwt_success(
        self, mock_credentials, mock_jwt_token
    ):
        """Test successful JWT token authentication."""
        mock_credentials.credentials = mock_jwt_token

        with patch(
            "app.services.user_service.decode_access_token", return_value="user123"
        ):
            result = await get_current_user_or_api_key(mock_credentials)

        assert result["type"] == "user"
        assert result["id"] == "user123"

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_api_key_success(
        self, mock_credentials, mock_api_key
    ):
        """Test successful API key authentication."""
        mock_credentials.credentials = mock_api_key

        mock_key_info = {
            "key_id": "key123",
            "name": "Test Key",
            "scopes": ["read", "write"],
            "created_at": "2023-01-01T00:00:00",
            "expires_at": None,
        }

        with patch(
            "app.services.api_key_service.verify_api_key", return_value=mock_key_info
        ):
            result = await get_current_user_or_api_key(mock_credentials)

        assert result["type"] == "api_key"
        assert result["info"] == mock_key_info

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_jwt_failure_api_key_success(
        self, mock_credentials, mock_jwt_token
    ):
        """Test JWT failure but API key success."""
        mock_credentials.credentials = mock_jwt_token

        mock_key_info = {
            "key_id": "key123",
            "name": "Test Key",
            "scopes": ["read"],
            "created_at": "2023-01-01T00:00:00",
            "expires_at": None,
        }

        with patch(
            "app.services.user_service.decode_access_token",
            side_effect=Exception("Invalid JWT"),
        ), patch(
            "app.services.api_key_service.verify_api_key", return_value=mock_key_info
        ):
            result = await get_current_user_or_api_key(mock_credentials)

        assert result["type"] == "api_key"
        assert result["info"] == mock_key_info

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_both_failure(
        self, mock_credentials, mock_jwt_token
    ):
        """Test both JWT and API key authentication failure."""
        mock_credentials.credentials = mock_jwt_token

        with patch(
            "app.services.user_service.decode_access_token",
            side_effect=Exception("Invalid JWT"),
        ), patch(
            "app.services.api_key_service.verify_api_key",
            side_effect=Exception("Invalid API key"),
        ):
            with pytest.raises(
                HTTPException, match="Invalid authentication token or API key"
            ):
                await get_current_user_or_api_key(mock_credentials)

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_no_credentials(self):
        """Test authentication with no credentials."""
        with pytest.raises(HTTPException, match="Authentication required"):
            await get_current_user_or_api_key(None)

    @pytest.mark.asyncio
    async def test_get_current_user_or_api_key_invalid_format(self, mock_credentials):
        """Test authentication with invalid token format."""
        mock_credentials.credentials = "invalid_token_format"

        with patch(
            "app.services.user_service.decode_access_token",
            side_effect=Exception("Invalid JWT"),
        ), patch(
            "app.services.api_key_service.verify_api_key",
            side_effect=Exception("Invalid API key"),
        ):
            with pytest.raises(
                HTTPException, match="Invalid authentication token or API key"
            ):
                await get_current_user_or_api_key(mock_credentials)

    @pytest.mark.asyncio
    async def test_require_user_auth_success(self):
        """Test successful user authentication requirement."""
        auth_result = {"type": "user", "id": "user123"}

        result = await require_user_auth(auth_result)
        assert result == "user123"

    @pytest.mark.asyncio
    async def test_require_user_auth_api_key_failure(self):
        """Test user authentication requirement with API key (should fail)."""
        auth_result = {"type": "api_key", "info": {"key_id": "key123"}}

        with pytest.raises(HTTPException, match="User authentication required"):
            await require_user_auth(auth_result)

    @pytest.mark.asyncio
    async def test_require_user_auth_invalid_type(self):
        """Test user authentication requirement with invalid type."""
        auth_result = {"type": "invalid", "id": "user123"}

        with pytest.raises(HTTPException, match="User authentication required"):
            await require_user_auth(auth_result)

    @pytest.mark.asyncio
    async def test_require_api_key_auth_success(self):
        """Test successful API key authentication requirement."""
        auth_result = {"type": "api_key", "info": {"key_id": "key123"}}

        result = await require_api_key_auth(auth_result)
        assert result == {"key_id": "key123"}

    @pytest.mark.asyncio
    async def test_require_api_key_auth_jwt_failure(self):
        """Test API key authentication requirement with JWT (should fail)."""
        auth_result = {"type": "user", "id": "user123"}

        with pytest.raises(HTTPException, match="API key authentication required"):
            await require_api_key_auth(auth_result)

    @pytest.mark.asyncio
    async def test_require_api_key_auth_invalid_type(self):
        """Test API key authentication requirement with invalid type."""
        auth_result = {"type": "invalid", "info": {"key_id": "key123"}}

        with pytest.raises(HTTPException, match="API key authentication required"):
            await require_api_key_auth(auth_result)

    @pytest.mark.asyncio
    async def test_require_any_auth_user(self):
        """Test any authentication requirement with user."""
        auth_result = {"type": "user", "id": "user123"}

        result = await require_any_auth(auth_result)
        assert result == auth_result

    @pytest.mark.asyncio
    async def test_require_any_auth_api_key(self):
        """Test any authentication requirement with API key."""
        auth_result = {"type": "api_key", "info": {"key_id": "key123"}}

        result = await require_any_auth(auth_result)
        assert result == auth_result

    @pytest.mark.asyncio
    async def test_require_any_auth_invalid_type(self):
        """Test any authentication requirement with invalid type."""
        auth_result = {"type": "invalid", "id": "user123"}

        result = await require_any_auth(auth_result)
        assert result == auth_result

    @pytest.mark.asyncio
    async def test_api_key_verification_error_handling(
        self, mock_credentials, mock_api_key
    ):
        """Test API key verification error handling."""
        mock_credentials.credentials = mock_api_key

        with patch(
            "app.services.api_key_service.verify_api_key",
            side_effect=Exception("API key expired"),
        ):
            with pytest.raises(HTTPException, match="Invalid API key: API key expired"):
                await get_current_user_or_api_key(mock_credentials)

    @pytest.mark.asyncio
    async def test_jwt_token_edge_cases(self, mock_credentials):
        """Test JWT token edge cases."""
        # Test with token that doesn't start with "eyJ"
        mock_credentials.credentials = "not_a_jwt_token"

        mock_key_info = {"key_id": "key123"}

        with patch(
            "app.services.api_key_service.verify_api_key", return_value=mock_key_info
        ):
            result = await get_current_user_or_api_key(mock_credentials)

        assert result["type"] == "api_key"

    @pytest.mark.asyncio
    async def test_api_key_edge_cases(self, mock_credentials):
        """Test API key edge cases."""
        # Test with key that doesn't start with "ak_"
        mock_credentials.credentials = "not_an_api_key"

        with patch(
            "app.services.user_service.decode_access_token",
            side_effect=Exception("Invalid JWT"),
        ), patch(
            "app.services.api_key_service.verify_api_key",
            side_effect=Exception("Invalid API key"),
        ):
            with pytest.raises(
                HTTPException, match="Invalid authentication token or API key"
            ):
                await get_current_user_or_api_key(mock_credentials)


if __name__ == "__main__":
    pytest.main([__file__])
