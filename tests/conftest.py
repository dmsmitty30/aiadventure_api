import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_api_key_collection, get_user_collection
# Import your app components
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI application."""
    return TestClient(test_app)


@pytest.fixture
def mock_user_id():
    """Generate a mock user ID."""
    return str(ObjectId())


@pytest.fixture
def mock_adventure_id():
    """Generate a mock adventure ID."""
    return str(ObjectId())


@pytest.fixture
def mock_api_key_id():
    """Generate a mock API key ID."""
    return str(ObjectId())


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "secure_password_123",
        "role": "user",
        "createdAt": datetime.utcnow(),
    }


@pytest.fixture
def sample_admin_user_data():
    """Sample admin user data for testing."""
    return {
        "email": "admin@example.com",
        "password": "admin_password_123",
        "role": "admin",
        "createdAt": datetime.utcnow(),
    }


@pytest.fixture
def sample_api_key_data():
    """Sample API key data for testing."""
    return {"name": "Test API Key", "scopes": ["read", "write"], "expires_in_days": 30}


@pytest.fixture
def sample_adventure_data():
    """Sample adventure data for testing."""
    return {
        "owner_id": str(ObjectId()),
        "title": "Test Adventure",
        "synopsis": "A test adventure for unit testing",
        "userPrompt": "Create a test adventure",
        "createdAt": datetime.utcnow(),
        "perspective": "Second Person",
        "max_levels": 5,
        "min_words_per_level": 100,
        "max_words_per_level": 200,
        "nodes": [],
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_jwt_token"


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "ak_test123456789"


@pytest.fixture
def mock_mongo_collection():
    """Mock MongoDB collection for testing."""
    collection = Mock()
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()
    return collection


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing."""
    s3_client = Mock()
    s3_client.upload_fileobj = AsyncMock()
    s3_client.generate_presigned_url = AsyncMock(
        return_value="https://example.com/presigned-url"
    )
    s3_client.download_fileobj = AsyncMock()
    return s3_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    openai_client = Mock()
    openai_client.images.generate = AsyncMock()
    openai_client.chat.completions.create = AsyncMock()
    return openai_client


@pytest.fixture
def mock_pillow_image():
    """Mock Pillow Image for testing."""
    image = Mock()
    image.convert = Mock(return_value=image)
    image.crop = Mock(return_value=image)
    image.resize = Mock(return_value=image)
    image.save = Mock()
    image.size = (1024, 1792)
    return image


# Database fixtures
@pytest.fixture
async def mock_user_collection():
    """Mock user collection for testing."""
    return mock_mongo_collection()


@pytest.fixture
async def mock_api_key_collection():
    """Mock API key collection for testing."""
    return mock_mongo_collection()


@pytest.fixture
async def mock_adventure_collection():
    """Mock adventure collection for testing."""
    return mock_mongo_collection()


# Authentication fixtures
@pytest.fixture
def mock_auth_result_user():
    """Mock authentication result for user."""
    return {"type": "user", "id": str(ObjectId())}


@pytest.fixture
def mock_auth_result_api_key():
    """Mock authentication result for API key."""
    return {
        "type": "api_key",
        "info": {
            "key_id": str(ObjectId()),
            "name": "Test Key",
            "scopes": ["read", "write"],
            "created_at": datetime.utcnow(),
            "expires_at": None,
        },
    }


# Error fixtures
@pytest.fixture
def mock_http_exception():
    """Mock HTTP exception for testing."""
    from fastapi import HTTPException

    return HTTPException(status_code=400, detail="Test error")


@pytest.fixture
def mock_validation_error():
    """Mock validation error for testing."""
    from pydantic import ValidationError

    return ValidationError(errors=[], model=Mock())


# Environment fixtures
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    import os

    with patch.dict(
        os.environ,
        {
            "MONGO_URL": "mongodb://localhost:27017/test",
            "DATABASE_NAME": "test_db",
            "JWT_SECRET_KEY": "test_secret_key",
            "IMAGE_BUCKET_NAME": "test-image-bucket",
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_REGION": "us-east-1",
            "OPENAI_API_KEY": "test_openai_key",
        },
    ):
        yield


# Utility functions for testing
def create_mock_response(status_code: int, data: dict = None):
    """Create a mock HTTP response for testing."""
    response = Mock()
    response.status_code = status_code
    if data:
        response.json = Mock(return_value=data)
    return response


def create_mock_request(headers: dict = None, query_params: dict = None):
    """Create a mock HTTP request for testing."""
    request = Mock()
    request.headers = headers or {}
    request.query_params = query_params or {}
    return request


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Add cleanup logic here if needed
    pass
