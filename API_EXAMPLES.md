# API Examples

This document provides example API requests using curl to test the chat application.

## Base URL

```
http://localhost:8000/api
```

## User Registration and Authentication

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Johnson",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }' \
  -c cookies.txt
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }' \
  -c cookies.txt -b cookies.txt
```

### 3. Get Profile

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -b cookies.txt
```

### 4. List Users

```bash
curl -X GET http://localhost:8000/api/users/list/ \
  -b cookies.txt
```

## Conversations

### 5. Create a Conversation

```bash
# Replace USER_ID_1 and USER_ID_2 with actual user IDs
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2]
  }' \
  -b cookies.txt
```

### 6. Create a Group Conversation

```bash
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2, 3],
    "name": "Team Discussion"
  }' \
  -b cookies.txt
```

### 7. List All Conversations

```bash
curl -X GET http://localhost:8000/api/chat/conversations/ \
  -b cookies.txt
```

### 8. Get Conversation Details

```bash
# Replace CONVERSATION_ID with actual UUID
curl -X GET http://localhost:8000/api/chat/conversations/CONVERSATION_ID/ \
  -b cookies.txt
```

### 9. Get Messages from a Conversation

```bash
# Replace CONVERSATION_ID with actual UUID
curl -X GET "http://localhost:8000/api/chat/conversations/CONVERSATION_ID/messages/?limit=50" \
  -b cookies.txt
```

## WebSocket Connection

### 10. Connect to WebSocket (JavaScript)

```javascript
// In browser console or JavaScript file
const conversationId = "YOUR_CONVERSATION_UUID";
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}/`);

socket.onopen = function (e) {
  console.log("Connected to chat");
};

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

// Send a message
socket.send(
  JSON.stringify({
    type: "message",
    content: "Hello, everyone!",
  })
);

// Send typing indicator
socket.send(
  JSON.stringify({
    type: "typing",
    is_typing: true,
  })
);

// Mark as read
socket.send(
  JSON.stringify({
    type: "read",
  })
);
```

## Complete Workflow Example

### Step-by-Step: Create Users and Start Chatting

```bash
# 1. Register User 1
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Johnson",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }' \
  -c alice_cookies.txt

# 2. Register User 2
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "first_name": "Bob",
    "last_name": "Smith",
    "password": "SecurePass456",
    "password_confirm": "SecurePass456"
  }' \
  -c bob_cookies.txt

# 3. Login as Alice
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }' \
  -c alice_cookies.txt -b alice_cookies.txt

# 4. Get list of users as Alice (to find Bob's ID)
curl -X GET http://localhost:8000/api/users/list/ \
  -b alice_cookies.txt

# 5. Create a conversation between Alice and Bob
# Replace USER_IDS with actual IDs from step 4
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2]
  }' \
  -b alice_cookies.txt

# 6. The response will include the conversation ID
# Use it to retrieve messages
curl -X GET http://localhost:8000/api/chat/conversations/CONVERSATION_ID/messages/ \
  -b alice_cookies.txt

# 7. Now open the WebSocket connection (use example_client.html)
# Or use wscat:
# npm install -g wscat
# wscat -c ws://localhost:8000/ws/chat/CONVERSATION_ID/
```

## Testing Rate Limiting

```bash
# This will trigger rate limiting after 10 requests
for i in {1..15}; do
  curl -X GET "http://localhost:8000/api/chat/conversations/CONVERSATION_ID/messages/" \
    -b cookies.txt
  echo "\nRequest $i completed"
  sleep 1
done
```

## Health Check

```bash
curl -X GET http://localhost:8000/api/chat/health/
```

## Logout

```bash
curl -X POST http://localhost:8000/api/users/logout/ \
  -b cookies.txt
```

## Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Create a session to handle cookies
session = requests.Session()

# Register
response = session.post(f"{BASE_URL}/users/register/", json={
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "TestPass123",
    "password_confirm": "TestPass123"
})
print("Register:", response.json())

# Login
response = session.post(f"{BASE_URL}/users/login/", json={
    "email": "test@example.com",
    "password": "TestPass123"
})
print("Login:", response.json())

# Get profile
response = session.get(f"{BASE_URL}/users/profile/")
print("Profile:", response.json())

# List conversations
response = session.get(f"{BASE_URL}/chat/conversations/")
print("Conversations:", response.json())
```

## WebSocket Testing with Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    # Replace with your conversation ID
    conversation_id = "YOUR_CONVERSATION_UUID"
    uri = f"ws://localhost:8000/ws/chat/{conversation_id}/"

    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")

        # Send a message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "Hello from Python!"
        }))

        # Receive messages
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data}")

# Run the test
asyncio.run(test_websocket())
```

## Notes

- All API endpoints (except health check and registration/login) require authentication
- Session cookies are used for authentication
- WebSocket connections must be authenticated (cookies are sent automatically by the browser)
- Rate limiting is enforced on message retrieval endpoints (10 requests/minute)
- Messages in Redis expire after 24 hours by default
