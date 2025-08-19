# AI Adventure API - Test Suite

This directory contains comprehensive unit tests for the AI Adventure API. The tests cover all major components including API key management, authentication, user management, and admin functionality.

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Using pytest directly
python -m pytest

# Using the test runner script
python run_tests.py

# Using the test runner with verbose output
python run_tests.py --type all --verbose
```

### 3. Run Specific Test Categories

```bash
# Run only unit tests
python run_tests.py --type unit

# Run tests with coverage report
python run_tests.py --type coverage

# Run linting checks
python run_tests.py --type lint

# Format code
python run_tests.py --type format
```

### 4. Run Specific Test Files

```bash
# Run specific test file
python -m pytest tests/test_api_key_service.py

# Run tests matching a pattern
python -m pytest -k "test_generate_api_key"

# Run tests with verbose output
python -m pytest -v tests/test_admin_router.py
```

## 📁 Test Structure

```
tests/
├── __init__.py                 # Makes tests a Python package
├── conftest.py                 # Shared fixtures and configuration
├── test_api_key_service.py     # API key service tests
├── test_admin_router.py        # Admin router endpoint tests
├── test_auth_service.py        # Authentication service tests
├── test_user_service.py        # User service tests
└── README.md                   # This file
```

## 🧪 Test Categories

### 1. **API Key Service Tests** (`test_api_key_service.py`)
- ✅ API key generation
- ✅ API key verification
- ✅ API key management (CRUD operations)
- ✅ Thumbnail cache key generation
- ✅ Error handling and edge cases

### 2. **Admin Router Tests** (`test_admin_router.py`)
- ✅ Admin authentication verification
- ✅ API key management endpoints
- ✅ User creation by admins
- ✅ Authorization and access control
- ✅ Error handling

### 3. **Authentication Service Tests** (`test_auth_service.py`)
- ✅ JWT token authentication
- ✅ API key authentication
- ✅ Mixed authentication scenarios
- ✅ Authentication requirements
- ✅ Error handling

### 4. **User Service Tests** (`test_user_service.py`)
- ✅ User registration
- ✅ Admin role checking
- ✅ User role retrieval
- ✅ Password hashing
- ✅ Input validation

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)
- **Test Discovery**: Automatically finds test files in `tests/` directory
- **Coverage**: Generates HTML and XML coverage reports
- **Markers**: Defines test categories (slow, integration, unit, asyncio)
- **Warnings**: Filters out deprecation warnings

### Shared Fixtures (`conftest.py`)
- **Mock Objects**: MongoDB collections, S3 clients, OpenAI clients
- **Sample Data**: User data, API key data, adventure data
- **Environment Variables**: Mock environment for testing
- **Test Utilities**: Helper functions for creating mock responses

## 🎯 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api_key_service.py

# Run tests matching pattern
pytest -k "admin"

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Advanced Commands

```bash
# Run only fast tests (exclude slow markers)
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Generate coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html
```

## 📊 Coverage Reports

After running tests with coverage, you'll find:

- **Terminal Output**: Shows missing lines and coverage percentage
- **HTML Report**: `htmlcov/index.html` - Interactive coverage report
- **XML Report**: `coverage.xml` - For CI/CD integration

## 🐛 Debugging Tests

### 1. **Verbose Output**
```bash
pytest -v -s
```

### 2. **Stop on First Failure**
```bash
pytest -x
```

### 3. **Debug Specific Test**
```bash
pytest tests/test_admin_router.py::TestAdminRouter::test_create_api_key_success -v -s
```

### 4. **Show Local Variables on Failure**
```bash
pytest --tb=long
```

## 🔍 Test Patterns

### Naming Conventions
- **Test Files**: `test_*.py`
- **Test Classes**: `Test*`
- **Test Methods**: `test_*`

### Example Test Structure
```python
class TestAPIKeyService:
    """Test cases for API key service functions."""
    
    @pytest.fixture
    def mock_collection(self):
        """Mock MongoDB collection for testing."""
        # Setup code
        
    @pytest.mark.asyncio
    async def test_generate_api_key_success(self, mock_collection):
        """Test successful API key generation."""
        # Test implementation
        assert result["api_key"].startswith("ak_")
```

## 🚨 Common Issues

### 1. **Import Errors**
- Ensure you're running tests from the project root
- Check that `app/` directory exists
- Verify Python path includes project root

### 2. **Async Test Issues**
- Use `@pytest.mark.asyncio` decorator for async tests
- Ensure `pytest-asyncio` is installed
- Check `asyncio_mode = auto` in `pytest.ini`

### 3. **Mock Issues**
- Verify mock objects are properly configured
- Check that patches target correct import paths
- Use `AsyncMock` for async methods

### 4. **Database Connection Issues**
- Tests use mocked MongoDB collections
- No actual database connection required
- Check mock setup in fixtures

## 📈 Adding New Tests

### 1. **Create Test File**
```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    def test_new_feature_success(self):
        # Test implementation
        pass
```

### 2. **Add to Test Runner**
Update `run_tests.py` if you add new test categories.

### 3. **Update Coverage**
Ensure new code is covered by tests.

## 🏗️ CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    python -m pytest --cov=app --cov-report=xml
```

### Coverage Badge
Add coverage badge to your README:
```markdown
![Coverage](https://img.shields.io/badge/coverage-85%25-green)
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Pytest-Cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add comprehensive test coverage
3. Include edge cases and error scenarios
4. Update this README if adding new test categories
5. Ensure all tests pass before submitting

---

**Happy Testing! 🎉** 