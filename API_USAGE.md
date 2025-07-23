# AI Adventure API - Usage Guide

This guide provides detailed examples and best practices for using the AI Adventure API.

## 🚀 Quick Start

### 1. Setup and Authentication

First, register a user and get an access token:

```bash
# Register a new user
curl -X POST "http://localhost:8000/user/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "adventurer@example.com",
       "password": "securepassword123"
     }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Start Your First Adventure

```bash
curl -X POST "http://localhost:8000/adventure/start" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Create a story about a young wizard discovering their magical powers in a hidden forest",
       "min_words_per_level": 150,
       "max_words_per_level": 300,
       "max_levels": 8,
       "perspective": "Second Person"
     }'

# Response:
{
  "adventure_id": "507f1f77bcf86cd799439011",
  "title": "The Forest's Secret Magic",
  "synopsis": "A young apprentice discovers ancient magical powers...",
  "createdAt": "2024-01-15T10:30:00Z",
  "coverImageURL": "https://s3.amazonaws.com/...",
  "node_index": 0
}
```

## 📖 Complete API Examples

### Adventure Management

#### List All Adventures
```bash
curl -X GET "http://localhost:8000/adventure/list" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "adventures": [
    {
      "adventure_id": "507f1f77bcf86cd799439011",
      "title": "The Forest's Secret Magic",
      "synopsis": "A young apprentice discovers...",
      "userPrompt": "Create a story about a young wizard...",
      "createdAt": "2024-01-15T10:30:00Z",
      "perspective": "Second Person",
      "max_levels": 8,
      "min_words_per_level": 150,
      "max_words_per_level": 300,
      "numNodes": 1
    }
  ]
}
```

#### Get Adventure Nodes
```bash
curl -X GET "http://localhost:8000/adventure/nodes/507f1f77bcf86cd799439011" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "adventure_id": "507f1f77bcf86cd799439011",
  "nodes": [
    {
      "text": "You stand at the edge of an ancient forest...",
      "options": [
        "Enter the forest cautiously",
        "Call out for help",
        "Turn back and return home"
      ],
      "level": 0
    }
  ]
}
```

#### Continue Adventure
```bash
curl -X PUT "http://localhost:8000/adventure/continue" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "adventure_id": "507f1f77bcf86cd799439011",
       "start_from_node_id": 0,
       "selected_option": 0,
       "end_after_insert": "continue"
     }'

# Response:
{
  "adventure_id": "507f1f77bcf86cd799439011",
  "title": "The Forest's Secret Magic",
  "synopsis": "A young apprentice discovers...",
  "createdAt": "2024-01-15T10:30:00Z",
  "coverImageURL": "https://s3.amazonaws.com/...",
  "node_index": 1
}
```

#### End Adventure (Positive Ending)
```bash
curl -X PUT "http://localhost:8000/adventure/continue" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "adventure_id": "507f1f77bcf86cd799439011",
       "start_from_node_id": 5,
       "selected_option": 1,
       "end_after_insert": "finish"
     }'
```

#### End Adventure (Death Ending)
```bash
curl -X PUT "http://localhost:8000/adventure/continue" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "adventure_id": "507f1f77bcf86cd799439011",
       "start_from_node_id": 3,
       "selected_option": 2,
       "end_after_insert": "dead"
     }'
```

#### Get Cover Image URL
```bash
curl -X GET "http://localhost:8000/adventure/getCoverImageURL/507f1f77bcf86cd799439011/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
  "image_url": "https://s3.amazonaws.com/adventureappdms/..."
}
```

#### Delete Adventure
```bash
curl -X DELETE "http://localhost:8000/adventure/delete" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "adventure_id": "507f1f77bcf86cd799439011"
     }'
```

#### Truncate Adventure (Remove nodes after a certain point)
```bash
curl -X PATCH "http://localhost:8000/adventure/truncate" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "adventure_id": "507f1f77bcf86cd799439011",
       "node_index": 3
     }'
```

## 🎮 Story Generation Tips

### Effective Prompts

**Good Examples:**
- "Create a story about a detective solving a mystery in a haunted mansion"
- "Write an adventure where a young chef discovers magical ingredients in a hidden market"
- "Tell a tale of a time traveler who must prevent a historical disaster"

**Story Parameters:**
- `min_words_per_level`: 100-200 words (recommended)
- `max_words_per_level`: 200-400 words (recommended)
- `max_levels`: 5-15 levels (depending on story complexity)
- `perspective`: "First Person", "Second Person", or "Third Person"

### Story Perspectives

**Second Person (Recommended):**
```json
{
  "perspective": "Second Person"
}
```
- Creates immersive "choose your own adventure" experience
- Uses "You" pronouns for direct reader engagement

**First Person:**
```json
{
  "perspective": "First Person"
}
```
- Tells story from protagonist's viewpoint
- Uses "I" pronouns

**Third Person:**
```json
{
  "perspective": "Third Person"
}
```
- Traditional narrative style
- Uses "He/She/They" pronouns

## 🔐 Authentication Best Practices

### Token Management
```javascript
// Store token securely
const token = response.access_token;
localStorage.setItem('auth_token', token);

