# Real-Time Chat Application

A production-ready real-time chat application built with Django, WebSockets, Redis, and PostgreSQL. This application supports real-time messaging, user authentication, conversation management, and includes comprehensive API throttling and logging.

![CI/CD](https://github.com/yourusername/realtimeMessage/workflows/CI/CD%20Pipeline/badge.svg)

## 🚀 Features

- **Real-time messaging** using WebSockets (Django Channels)
- **User authentication** with email-based registration
- **Message persistence** in Redis for fast access (24-hour TTL)
- **Conversation management** (1-on-1 and group chats)
- **API throttling** (10 requests/minute for messages)
- **Comprehensive logging** of all API calls
- **Form validation** with detailed error messages
- **Typing indicators** and read receipts
- **RESTful API** with consistent JSON responses
- **Docker support** for easy deployment
- **Automated testing** with pytest
- **CI/CD pipeline** with GitHub Actions

## 📋 Table of Contents

- [Technologies](#technologies)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [WebSocket Protocol](#websocket-protocol)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🛠 Technologies

- **Backend**: Python 3.11, Django 4.2
- **Real-time**: Django Channels, WebSockets
- **Database**: PostgreSQL 15
- **Cache/Message Store**: Redis 7
- **API**: Django REST Framework
- **Testing**: pytest, pytest-django, pytest-asyncio
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 🏗 Architecture

### System Overview

```
┌─────────────┐         ┌─────────────┐
│   Client    │◄───────►│   Django    │
│ (WebSocket) │         │  Channels   │
└─────────────┘         └──────┬──────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Redis     │
                        │ (Channel     │
                        │  Layer &     │
                        │  Messages)   │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  PostgreSQL  │
                        │    (Users    │
                        │     & Conv)  │
                        └──────────────┘
```

### Data Storage Strategy

- **PostgreSQL**: User accounts, conversation metadata
- **Redis**:
  - Real-time messages (sorted sets with 24h TTL)
  - Channel layer for WebSocket communication
  - Unread message counters
  - Rate limiting cache

## 📦 Installation

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+, PostgreSQL 15+, Redis 7+

### Option 1: Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/realtimeMessage.git
   cd realtimeMessage
   ```

2. **Start all services**

   ```bash
   docker-compose up --build
   ```

3. **Access the application**

   - API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

4. **Create a superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Option 2: Local Development

1. **Clone and setup virtual environment**

   ```bash
   git clone https://github.com/yourusername/realtimeMessage.git
   cd realtimeMessage
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis credentials
   ```

4. **Start PostgreSQL and Redis**

   ```bash
   # Using Docker for just the databases
   docker run -d -p 5432:5432 -e POSTGRES_DB=chatdb -e POSTGRES_USER=chatuser -e POSTGRES_PASSWORD=chatpassword postgres:15-alpine
   docker run -d -p 6379:6379 redis:7-alpine
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   daphne -b 0.0.0.0 -p 8000 chat_project.asgi:application
   ```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api
```

### Authentication

The API uses session-based authentication. After logging in, the session cookie will be used for subsequent requests.

### Response Format

All API responses follow this structure:

**Success Response:**

```json
{
  "status": "success",
  "message": "Operation successful",
  "data": { ... }
}
```

**Error Response:**

```json
{
  "status": "error",
  "message": "Error description",
  "errors": { ... }
}
```

### User Endpoints

#### Register User

```http
POST /api/users/register/
Content-Type: application/json

{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}
```

**Validation Rules:**

- Email: Valid email format, unique
- First/Last Name: Min 2 characters, letters only
- Password: Min 8 characters
- Passwords must match

**Response:** `201 Created`

```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

#### Login

```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`

#### Logout

```http
POST /api/users/logout/
```

**Response:** `200 OK`

#### Get Profile

```http
GET /api/users/profile/
```

**Response:** `200 OK` (Returns current user's profile)

#### List Users

```http
GET /api/users/list/
```

**Response:** `200 OK` (Returns all users except current user)

### Chat Endpoints

#### Create Conversation

```http
POST /api/chat/conversations/
Content-Type: application/json

{
  "participant_ids": [1, 2],
  "name": "Optional Group Name"
}
```

**Notes:**

- Minimum 2 participants
- Automatically creates group chat if > 2 participants
- Returns existing conversation for 1-on-1 chats

**Response:** `201 Created`

```json
{
  "status": "success",
  "message": "Conversation created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": null,
    "display_name": "Chat with Jane Smith",
    "is_group": false,
    "participants": [...],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### List Conversations

```http
GET /api/chat/conversations/
```

**Response:** `200 OK`

```json
{
  "status": "success",
  "data": [
    {
      "id": "...",
      "name": "...",
      "message_count": 42,
      "unread_count": 5,
      ...
    }
  ]
}
```

#### Get Conversation Details

```http
GET /api/chat/conversations/{conversation_id}/
```

**Response:** `200 OK`

#### Get Messages

```http
GET /api/chat/conversations/{conversation_id}/messages/?limit=50&offset=0
```

**Query Parameters:**

- `limit`: Max messages to retrieve (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)

**Rate Limit:** 10 requests/minute per user

**Response:** `200 OK`

```json
{
  "status": "success",
  "data": {
    "conversation_id": "...",
    "messages": [
      {
        "id": "msg-uuid",
        "conversation_id": "...",
        "sender_id": 1,
        "sender_name": "John Doe",
        "sender_email": "john@example.com",
        "content": "Hello!",
        "timestamp": 1234567890.0,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "count": 50,
    "total": 150
  }
}
```

### Health Check

```http
GET /api/chat/health/
```

**Response:** `200 OK`

## 🔌 WebSocket Protocol

### Connect to Conversation

```
ws://localhost:8000/ws/chat/{conversation_id}/
```

**Requirements:**

- User must be authenticated
- User must be a participant in the conversation

### Connection Established

```json
{
  "type": "connection_established",
  "message": "Connected to chat",
  "conversation_id": "..."
}
```

### Send Message

```json
{
  "type": "message",
  "content": "Hello, world!"
}
```

### Receive Message

```json
{
  "type": "message",
  "message": {
    "id": "msg-uuid",
    "conversation_id": "...",
    "sender_id": 1,
    "sender_name": "John Doe",
    "sender_email": "john@example.com",
    "content": "Hello, world!",
    "timestamp": 1234567890.0,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Typing Indicator

```json
// Send
{
  "type": "typing",
  "is_typing": true
}

// Receive
{
  "type": "typing",
  "user_id": 1,
  "user_name": "John Doe",
  "is_typing": true
}
```

### Read Receipt

```json
{
  "type": "read"
}
```

### Error Response

```json
{
  "type": "error",
  "message": "Error description"
}
```

## 🧪 Running Tests

### Using Docker

```bash
docker-compose exec web pytest
```

### With Coverage

```bash
docker-compose exec web pytest --cov=. --cov-report=html
```

### Locally

```bash
# Make sure PostgreSQL and Redis are running
pytest
pytest --cov=. --cov-report=html
```

### Test Categories

- **Unit Tests**: User models, serializers, utilities
- **Integration Tests**: API endpoints, authentication flows
- **WebSocket Tests**: Real-time messaging functionality

## 🚀 Deployment

### Docker Compose (Production)

1. **Update environment variables**

   ```bash
   # Edit docker-compose.yml with production values
   # Set DEBUG=False
   # Use strong SECRET_KEY
   # Configure allowed hosts
   ```

2. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment Options

#### Heroku

```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
heroku run python manage.py migrate
```

#### AWS (ECS + RDS + ElastiCache)

1. Create RDS PostgreSQL instance
2. Create ElastiCache Redis cluster
3. Build and push Docker image to ECR
4. Deploy to ECS/Fargate
5. Configure load balancer for WebSocket support

#### Google Cloud (Cloud Run + Cloud SQL + Memorystore)

1. Create Cloud SQL PostgreSQL instance
2. Create Memorystore Redis instance
3. Build and deploy to Cloud Run
4. Configure for WebSocket connections

## 📁 Project Structure

```
realtimeMessage/
├── chat/                      # Chat application
│   ├── consumers.py          # WebSocket consumers
│   ├── models.py             # Conversation model
│   ├── redis_manager.py      # Redis message storage
│   ├── serializers.py        # API serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   ├── routing.py            # WebSocket routing
│   ├── middleware.py         # API logging
│   ├── throttling.py         # Rate limiting
│   ├── exceptions.py         # Error handling
│   └── tests.py              # Tests
├── users/                     # User management
│   ├── models.py             # Custom User model
│   ├── serializers.py        # User serializers
│   ├── views.py              # Authentication views
│   ├── urls.py               # User URLs
│   └── tests.py              # User tests
├── chat_project/             # Django project
│   ├── settings.py           # Configuration
│   ├── urls.py               # Main URL config
│   ├── asgi.py               # ASGI config
│   └── wsgi.py               # WSGI config
├── logs/                      # Application logs
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Docker image
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── manage.py                 # Django management
└── README.md                 # This file
```

## 🔒 Security Features

- **Password hashing** using Django's PBKDF2
- **CSRF protection** for API endpoints
- **Session security** with secure cookies
- **Input validation** on all user inputs
- **SQL injection protection** via Django ORM
- **XSS protection** via Django templates
- **Rate limiting** to prevent abuse
- **CORS configuration** for cross-origin requests

## 📊 Logging & Monitoring

### Log Files

- `logs/django.log` - General application logs
- `logs/api.log` - API request/response logs

### Log Format

```
2024-01-01 12:00:00 INFO API Request: POST /api/users/login/ - User: anonymous - IP: 127.0.0.1
2024-01-01 12:00:00 INFO API Response: POST /api/users/login/ - Status: 200 - Duration: 0.123s
```

### Monitoring

All API calls are logged with:

- HTTP method and path
- User ID (or anonymous)
- Client IP address
- Response status code
- Request duration

## ⚡ API Throttling

### Rate Limits

- **Anonymous users**: 20 requests/minute
- **Authenticated users**: 100 requests/minute
- **Message endpoints**: 10 requests/minute (additional limit)

### Throttle Response

```http
HTTP 429 Too Many Requests

{
  "status": "error",
  "message": "Request was throttled. Expected available in X seconds."
}
```

## 🐛 Troubleshooting

### WebSocket Connection Issues

1. Ensure Redis is running
2. Check that user is authenticated
3. Verify user is a conversation participant
4. Check browser console for errors

### Database Connection Errors

1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure database exists and is accessible

### Redis Connection Errors

1. Verify Redis is running on the correct port
2. Check Redis host in settings
3. Ensure firewall allows connection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Django Channels documentation
- Redis documentation
- Django REST Framework guides

---

**Built with ❤️ using Django, Channels, and Redis**
