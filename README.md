# AI Adventure API

A FastAPI-based backend service that powers an AI-driven "choose your own adventure" application. This API generates interactive stories using OpenAI's GPT models, creates cover images with DALL-E, and manages user adventures with MongoDB.

## 🚀 Features

- **AI-Powered Story Generation**: Creates dynamic choose-your-own-adventure stories using OpenAI GPT-4
- **Image Generation**: Automatically generates cover images for stories using DALL-E 3
- **User Authentication**: JWT-based authentication system with user registration and login
- **Adventure Management**: Create, continue, delete, and truncate adventures
- **Cloud Storage**: S3 integration for storing and serving story cover images
- **MongoDB Database**: Scalable document storage for adventures and user data
- **RESTful API**: Clean, well-documented API endpoints

## 🏗️ Architecture

```
aiadventure_api/
├── app/
│   ├── routers/          # API route handlers
│   │   ├── adventure.py  # Adventure CRUD operations
│   │   ├── user.py       # User authentication
│   │   └── auth.py       # Auth utilities
│   ├── services/         # Business logic
│   │   ├── adventure_service.py  # Story generation logic
│   │   ├── chatgpt_service.py    # OpenAI integration
│   │   ├── image_service.py      # DALL-E & S3 integration
│   │   └── user_service.py       # User management
│   ├── schemas/          # Pydantic models
│   ├── database.py       # MongoDB connection & operations
│   └── main.py          # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **Database**: MongoDB (with Motor async driver)
- **AI Services**: OpenAI GPT-4 & DALL-E 3
- **Cloud Storage**: AWS S3
- **Authentication**: JWT tokens
- **Password Hashing**: Argon2
- **Image Processing**: Pillow
- **HTTP Client**: httpx

## 📋 Prerequisites

- Python 3.8+
- MongoDB instance
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
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database
   MONGO_URL=mongodb://localhost:27017
   DATABASE_NAME=aiadventure_db
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # AWS S3
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   
   # JWT (generate a secure secret)
   SECRET_KEY=your_jwt_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
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

## 🔐 Authentication

The API uses JWT-based authentication. Most endpoints require a Bearer token in the Authorization header.

### Getting an Access Token

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/user/register" \
        -H "Content-Type: application/json" \
        -d '{"email": "user@example.com", "password": "securepassword"}'
   ```

2. **Login to get token**:
   ```bash
   curl -X POST "http://localhost:8000/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=securepassword"
   ```

## 📖 API Endpoints

### Adventure Management

#### Start a New Adventure
```http
POST /adventure/start
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "prompt": "Create a story about a space explorer",
  "min_words_per_level": 100,
  "max_words_per_level": 200,
  "max_levels": 10,
  "perspective": "Second Person"
}
```

#### List User Adventures
```http
GET /adventure/list
Authorization: Bearer <your_token>
```

#### Get Adventure Nodes
```http
GET /adventure/nodes/{adventure_id}
Authorization: Bearer <your_token>
```

#### Continue Adventure
```http
PUT /adventure/continue
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "adventure_id": "adventure_id_here",
  "start_from_node_id": 0,
  "selected_option": 1,
  "end_after_insert": "continue"
}
```

#### Delete Adventure
```http
DELETE /adventure/delete
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "adventure_id": "adventure_id_here"
}
```

#### Truncate Adventure
```http
PATCH /adventure/truncate
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "adventure_id": "adventure_id_here",
  "node_index": 3
}
```

#### Get Cover Image URL
```http
GET /adventure/getCoverImageURL/{adventure_id}/
Authorization: Bearer <your_token>
```

### User Management

#### Register User
```http
POST /user/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

## 🎮 Story Generation Features

### Story Structure
Each adventure consists of:
- **Title**: Generated story title (max 5 words)
- **Synopsis**: Story summary (max 200 words)
- **Nodes**: Story chapters with branching choices
- **Cover Image**: AI-generated cover art

### Story Perspectives
- **First Person**: "I walked through the door..."
- **Second Person**: "You walk through the door..."
- **Third Person**: "He walked through the door..."

### Story Outcomes
- **Continue**: Story continues with new choices
- **Finish**: Story ends with positive conclusion
- **Dead**: Story ends with protagonist's death

## 🖼️ Image Generation

The API automatically generates cover images for each adventure using DALL-E 3:
- **Size**: 1024x1792 (portrait orientation)
- **Style**: Vivid (enhanced colors and details)
- **Storage**: Uploaded to S3 with presigned URLs for secure access

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "string",
  "hashed_password": "string",
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
  "nodes": [
    {
      "text": "string",
      "options": ["string"],
      "level": "number"
    }
  ]
}
```

## 🧪 Testing

The project includes test files for various components:
- `test_adventure.py`: Tests story generation
- `test_continue_adventure.py`: Tests story continuation
- `test_imagecreate.py`: Tests image generation

Run tests with:
```bash
python test_adventure.py
```

## 🔒 Security Features

- **Password Hashing**: Argon2 for secure password storage
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Pydantic models for request validation
- **CORS Support**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in FastAPI rate limiting capabilities

## 🚀 Deployment

### Docker Deployment
1. Build the Docker image:
   ```bash
   docker build -t aiadventure-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env aiadventure-api
   ```

### Production Considerations
- Use a production ASGI server like Gunicorn with Uvicorn workers
- Set up proper MongoDB authentication
- Configure AWS IAM roles for S3 access
- Implement proper logging and monitoring
- Set up SSL/TLS certificates
- Configure environment-specific settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test files for usage examples
- Open an issue on the repository

## 🔄 Version History

- **v1.0.0**: Initial release with core adventure generation features
- Basic user authentication and adventure management
- OpenAI GPT-4 integration for story generation
- DALL-E 3 integration for cover images
- MongoDB storage with S3 image hosting