// Use token in requests
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### Error Handling
```javascript
// Handle authentication errors
if (response.status === 401) {
  // Token expired or invalid
  localStorage.removeItem('auth_token');
  // Redirect to login
}
```

## 🖼️ Image Generation

### Cover Image Features
- **Automatic Generation**: Each adventure gets a unique cover image
- **DALL-E 3**: High-quality AI-generated artwork
- **Portrait Orientation**: 1024x1792 pixels (mobile-friendly)
- **Vivid Style**: Enhanced colors and details
- **S3 Storage**: Secure cloud storage with presigned URLs

### Image Access
```javascript
// Get cover image URL
const response = await fetch(`/adventure/getCoverImageURL/${adventureId}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { image_url } = await response.json();

// Display image
const img = document.createElement('img');
img.src = image_url;
img.alt = adventure.title;
```

## 🗄️ Database Schema Examples

### User Document
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "adventurer@example.com",
  "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$...",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### Adventure Document
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "owner_id": "507f1f77bcf86cd799439011",
  "title": "The Forest's Secret Magic",
  "synopsis": "A young apprentice discovers ancient magical powers...",
  "userPrompt": "Create a story about a young wizard...",
  "createdAt": "2024-01-15T10:30:00Z",
  "perspective": "Second Person",
  "max_levels": 8,
  "min_words_per_level": 150,
  "max_words_per_level": 300,
  "image_s3_bucket": "adventureappdms",
  "image_s3_key": "adventure_507f1f77bcf86cd799439012.jpg",
  "nodes": [
    {
      "text": "You stand at the edge of an ancient forest...",
      "options": [
        "Enter the forest cautiously",
        "Call out for help",
        "Turn back and return home"
      ],
      "level": 0
    },
    {
      "text": "You step carefully into the forest...",
      "options": [
        "Continue deeper into the forest",
        "Look for signs of civilization"
      ],
      "level": 1
    }
  ]
}
```

## 🧪 Testing Examples

### Using the Test Files

**Test Story Generation:**
```bash
python test_adventure.py
```

**Test Story Continuation:**
```bash
python test_continue_adventure.py
```

**Test Image Generation:**
```bash
python test_imagecreate.py
```

### Custom Test Example
```python
import asyncio
from app.services.chatgpt_service import askOpenAI_structured, developerMessage, userMessage

async def test_custom_story():
    context = [
        developerMessage("Create a choose-your-own adventure story...")
    ]
    
    prompt = userMessage("Create a story about a robot learning to paint")
    response = await askOpenAI_structured(context, prompt, "new")
    print(response)

asyncio.run(test_custom_story())
```

## 🚀 Performance Tips

### API Optimization
1. **Batch Requests**: Group related operations when possible
2. **Caching**: Cache adventure data on the client side
3. **Pagination**: For large adventure lists (future feature)
4. **Connection Pooling**: Use connection pooling for database operations

### Story Generation
1. **Clear Prompts**: Be specific about story elements
2. **Reasonable Lengths**: Don't set extremely high word counts
3. **Appropriate Levels**: Balance story depth with user engagement

## 🔒 Security Considerations

### Client-Side Security
```javascript
// Never store sensitive data in localStorage
// Use secure HTTP-only cookies for production
// Implement token refresh logic
```

### API Security
- All endpoints require authentication (except registration)
- Input validation on all requests
- Rate limiting to prevent abuse
- Secure password hashing with Argon2

## 🆘 Troubleshooting

### Common Issues

**401 Unauthorized:**
- Check if token is valid and not expired
- Ensure token is included in Authorization header
- Verify token format: `Bearer <token>`

**404 Not Found:**
- Verify adventure_id exists and belongs to user
- Check if adventure was deleted

**500 Internal Server Error:**
- Check OpenAI API key and quota
- Verify AWS S3 credentials
- Check MongoDB connection

### Debug Mode
```bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug
```

## 📞 Support

For additional help:
- Check the interactive API docs at `/docs`
- Review the test files for working examples
- Open an issue on the repository
- Check the main README.md for setup instructions 