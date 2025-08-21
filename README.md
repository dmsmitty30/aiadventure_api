# AI Adventure API

A FastAPI-based backend service that powers an AI-driven "choose your own adventure" application. This API generates interactive stories using OpenAI's GPT models, creates cover images with DALL-E, and manages user adventures with MongoDB. Features comprehensive security, role-based access control, and API key management for developers.

## 🚀 Features

- **AI-Powered Story Generation**: Creates dynamic choose-your-own-adventure stories using OpenAI GPT-4
- **Conditional Cover Image Generation**: Optional DALL-E 3 cover image creation with S3 storage
- **Advanced Authentication System**: JWT tokens + API key support for flexible developer access
- **Role-Based Access Control (RBAC)**: Admin and user roles with granular permissions
- **API Key Management**: Comprehensive system for developer API access without user registration
- **Adventure Management**: Create, clone, continue, delete, and truncate adventures
- **Cloud Storage**: S3 integration with thumbnail generation and caching
- **MongoDB Database**: Scalable document storage with proper indexing
- **RESTful API**: Clean, well-documented API endpoints with OpenAPI/Swagger UI
- **Enterprise Security**: CORS, rate limiting, input sanitization, and security headers

## 🏗️ Architecture

```
aiadventure_api/
├── app/
│   ├── routers/          # API route handlers
│   │   ├── adventure.py  # Adventure CRUD operations with RBAC
│   │   ├── user.py       # User authentication & management
│   │   ├── admin.py      # Admin-only endpoints (API keys, users)
│   │   └── auth.py       # Unified authentication system
│   ├── services/         # Business logic layer
│   │   ├── adventure_service.py  # Story generation & management
│   │   ├── chatgpt_service.py    # OpenAI GPT-4 integration
│   │   ├── image_service.py      # DALL-E 3 & S3 with thumbnails
│   │   ├── user_service.py       # User management & RBAC
│   │   └── api_key_service.py    # API key generation & validation
│   ├── schemas/          # Pydantic models & validation
│   │   ├── adventure.py  # Adventure data models
│   │   ├── user.py       # User & role models
│   │   └── api_key.py    # API key models
│   ├── security.py       # Input sanitization & validation
│   ├── database.py       # MongoDB connection & operations
│   └── main.py          # FastAPI app with security middleware
├── tests/                # Comprehensive test suite
│   ├── test_rbac_adventure_access.py  # RBAC security tests
│   ├── test_api_key_service.py        # API key service tests
│   └── conftest.py                    # Test fixtures & configuration
├── requirements.txt      # Production dependencies
├── requirements-test.txt # Testing dependencies
└── README.md            # This file
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI with async/await support
- **Database**: MongoDB with Motor async driver
- **AI Services**: OpenAI GPT-4 & DALL-E 3
- **Cloud Storage**: AWS S3 with thumbnail caching
- **Authentication**: JWT tokens + API keys
- **Password Hashing**: Argon2 (industry standard)
- **Image Processing**: Pillow for thumbnails
- **Security**: CORS, rate limiting, input sanitization
- **Testing**: Pytest with async support
- **Code Quality**: Black, Flake8, isort

## 📋 Prerequisites

- Python 3.8+
- MongoDB instance (local or cloud)
- OpenAI API key
- AWS S3 bucket and credentials
- Virtual environment (recommended)

## 🔧 Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aiadventure_api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # Database
   MONGO_URL=mongodb://localhost:27017
   DATABASE_NAME=aiadventure_db
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # AWS S3
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   IMAGE_BUCKET_NAME=your_s3_bucket_name
   
   # JWT (REQUIRED - no fallback for security)
   SECRET_KEY=your_secure_jwt_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours default
   
   # CORS (optional - defaults to localhost)
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

## 🚀 Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## 🔐 Authentication System

The API supports **dual authentication** methods:

### 1. JWT Token Authentication (Users)
- **Registration**: `/user/register` - Create new user accounts
- **Login**: `/token` - Get JWT access token
- **Token Expiry**: 24 hours (configurable)
- **Password Security**: Argon2 hashing

### 2. API Key Authentication (Developers)
- **Admin Creation**: `/admin/api-keys` - Create API keys (admin only)
- **Key Management**: Full CRUD operations for API keys
- **Scope Support**: Configurable permissions
- **Expiration**: Optional key expiry dates

### Getting Access

#### For End Users:
```bash
# Register
curl -X POST "http://localhost:8000/user/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword", "role": "user"}'

