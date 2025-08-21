# RBAC Test Suite for AI Adventure API

This comprehensive test suite verifies that Role-Based Access Control (RBAC) is working correctly across all adventure operations and user management endpoints.

## 🎯 **What These Tests Cover**

### **1. Regular User Permissions**
- ✅ **Can create their own stories** (`/adventure/start`)
- ✅ **Can clone their own stories** (`/adventure/clone`)
- ✅ **Can continue their own stories** (`/adventure/continue`)
- ✅ **Can truncate their own stories** (`/adventure/truncate`)
- ✅ **Can delete their own stories** (`/adventure/delete`)
- ❌ **Cannot access stories they don't own**
- ❌ **Cannot access admin endpoints**

### **2. Admin User Permissions**
- ✅ **Can access any story** (regardless of ownership)
- ✅ **Can clone any story**
- ✅ **Can continue any story**
- ✅ **Can truncate any story**
- ✅ **Can delete any story**
- ✅ **Can delete other users** (`/admin/users/{user_id}`)
- ✅ **Can access all admin endpoints**
- ❌ **Cannot delete themselves**

### **3. User Management RBAC**
- ✅ **Only admins can create users** (`/admin/users`)
- ✅ **Only admins can delete users** (`/admin/users/{user_id}`)
- ✅ **Only admins can manage API keys**
- ❌ **Regular users cannot access admin functions**

## 🧪 **Running the Tests**

### **Option 1: Run All RBAC Tests**
```bash
python run_rbac_tests.py
```

### **Option 2: Run Specific Test Categories**
```bash
# Run only adventure access tests
python run_rbac_tests.py adventure

# Run only ownership validation tests
python run_rbac_tests.py ownership

# Run only user management tests
python run_rbac_tests.py user_management
```

### **Option 3: Run with Pytest Directly**
```bash
# Run all RBAC tests
python -m pytest tests/test_rbac_adventure_access.py -v

# Run specific test class
python -m pytest tests/test_rbac_adventure_access.py::TestRBACAdventureAccess -v

# Run specific test method
python -m pytest tests/test_rbac_adventure_access.py::TestRBACAdventureAccess::test_regular_user_can_create_own_story -v
```

## 📋 **Test Structure**

### **TestRBACAdventureAccess**
Tests the core adventure operations with different user roles:
- Regular user permissions on their own stories
- Regular user restrictions on others' stories
- Admin user permissions on all stories
- Admin user restrictions (self-deletion prevention)

### **TestAdventureOwnershipValidation**
Tests that adventure ownership is properly validated:
- Users cannot modify adventures they don't own
- Proper error responses for unauthorized access

### **TestUserManagementRBAC**
Tests user management endpoint access control:
- Admin-only user creation
- Admin-only user deletion
- Admin-only API key management

## 🔧 **Test Dependencies**

The tests use extensive mocking to avoid requiring:
- Real MongoDB database
- Real AWS S3 services
- Real OpenAI API calls
- Real image processing

All external dependencies are mocked using `unittest.mock`.

## 📊 **Expected Test Results**

When all tests pass, you should see:
```
✅ All RBAC tests passed!
🎉 Role-based access control is working correctly.
```

## 🚨 **Common Test Failures**

### **Authentication Issues**
- **401 Unauthorized**: JWT token validation problems
- **403 Forbidden**: Role-based access denied

### **Mock Configuration Issues**
- **ImportError**: Missing mock patches
- **AttributeError**: Incorrect mock return values

### **Async Issues**
- **RuntimeError**: Missing `@pytest.mark.asyncio` decorator
- **Event loop errors**: Async test configuration problems

## 🛠 **Troubleshooting**

### **If Tests Won't Run**
1. **Install dependencies**: `pip install pytest pytest-asyncio pytest-mock`
2. **Check Python version**: Tests require Python 3.7+
3. **Verify imports**: Make sure all app modules can be imported

### **If Tests Fail**
1. **Check mock configurations**: Verify all external services are properly mocked
2. **Review error messages**: Look for specific assertion failures
3. **Check test data**: Ensure test fixtures are properly configured

### **If You Need to Debug**
1. **Run with `-s` flag**: `pytest -s` to see print statements
2. **Use `--pdb`**: `pytest --pdb` to drop into debugger on failures
3. **Check logs**: Look for any error output in the test run

## 🔄 **Adding New Tests**

To add new RBAC tests:

1. **Create test method** in appropriate test class
2. **Use existing fixtures** for common test data
3. **Mock external dependencies** using `@patch` decorator
4. **Test both positive and negative cases**
5. **Verify proper error responses** for unauthorized access

## 📝 **Example Test Method**

```python
@pytest.mark.asyncio
async def test_new_feature_rbac(self, client, admin_token, regular_token):
    """Test that new feature respects RBAC"""
    # Test admin access
    response = client.post(
        "/new/endpoint",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"data": "test"}
    )
    assert response.status_code == 200
    
    # Test regular user restriction
    response = client.post(
        "/new/endpoint",
        headers={"Authorization": f"Bearer {regular_token}"},
        json={"data": "test"}
    )
    assert response.status_code in [401, 403]
```

## 🎉 **Success Criteria**

The RBAC system is working correctly when:
- ✅ Regular users can only access their own content
- ✅ Admin users can access all content
- ✅ Unauthorized access is properly blocked
- ✅ Error messages are clear and appropriate
- ✅ All test scenarios pass consistently
