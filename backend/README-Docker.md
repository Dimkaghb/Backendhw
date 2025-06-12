# FastAPI Todo App - Docker Setup

This document explains how to run the FastAPI Todo application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start all services** (FastAPI app + MongoDB + Mongo Express):
   ```bash
   docker-compose up -d
   ```

2. **Access the application**:
   - FastAPI App: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express (Web UI): http://localhost:8081 (admin/admin123)

3. **Stop all services**:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker only

1. **Build the image**:
   ```bash
   docker build -t fastapi-todo .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name fastapi-todo-app \
     -p 8000:8000 \
     -e MONGO_DB_URL="mongodb://host.docker.internal:27017/todo" \
     fastapi-todo
   ```

## Environment Variables

You can customize the application using these environment variables:

- `MONGO_DB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

## Development

### Building for development

```bash
# Build the image
docker build -t fastapi-todo-dev .

# Run with volume mounting for development
docker run -d \
  --name fastapi-todo-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  fastapi-todo-dev
```

### Logs

```bash
# View application logs
docker logs fastapi-todo-app

# Follow logs in real-time
docker logs -f fastapi-todo-app
```

## Services Overview

When using docker-compose, the following services are started:

1. **fastapi-app** (Port 8000): The main FastAPI application
2. **mongodb** (Port 27017): MongoDB database
3. **mongo-express** (Port 8081): Web-based MongoDB admin interface

## API Endpoints

Once running, you can access these endpoints:

- `POST /signup` - Create a new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user info (requires auth)
- `POST /create_task` - Create a new task (requires auth)
- `GET /get_tasks` - Get all user tasks (requires auth)

## Testing

You can test the API using the included test script:

```bash
# Run tests inside the container
docker exec fastapi-todo-app python test_api.py
```

## Troubleshooting

### Container won't start
- Check logs: `docker logs fastapi-todo-app`
- Ensure ports 8000, 27017, and 8081 are not in use

### MongoDB connection issues
- Verify MongoDB container is running: `docker ps`
- Check MongoDB logs: `docker logs mongodb-todo`

### Permission issues
- The application runs as a non-root user for security
- Ensure file permissions are correct if mounting volumes 