# Login
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=securepassword"
```

#### For Developers (API Keys):
```bash
# Admin creates API key
curl -X POST "http://localhost:8000/admin/api-keys" \
     -H "Authorization: Bearer <admin_jwt_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "My App", "scopes": ["read", "write"], "expires_in_days": 30}'

# Use API key
curl -X GET "http://localhost:8000/adventure/list" \
     -H "Authorization: Bearer <api_key>"
```

## 🎭 Role-Based Access Control (RBAC)

### User Roles
- **`user`**: Regular users can manage their own adventures
- **`admin`**: Administrators can access all adventures and manage users/API keys

### Permission Matrix

| Action | Regular User | Admin User |
|--------|--------------|------------|
| Create own story | ✅ | ✅ |
| Clone own story | ✅ | ✅ |
| Continue own story | ✅ | ✅ |
| Truncate own story | ✅ | ✅ |
| Delete own story | ✅ | ✅ |
| Access others' stories | ❌ | ✅ |
| Manage API keys | ❌ | ✅ |
| Delete users | ❌ | ✅ |
| Create admin users | ❌ | ✅ |

## 📖 Adventure Management

### Story Creation
```bash
curl -X POST "http://localhost:8000/adventure/start" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A mysterious forest adventure",
       "max_levels": 5,
       "min_words_per_level": 150,
       "max_words_per_level": 300,
       "perspective": "Second Person",
       "coverimage": true
     }'
```

### Story Operations
- **Continue**: `/adventure/continue/{adventure_id}` - Add new story branches
- **Clone**: `/adventure/clone` - Duplicate existing adventures
- **Truncate**: `/adventure/truncate` - Remove story branches
- **Delete**: `/adventure/delete/{adventure_id}` - Remove adventures
- **List**: `/adventure/list` - View user's adventures
- **Nodes**: `/adventure/nodes/{adventure_id}` - Get story structure

### Story Perspectives
- **First Person**: "I walked through the door..."
- **Second Person**: "You walk through the door..."
- **Third Person**: "He walked through the door..."

### Cover Image Management
- **Conditional Generation**: `coverimage` parameter controls image creation
- **Update**: `/adventure/coverImage/update/{adventure_id}` - Modify existing images
- **Thumbnails**: `/adventure/coverImage/{adventure_id}` - Get optimized images
- **S3 Storage**: Automatic upload with thumbnail caching

## 🖼️ Image Generation & Storage

### DALL-E 3 Integration
- **Size**: 1024x1792 (portrait orientation)
- **Style**: Vivid (enhanced colors and details)
- **Conditional**: Only generated when `coverimage: true`

### S3 Storage & Processing
- **Automatic Upload**: Generated images stored in S3
- **Thumbnail Generation**: Cropped and scaled versions for performance
- **Caching**: Thumbnails cached to reduce processing overhead
- **Presigned URLs**: Secure, time-limited access to images

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "string",
  "hashed_password": "string",
  "role": "user|admin",
  "createdAt": "datetime"
}
```

### Adventures Collection
```json
{
  "_id": "ObjectId",
  "owner_id": "string",
  "title": "string",
  "synopsis": "string",
  "userPrompt": "string",
  "createdAt": "datetime",
  "perspective": "string",
  "max_levels": "number",
  "min_words_per_level": "number",
  "max_words_per_level": "number",
  "image_s3_bucket": "string",
  "image_s3_key": "string",
  "clone_of": "string|null",
  "nodes": [
    {
      "text": "string",
      "options": ["string"],
      "level": "number"
    }
  ]
}
```

