# API Documentation

## Overview

The Azure Foundry Local Chat Playground exposes a RESTful API for programmatic access to chat functionality and model management.

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### Models

#### GET /models/available
Get list of available models and their status.

**Response:**
```json
{
  "models": ["qwen2.5-0.5b", "phi-3.5-mini", "llama-3.2-1b"],
  "status": {
    "qwen2.5-0.5b": {
      "status": "ready",
      "initialized_at": "2025-09-29T10:30:00Z"
    }
  }
}
```

#### POST /models/initialize
Initialize a specific model.

**Request:**
```json
{
  "model": "qwen2.5-0.5b"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model qwen2.5-0.5b initialized successfully",
  "status": { ... }
}
```

### Chat

#### POST /chat
Send a message to selected models (non-streaming).

**Request:**
```json
{
  "message": "Hello, how are you?",
  "models": ["qwen2.5-0.5b", "phi-3.5-mini"]
}
```

**Response:**
```json
{
  "message": "Hello, how are you?",
  "responses": {
    "qwen2.5-0.5b": "Hello! I'm doing well, thank you for asking...",
    "phi-3.5-mini": "Hi there! I'm functioning perfectly..."
  },
  "errors": {},
  "timestamp": "2025-09-29T10:35:00Z"
}
```

#### POST /chat/stream
Send a message with streaming responses (Server-Sent Events).

**Request:** Same as `/chat`

**Response:** Server-Sent Events stream with the following event types:

- `start`: Streaming initiated
- `model_start`: Model begins processing
- `chunk`: Content chunk from model
- `model_complete`: Model finished
- `error`: Error from specific model
- `complete`: All models finished

### System

#### GET /status
Get system and model status.

**Response:**
```json
{
  "models": { ... },
  "history_count": 10,
  "available_models": [ ... ]
}
```

#### GET /history
Get chat history.

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2025-09-29T10:30:00Z",
      "user": "Hello",
      "responses": { ... }
    }
  ],
  "total_messages": 5
}
```

#### POST /history/clear
Clear chat history.

**Response:**
```json
{
  "success": true,
  "message": "History cleared"
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Usage Examples

### Python Example

```python
import requests

# Initialize a model
response = requests.post('http://localhost:5000/api/models/initialize', 
                        json={'model': 'qwen2.5-0.5b'})
print(response.json())

# Send a chat message
response = requests.post('http://localhost:5000/api/chat',
                        json={
                            'message': 'What is AI?',
                            'models': ['qwen2.5-0.5b']
                        })
print(response.json())
```

### JavaScript Example

```javascript
// Initialize a model
const initResponse = await fetch('/api/models/initialize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'qwen2.5-0.5b' })
});

// Send streaming chat
const eventSource = new EventSource('/api/chat/stream?' + 
    new URLSearchParams({
        message: 'Hello',
        models: 'qwen2.5-0.5b'
    }));

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## Rate Limits

Currently, no rate limits are enforced, but consider:
- Model initialization can be slow (30+ seconds)
- Concurrent requests are limited by model capacity
- Streaming connections are kept alive until completion

## Security

- The API runs on localhost by default
- No authentication is required for local development
- For production deployment, implement proper authentication