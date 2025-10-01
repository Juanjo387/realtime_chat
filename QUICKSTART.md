# Quick Start Guide

Get the real-time chat application running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+, PostgreSQL, and Redis

## Option 1: Docker (Fastest - Recommended)

### 1. Start the Application

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd realtimeMessage

# Start all services with Docker Compose
docker-compose up --build
```

Wait for the services to start. You should see:

```
web_1    | PostgreSQL started
web_1    | Redis started
web_1    | Running migrations...
web_1    | Collecting static files...
```

### 2. Verify It's Running

Open your browser and go to:

- API Health Check: http://localhost:8000/api/chat/health/

You should see:

```json
{
  "status": "success",
  "message": "API is running"
}
```

### 3. Create Test Users

```bash
# In a new terminal, register two users
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@test.com",
    "first_name": "Alice",
    "last_name": "Smith",
    "password": "TestPass123",
    "password_confirm": "TestPass123"
  }' \
  -c alice.txt

curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@test.com",
    "first_name": "Bob",
    "last_name": "Jones",
    "password": "TestPass123",
    "password_confirm": "TestPass123"
  }' \
  -c bob.txt
```

### 4. Create a Conversation

```bash
# Login as Alice
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@test.com",
    "password": "TestPass123"
  }' \
  -c alice.txt -b alice.txt

# Create a conversation between Alice (ID: 1) and Bob (ID: 2)
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": [1, 2]
  }' \
  -b alice.txt

# Note the conversation ID from the response (UUID format)
```

### 5. Test Real-Time Messaging

**Option A: Use the HTML Client**

1. Open `example_client.html` in your browser
2. Enter the conversation ID from step 4
3. Click "Connect"
4. Start chatting!

**Option B: Use Browser Console**

Open browser console and run:

```javascript
// Replace with your conversation ID
const conversationId = "YOUR-UUID-HERE";
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}/`);

socket.onopen = () => console.log("Connected!");
socket.onmessage = (e) => console.log("Received:", JSON.parse(e.data));

// Send a message
socket.send(
  JSON.stringify({
    type: "message",
    content: "Hello from the browser!",
  })
);
```

### 6. View Logs

```bash
# View application logs
docker-compose logs -f web

# View just Django logs
docker-compose exec web tail -f logs/django.log

# View API logs
docker-compose exec web tail -f logs/api.log
```

### 7. Run Tests

```bash
docker-compose exec web pytest
```

### 8. Access Admin Panel

```bash
# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Then visit http://localhost:8000/admin
```

## Option 2: Local Development (Without Docker)

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL and Redis

```bash
# Using Docker for databases only
docker run -d --name chatdb -p 5432:5432 \
  -e POSTGRES_DB=chatdb \
  -e POSTGRES_USER=chatuser \
  -e POSTGRES_PASSWORD=chatpassword \
  postgres:15-alpine

docker run -d --name chatredis -p 6379:6379 redis:7-alpine
```

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=chatdb
DB_USER=chatuser
DB_PASSWORD=chatpassword
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
MESSAGE_EXPIRY=86400
EOF
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start the Server

```bash
# Using Daphne (ASGI server for WebSockets)
daphne -b 0.0.0.0 -p 8000 chat_project.asgi:application

# OR using Django development server (WebSockets may not work)
# python manage.py runserver
```

### 6. Follow Steps 3-5 from Docker Instructions

The API endpoints and testing steps are the same!

## Common Commands

### Docker

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web pytest

# Shell access
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec web python manage.py dbshell
```

### Local Development

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

## Testing the Full Workflow

Here's a complete test scenario:

### 1. Register Users

```bash
# Register Alice
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","first_name":"Alice","last_name":"Smith","password":"Pass123","password_confirm":"Pass123"}' \
  -c alice.txt

# Register Bob
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@test.com","first_name":"Bob","last_name":"Jones","password":"Pass123","password_confirm":"Pass123"}' \
  -c bob.txt
```

### 2. Login

```bash
# Alice logs in
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"Pass123"}' \
  -c alice.txt -b alice.txt

# Bob logs in
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@test.com","password":"Pass123"}' \
  -c bob.txt -b bob.txt
```

### 3. Create Conversation

```bash
# Alice creates a conversation with Bob
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"participant_ids":[1,2]}' \
  -b alice.txt | jq .
```

Save the conversation ID from the response.

### 4. Connect with WebSocket

Open two browser windows with `example_client.html`:

1. In first window, enter the conversation ID and connect
2. In second window, enter the same conversation ID and connect
3. Send messages from either window
4. See real-time delivery in both!

### 5. Retrieve Message History

```bash
# Get messages from the conversation
curl -X GET "http://localhost:8000/api/chat/conversations/YOUR_CONV_ID/messages/" \
  -b alice.txt | jq .
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
docker-compose run -p 8001:8000 web
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart db
```

### Redis Connection Error

```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis
docker-compose restart redis
```

### WebSocket Connection Failed

1. Ensure you're logged in (have valid session cookie)
2. Check that you're a participant in the conversation
3. Verify Redis is running
4. Check browser console for detailed error messages

### Tests Failing

```bash
# Make sure databases are running
docker-compose up -d db redis

# Run tests with verbose output
pytest -v

# Run specific test
pytest chat/tests.py::TestConversationCreation -v
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) for more API usage examples
3. Explore the admin panel at http://localhost:8000/admin
4. Read the code to understand the architecture
5. Add new features and customize!

## API Endpoints Summary

| Endpoint                                 | Method    | Description              |
| ---------------------------------------- | --------- | ------------------------ |
| `/api/users/register/`                   | POST      | Register a new user      |
| `/api/users/login/`                      | POST      | Login                    |
| `/api/users/logout/`                     | POST      | Logout                   |
| `/api/users/profile/`                    | GET       | Get current user profile |
| `/api/users/list/`                       | GET       | List all users           |
| `/api/chat/conversations/`               | GET       | List conversations       |
| `/api/chat/conversations/`               | POST      | Create conversation      |
| `/api/chat/conversations/{id}/`          | GET       | Get conversation details |
| `/api/chat/conversations/{id}/messages/` | GET       | Get messages             |
| `/api/chat/health/`                      | GET       | Health check             |
| `/ws/chat/{conversation_id}/`            | WebSocket | Real-time messaging      |

## Support

- Check the logs: `docker-compose logs -f web`
- Run tests: `docker-compose exec web pytest`
- Access Django shell: `docker-compose exec web python manage.py shell`

Happy chatting! 🎉