### API Keys Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "key_hash": "string",
  "scopes": ["string"],
  "is_active": "boolean",
  "created_at": "datetime",
  "expires_at": "datetime|null",
  "last_used": "datetime|null"
}
```

## 🛡️ Security Features

### **HIGH PRIORITY (Implemented)**
- **CORS Configuration**: Configurable allowed origins with secure defaults
- **Security Headers**: XSS protection, clickjacking prevention, content type enforcement
- **Rate Limiting**: Login (5/min), story generation (10/hour), IP-based tracking
- **Input Sanitization**: HTML sanitization, injection prevention, length validation

### **MEDIUM PRIORITY (Planned)**
- **Scope Validation**: API key permission checking
- **Audit Logging**: Comprehensive access and modification logs
- **Password Policies**: Strength requirements and validation

### **LOW PRIORITY (Future)**
- **HTTPS Enforcement**: HSTS headers and redirects
- **Session Management**: Advanced session handling
- **Dependency Updates**: Automated security patch management

### Security Implementation Details
- **Password Hashing**: Argon2 with secure parameters
- **JWT Security**: Configurable expiration, secure algorithms
- **Input Validation**: Pydantic models with sanitization
- **XSS Prevention**: HTML tag whitelisting and sanitization
- **DoS Protection**: Request size limits and rate limiting
- **Injection Prevention**: Pattern detection and sanitization

## 🧪 Testing

### Test Suite
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python -m pytest

# Run specific test suites
python -m pytest tests/test_rbac_adventure_access.py -v
python -m pytest tests/test_api_key_service.py -v

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

### Test Coverage
- **RBAC Security**: Comprehensive role-based access control testing
- **API Key Management**: Full CRUD operation testing
- **Adventure Operations**: Story creation, modification, and deletion
- **Authentication**: JWT and API key validation
- **Input Validation**: Security and sanitization testing

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t aiadventure-api .

# Run container
docker run -p 8000:8000 --env-file .env aiadventure-api
```

### Production Considerations
- **ASGI Server**: Gunicorn with Uvicorn workers
- **Database**: MongoDB with authentication and SSL
- **AWS**: IAM roles for S3 access, CloudWatch monitoring
- **Security**: SSL/TLS certificates, firewall configuration
- **Monitoring**: Log aggregation, health checks, metrics
- **Environment**: Separate configs for dev/staging/production

## 🔄 API Versioning

### Current Version: v2.0.0
- **Major Features**: RBAC, API key management, security enhancements
- **Breaking Changes**: Authentication system overhaul
- **New Endpoints**: Admin routes, cover image management, adventure cloning
- **Security**: Comprehensive security implementation

### Migration Guide
- Update authentication headers to use new unified system
- Replace old cover image endpoints with new `/coverImage/*` routes
- Use new adventure deletion endpoint with path parameters
- Implement proper error handling for new validation responses

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with proper testing
4. **Run** the test suite (`python -m pytest`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Standards
- **Code Style**: Black formatting, Flake8 linting
- **Testing**: Minimum 80% coverage for new features
- **Documentation**: Update README and docstrings
- **Security**: Follow security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **API Documentation**: Interactive docs at `/docs`
- **Test Examples**: Review test files for usage patterns
- **Security Issues**: Report vulnerabilities privately
- **Feature Requests**: Open issues on GitHub

### Common Issues
- **401 Unauthorized**: Check token validity and expiration
- **403 Forbidden**: Verify user role and permissions
- **422 Validation Error**: Check request payload format
- **429 Too Many Requests**: Rate limit exceeded, wait and retry

## 🔄 Version History

### v2.0.0 (Current)
- **Security Overhaul**: CORS, rate limiting, input sanitization, security headers
- **RBAC System**: Role-based access control with admin privileges
- **API Key Management**: Comprehensive developer access system
- **Cover Image System**: Conditional generation with thumbnail support
- **Adventure Cloning**: Copy existing adventures with attribution
- **Unified Authentication**: JWT + API key support in single system

### v1.0.0 (Legacy)
- Basic user authentication and adventure management
- OpenAI GPT-4 integration for story generation
- DALL-E 3 integration for cover images
- MongoDB storage with S3 image hosting

---

**⚠️ Security Notice**: This API implements enterprise-grade security measures. Always use HTTPS in production and keep dependencies updated.
