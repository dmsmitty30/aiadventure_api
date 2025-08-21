import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_mongodb_collection():
    """Mock MongoDB collection for testing"""
    collection = AsyncMock()
    collection.find_one.return_value = None
    collection.find.return_value = AsyncMock()
    collection.insert_one.return_value = AsyncMock(inserted_id=ObjectId())
    collection.update_one.return_value = AsyncMock(modified_count=1)
    collection.delete_one.return_value = AsyncMock(deleted_count=1)
    return collection


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing"""
    s3_client = AsyncMock()
    s3_client.upload_fileobj.return_value = None
    s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-key"
    return s3_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    openai_client = MagicMock()
    openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"title": "Test Story", "nodes": []}'))]
    )
    openai_client.images.generate.return_value = MagicMock(
        data=[MagicMock(url="http://test.com/image.jpg")]
    )
    return openai_client


@pytest.fixture
def mock_pillow_image():
    """Mock Pillow Image for testing"""
    with patch('PIL.Image.open') as mock_open:
        mock_image = MagicMock()
        mock_image.resize.return_value = mock_image
        mock_image.crop.return_value = mock_image
        mock_image.save.return_value = None
        mock_open.return_value = mock_image
        yield mock_image


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict('os.environ', {
        'SECRET_KEY': 'test-secret-key',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'MONGODB_URL': 'mongodb://localhost:27017/test',
        'DATABASE_NAME': 'test_db',
        'OPENAI_API_KEY': 'test-openai-key',
        'AWS_ACCESS_KEY_ID': 'test-access-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
        'AWS_REGION': 'us-east-1',
        'IMAGE_BUCKET_NAME': 'test-image-bucket'
    }):
        yield


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing"""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    response.content = b"test content"
    return response


@pytest.fixture
def mock_http_request():
    """Mock HTTP request for testing"""
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}
    request.cookies = {"access_token": "test-token"}
    return request


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "regular_user": {
            "_id": ObjectId(),
            "email": "user@test.com",
            "role": "user",
            "createdAt": "2025-01-01T00:00:00Z"
        },
        "admin_user": {
            "_id": ObjectId(),
            "email": "admin@test.com",
            "role": "admin",
            "createdAt": "2025-01-01T00:00:00Z"
        }
    }


    @pytest.fixture
    def sample_adventure_data():
        """Sample adventure data for testing"""
        return {
            "basic_adventure": {
                "_id": ObjectId(),
                "title": "Test Adventure",
                "owner_id": str(ObjectId()),
                "nodes": [{"id": 0, "text": "Start", "options": ["Continue"]}],
                "createdAt": "2025-01-01T00:00:00Z"
            },
            "cloned_adventure": {
                "_id": ObjectId(),
                "title": "(copy) Test Adventure",
                "owner_id": str(ObjectId()),
                "clone_of": str(ObjectId()),
                "nodes": [{"id": 0, "text": "Start", "options": ["Continue"]}],
                "createdAt": "2025-01-01T00:00:00Z"
            }
        }


@pytest.fixture
def mock_auth_service():
    """Mock authentication service for testing"""
    with patch('app.services.auth_service.require_any_auth') as mock_auth:
        mock_auth.return_value = {"type": "user", "id": str(ObjectId())}
        yield mock_auth


@pytest.fixture
def mock_user_service():
    """Mock user service for testing"""
    with patch('app.services.user_service.get_user_by_id') as mock_get_user, \
         patch('app.services.user_service.is_user_admin') as mock_is_admin:
        
        mock_get_user.return_value = {
            "_id": str(ObjectId()),
            "email": "test@example.com",
            "role": "user"
        }
        mock_is_admin.return_value = False
        
        yield {
            "get_user": mock_get_user,
            "is_admin": mock_is_admin
        }


@pytest.fixture
def mock_adventure_service():
    """Mock adventure service for testing"""
    with patch('app.services.adventure_service.fetch_adventures') as mock_fetch, \
         patch('app.services.adventure_service.get_adventure_for_user') as mock_get, \
         patch('app.services.adventure_service.clone_adventure') as mock_clone:
        
        mock_fetch.return_value = []
        mock_get.return_value = {
            "_id": ObjectId(),
            "title": "Test Adventure",
            "owner_id": str(ObjectId()),
            "nodes": []
        }
        mock_clone.return_value = {
            "adventure_id": str(ObjectId()),
            "title": "(copy) Test Adventure"
        }
        
        yield {
            "fetch": mock_fetch,
            "get": mock_get,
            "clone": mock_clone
        }


@pytest.fixture
def mock_api_key_service():
    """Mock API key service for testing"""
    with patch('app.services.api_key_service.list_api_keys') as mock_list, \
         patch('app.services.api_key_service.create_api_key') as mock_create, \
         patch('app.services.api_key_service.verify_api_key') as mock_verify:
        
        mock_list.return_value = []
        mock_create.return_value = {
            "key_id": str(ObjectId()),
            "api_key": "ak_test_key_123",
            "created_at": "2025-01-01T00:00:00Z"
        }
        mock_verify.return_value = {
            "key_id": str(ObjectId()),
            "user_id": str(ObjectId()),
            "is_active": True
        }
        
        yield {
            "list": mock_list,
            "create": mock_create,
            "verify": mock_verify
        }
