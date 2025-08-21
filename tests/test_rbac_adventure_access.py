import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app
from app.services.user_service import create_access_token
from app.services.adventure_service import (
    fetch_adventures, 
    clone_adventure, 
    generate_new_node
)
from app.database import (
    get_adventure_collection, 
    get_user_collection,
    update_adventure_nodes,
    delete_adventure,
    truncate_adventure
)


class TestRBACAdventureAccess:
    """Test suite for Role-Based Access Control in adventure operations"""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def regular_user_id(self):
        """Regular user ID for testing"""
        return str(ObjectId())
    
    @pytest.fixture
    def admin_user_id(self):
        """Admin user ID for testing"""
        return str(ObjectId())
    
    @pytest.fixture
    def other_user_id(self):
        """Another user ID for testing"""
        return str(ObjectId())
    
    @pytest.fixture
    def regular_user_token(self, regular_user_id):
        """JWT token for regular user"""
        return create_access_token(data={"sub": regular_user_id})
    
    @pytest.fixture
    def admin_user_token(self, admin_user_id):
        """JWT token for admin user"""
        return create_access_token(data={"sub": admin_user_id})
    
    @pytest.fixture
    def sample_adventure(self, regular_user_id):
        """Sample adventure data"""
        return {
            "_id": ObjectId(),
            "title": "Test Adventure",
            "owner_id": regular_user_id,
            "nodes": [{"id": 0, "text": "Start", "options": ["Continue"]}],
            "createdAt": "2025-01-01T00:00:00Z"
        }
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock user data for testing"""
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

    @pytest.mark.asyncio
    async def test_regular_user_can_create_own_story(self, client, regular_user_token, sample_adventure):
        """Test that regular users can create their own stories"""
        with patch('app.services.adventure_service.generate_new_story') as mock_gen_story, \
             patch('app.services.image_service.askDallE_structured') as mock_dalle, \
             patch('app.services.image_service.process_image') as mock_process, \
             patch('app.database.get_adventure_collection') as mock_collection:
            
            # Mock successful story generation
            mock_gen_story.return_value = '{"title": "Test Story", "nodes": []}'
            mock_dalle.return_value = MagicMock(data=[MagicMock(url="http://test.com/image.jpg")])
            mock_process.return_value = {"bucket_name": "test-bucket", "s3_key": "test-key"}
            
            # Mock database operations
            mock_coll = AsyncMock()
            mock_collection.return_value = mock_coll
            mock_coll.insert_one.return_value = AsyncMock(inserted_id=ObjectId())
            
            response = client.post(
                "/adventure/start",
                headers={"Authorization": f"Bearer {regular_user_token}"},
                json={
                    "prompt": "Test story",
                    "max_levels": 3,
                    "min_words_per_level": 100,
                    "max_words_per_level": 200,
                    "perspective": "Second Person",
                    "coverimage": False
                }
            )
            
            assert response.status_code == 200
            assert "adventure_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_regular_user_can_clone_own_story(self, client, regular_user_token, sample_adventure):
        """Test that regular users can clone their own stories"""
        with patch('app.services.adventure_service.clone_adventure') as mock_clone:
            mock_clone.return_value = {
                "adventure_id": str(ObjectId()),
                "title": "(copy) Test Adventure",
                "clone_of": str(sample_adventure["_id"])
            }
            
            response = client.post(
                "/adventure/clone",
                headers={"Authorization": f"Bearer {regular_user_token}"},
                json={"adventure_id": str(sample_adventure["_id"])}
            )
            
            assert response.status_code == 200
            assert "adventure_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_regular_user_can_continue_own_story(self, client, regular_user_token, sample_adventure):
        """Test that regular users can continue their own stories"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.services.adventure_service.get_adventure_by_id') as mock_get_by_id, \
             patch('app.services.adventure_service.generate_new_node') as mock_gen_node, \
             patch('app.database.update_adventure_nodes') as mock_update:
            
            # Debug: Print what we're setting up
            print(f"Setting up mock to return: {sample_adventure}")
            mock_get.return_value = sample_adventure
            mock_get_by_id.return_value = sample_adventure
            mock_gen_node.return_value = {"id": 1, "content": "New Node", "options": ["End"]}
            mock_update.return_value = True
            
            # Debug: Verify the mock is set up correctly
            print(f"Mock get_adventure_for_user return value: {mock_get.return_value}")
            
            response = client.post(
                "/adventure/continue",
                headers={"Authorization": f"Bearer {regular_user_token}"},
                json={
                    "adventure_id": str(sample_adventure["_id"]),
                    "start_from_node_id": 0,
                    "selected_option": 0,
                    "end_after_insert": "continue"
                }
            )
            
            assert response.status_code == 200
            assert "node_index" in response.json()
    
    @pytest.mark.asyncio
    async def test_regular_user_can_truncate_own_story(self, client, regular_user_token, sample_adventure):
        """Test that regular users can truncate their own stories"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.database.truncate_adventure') as mock_truncate:
    
            # Debug: Print what we're setting up
            print(f"Setting up mock to return: {sample_adventure}")
            mock_get.return_value = sample_adventure
            mock_truncate.return_value = True
            
            # Debug: Verify the mock is set up correctly
            print(f"Mock get_adventure_for_user return value: {mock_get.return_value}")
    
            response = client.patch(
                "/adventure/truncate",
                headers={"Authorization": f"Bearer {regular_user_token}"},
                json={"adventure_id": str(sample_adventure["_id"]), "node_index": 0}
            )
            
            # Debug: Print response details
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
    
            assert response.status_code == 200
            assert "action" in response.json()
    
    @pytest.mark.asyncio
    async def test_regular_user_can_delete_own_story(self, client, regular_user_token, sample_adventure):
        """Test that regular users can delete their own stories"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.database.delete_adventure') as mock_delete:
            
            mock_get.return_value = sample_adventure
            mock_delete.return_value = True
            
            response = client.delete(
                f"/adventure/delete/{sample_adventure['_id']}",
                headers={"Authorization": f"Bearer {regular_user_token}"}
            )
            
            assert response.status_code == 200
            assert "action" in response.json()
    
    @pytest.mark.asyncio
    async def test_regular_user_cannot_access_others_stories(self, client, regular_user_token, sample_adventure):
        """Test that regular users cannot access stories they don't own"""
        # Change the owner to a different user
        sample_adventure["owner_id"] = "different_user_id"
        
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get:
            mock_get.return_value = 401  # Not authorized
            
            response = client.get(
                f"/adventure/nodes/{sample_adventure['_id']}",
                headers={"Authorization": f"Bearer {regular_user_token}"}
            )
            
            assert response.status_code == 401
            assert "Content Not authorized for user" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_admin_user_can_access_any_story(self, client, admin_user_token, sample_adventure):
        """Test that admin users can access any story"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get:
            mock_get.return_value = sample_adventure
            
            response = client.get(
                f"/adventure/nodes/{sample_adventure['_id']}",
                headers={"Authorization": f"Bearer {admin_user_token}"}
            )
            
            assert response.status_code == 200
            assert "nodes" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_user_can_clone_any_story(self, client, admin_user_token, sample_adventure):
        """Test that admin users can clone any story"""
        with patch('app.services.adventure_service.clone_adventure') as mock_clone:
            mock_clone.return_value = {
                "adventure_id": str(ObjectId()),
                "title": "(copy) Test Adventure",
                "clone_of": str(sample_adventure["_id"])
            }
            
            response = client.post(
                "/adventure/clone",
                headers={"Authorization": f"Bearer {admin_user_token}"},
                json={"adventure_id": str(sample_adventure["_id"])}
            )
            
            assert response.status_code == 200
            assert "adventure_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_user_can_continue_any_story(self, client, admin_user_token, sample_adventure):
        """Test that admin users can continue any story"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.services.adventure_service.get_adventure_by_id') as mock_get_by_id, \
             patch('app.services.adventure_service.generate_new_node') as mock_gen_node, \
             patch('app.database.update_adventure_nodes') as mock_update:
            
            mock_get.return_value = sample_adventure
            mock_get_by_id.return_value = sample_adventure
            mock_gen_node.return_value = {"id": 1, "content": "New Node", "options": ["End"]}
            mock_update.return_value = True
            
            response = client.post(
                "/adventure/continue",
                headers={"Authorization": f"Bearer {admin_user_token}"},
                json={
                    "adventure_id": str(sample_adventure["_id"]),
                    "start_from_node_id": 0,
                    "selected_option": 0,
                    "end_after_insert": "continue"
                }
            )
            
            assert response.status_code == 200
            assert "node_index" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_user_can_truncate_any_story(self, client, admin_user_token, sample_adventure):
        """Test that admin users can truncate any story"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.database.truncate_adventure') as mock_truncate, \
             patch('app.services.user_service.is_user_admin') as mock_is_admin:
            
            # Debug: Print what we're setting up
            print(f"Setting up mock to return: {sample_adventure}")
            mock_get.return_value = sample_adventure
            mock_truncate.return_value = True
            mock_is_admin.return_value = True
            
            # Debug: Verify the mock is set up correctly
            print(f"Mock get_adventure_for_user return value: {mock_get.return_value}")
            print(f"Mock is_user_admin return value: {mock_is_admin.return_value}")
            
            response = client.patch(
                "/adventure/truncate",
                headers={"Authorization": f"Bearer {admin_user_token}"},
                json={"adventure_id": str(sample_adventure["_id"]), "node_index": 0}
            )
            
            # Debug: Print response details
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            
            assert response.status_code == 200
            assert "action" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_user_can_delete_any_story(self, client, admin_user_token, sample_adventure):
        """Test that admin users can delete any story"""
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get, \
             patch('app.database.delete_adventure') as mock_delete, \
             patch('app.services.user_service.is_user_admin') as mock_is_admin:
            
            mock_get.return_value = sample_adventure
            mock_delete.return_value = True
            mock_is_admin.return_value = True
            
            response = client.delete(
                f"/adventure/delete/{sample_adventure['_id']}",
                headers={"Authorization": f"Bearer {admin_user_token}"}
            )
            
            assert response.status_code == 200
            assert "action" in response.json()
    
    @pytest.mark.asyncio
    async def test_admin_user_can_delete_other_user(self, client, admin_user_token, regular_user_id):
        """Test that admin users can delete other users"""
        with patch('app.services.user_service.get_user_by_id') as mock_get_user, \
             patch('app.services.user_service.delete_user') as mock_delete_user, \
             patch('app.services.user_service.is_user_admin') as mock_is_admin:
            
            mock_get_user.return_value = {
                "_id": regular_user_id,
                "email": "user@test.com",
                "role": "user"
            }
            mock_delete_user.return_value = True
            mock_is_admin.return_value = True
            
            response = client.delete(
                f"/admin/users/{regular_user_id}",
                headers={"Authorization": f"Bearer {admin_user_token}"}
            )
            
            assert response.status_code == 200
            assert "User deleted successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_admin_user_cannot_delete_themselves(self, client, admin_user_token, admin_user_id):
        """Test that admin users cannot delete themselves"""
        with patch('app.services.user_service.is_user_admin') as mock_is_admin:
            mock_is_admin.return_value = True
            
            response = client.delete(
                f"/admin/users/{admin_user_id}",
                headers={"Authorization": f"Bearer {admin_user_token}"}
            )
            
            assert response.status_code == 400
            assert "Admin cannot delete themselves" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_regular_user_cannot_delete_users(self, client, regular_user_token, other_user_id):
        """Test that regular users cannot delete users"""
        response = client.delete(
            f"/admin/users/{other_user_id}",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        # Should get 403 Forbidden or 401 Unauthorized
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_regular_user_cannot_access_admin_endpoints(self, client, regular_user_token):
        """Test that regular users cannot access admin endpoints"""
        response = client.get(
            "/admin/api-keys",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        
        # Should get 403 Forbidden or 401 Unauthorized
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_admin_user_can_access_admin_endpoints(self, client, admin_user_token):
        """Test that admin users can access admin endpoints"""
        with patch('app.routers.admin.list_api_keys') as mock_list, \
             patch('app.services.user_service.is_user_admin') as mock_is_admin:
            
            mock_list.return_value = []
            mock_is_admin.return_value = True
            
            response = client.get(
                "/admin/api-keys",
                headers={"Authorization": f"Bearer {admin_user_token}"}
            )
            
            # Debug: Print response details
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            
            assert response.status_code == 200
            assert "api_keys" in response.json()


class TestAdventureOwnershipValidation:
    """Test suite for adventure ownership validation"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def user_token(self):
        user_id = str(ObjectId())
        return create_access_token(data={"sub": user_id})
    
    @pytest.mark.asyncio
    async def test_adventure_ownership_check(self, client, user_token):
        """Test that adventure ownership is properly validated"""
        adventure_id = str(ObjectId())
        
        with patch('app.routers.adventure.get_adventure_for_user') as mock_get:
            # Mock that the adventure belongs to a different user
            mock_get.return_value = {
                "_id": ObjectId(adventure_id),
                "owner_id": "different_user_id",
                "title": "Test Adventure"
            }
            
            response = client.delete(
                f"/adventure/delete/{adventure_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            assert response.status_code == 401
            assert "User not authorized to delete this content" in response.json()["detail"]


class TestUserManagementRBAC:
    """Test suite for user management role-based access control"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def admin_token(self):
        admin_id = str(ObjectId())
        return create_access_token(data={"sub": admin_id})
    
    @pytest.fixture
    def regular_token(self):
        user_id = str(ObjectId())
        return create_access_token(data={"sub": user_id})
    
    @pytest.mark.asyncio
    async def test_create_user_admin_only(self, client, admin_token, regular_token):
        """Test that only admins can create users"""
        # Admin should be able to create users
        with patch('app.services.user_service.register_user') as mock_register, \
             patch('app.services.user_service.is_user_admin') as mock_is_admin:
            
            mock_register.return_value = ObjectId()
            mock_is_admin.return_value = True
            
            response = client.post(
                "/admin/users",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "email": "newuser@test.com",
                    "password": "password123",
                    "role": "user"
                }
            )
            
            assert response.status_code == 200
            assert "User created successfully" in response.json()["message"]
        
        # Regular user should not be able to create users
        response = client.post(
            "/admin/users",
            headers={"Authorization": f"Bearer {regular_token}"},
            json={
                "email": "newuser2@test.com",
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_delete_user_admin_only(self, client, admin_token, regular_token):
        """Test that only admins can delete users"""
        user_to_delete = str(ObjectId())
        
        # Regular user should not be able to delete users
        response = client.delete(
            f"/admin/users/{user_to_delete}",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_api_key_management_admin_only(self, client, admin_token, regular_token):
        """Test that only admins can manage API keys"""
        # Regular user should not be able to list API keys
        response = client.get(
            "/admin/api-keys",
            headers={"Authorization": f"Bearer {regular_token}"}
        )
        
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
