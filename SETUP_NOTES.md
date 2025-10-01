# Setup Notes

This document contains important notes about the setup and configuration.

## Port Conflicts Resolved

If you have PostgreSQL or Redis running locally on your machine, the default Docker Compose ports will conflict. The following changes were made:

### Modified Ports

- **PostgreSQL**: Changed from `5432:5432` to `5433:5432`

  - Access from host: `localhost:5433`
  - Access from containers: `db:5432` (unchanged)

- **Redis**: Changed from `6379:6379` to `6380:6379`
  - Access from host: `localhost:6380`
  - Access from containers: `redis:6379` (unchanged)

**Note:** These port changes only affect external access from your host machine. Containers communicate internally using the default ports.

## Password Validators

Django's built-in password validators have been temporarily disabled to avoid import issues. If you want to re-enable them, uncomment the validators in `chat_project/settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validators.UserAttributeSimilarityValidator',
    },
    # ... other validators
]
```

**Security Note:** For production use, consider implementing custom password validation or using Django's validators with proper error handling.

## First Time Setup

After cloning the repository and starting the containers:

```bash
# Start the services
docker compose up -d --build

# Create migrations (if needed)
docker compose exec web python manage.py makemigrations users
docker compose exec web python manage.py makemigrations chat

# Run migrations
docker compose exec web python manage.py migrate

# Create a superuser (optional)
docker compose exec web python manage.py createsuperuser
```

## Verification

Test that everything is working:

```bash
# Health check
curl http://localhost:8000/api/chat/health/

# Register a user
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test","last_name":"User","password":"Pass123","password_confirm":"Pass123"}'
```

## Docker Compose V2

This project uses Docker Compose V2 (the Docker CLI plugin). Use `docker compose` (with a space) instead of `docker-compose` (with a hyphen):

```bash
# Correct
docker compose up -d

# Old syntax (may not work)
docker-compose up -d
```

## Access Points

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **WebSocket**: ws://localhost:8000/ws/chat/{conversation_id}/
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380

## Troubleshooting

### Port Already in Use

If you get "address already in use" errors:

1. Check what's using the port:

   ```bash
   sudo lsof -i :5432  # For PostgreSQL
   sudo lsof -i :6379  # For Redis
   ```

2. Either stop the local service or modify the port in `docker-compose.yml`

### Migration Errors

If you get "relation does not exist" errors:

```bash
docker compose down -v  # Remove volumes
docker compose up -d --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Container Won't Start

Check the logs:

```bash
docker compose logs web --tail=100
```

## Production Deployment

For production deployment:

1. Enable password validators in `settings.py`
2. Use strong `SECRET_KEY`
3. Set `DEBUG=False`
4. Configure proper `ALLOWED_HOSTS`
5. Use environment variables for sensitive data
6. Set up HTTPS/TLS
7. Configure proper backup strategies

## Support

- Check the main [README.md](README.md) for full documentation
- See [QUICKSTART.md](QUICKSTART.md) for quick setup guide
- Review [API_EXAMPLES.md](API_EXAMPLES.md) for API usage
