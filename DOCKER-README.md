# Docker Setup for Snake Playground Pro

Your application has been successfully containerized with Docker Compose! 🐳

## What's Running

- **PostgreSQL** (port 5432) - Database with persistent volumes
- **Backend** (port 8000) - FastAPI with auto-migrations
- **Frontend** (ports 80 & 8080) - Nginx serving React app

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (destroys data!)
docker-compose down -v
```

## Using the Helper Script

```bash
# Start services
./docker-dev.sh up

# View logs (all services)
./docker-dev.sh logs

# View logs (specific service)
./docker-dev.sh logs backend

# Restart a service
./docker-dev.sh restart backend

# Access backend shell
./docker-dev.sh shell-backend

# Access PostgreSQL
./docker-dev.sh shell-db

# Run migrations manually
./docker-dev.sh migrate

# Create new migration
./docker-dev.sh migrate-create "description"

# Reset database (destroys all data!)
./docker-dev.sh reset-db

# Stop services
./docker-dev.sh down
```

## Access Points

### Local Development
- **Frontend**: http://localhost or http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Database**: `postgresql://snake_user:snake_password_dev@localhost:5432/snake_playground`

### GitHub Codespaces
- **Frontend**: https://${CODESPACE_NAME}-80.app.github.dev
- **Backend API**: https://${CODESPACE_NAME}-8000.app.github.dev/api/v1/docs
- **Note**: Ports 80, 8000, and 8080 are automatically configured for public visibility
- **Port Visibility**: All ports are set to public to avoid login issues

## How It Works

### Database
- **PostgreSQL 16** running in Alpine Linux container
- Data persisted in Docker volume `postgres_data`
- Automatic health checks every 10 seconds

### Backend
- **Python 3.12** with FastAPI and UV package manager
- Auto-runs Alembic migrations on startup
- Hot reload enabled (code changes trigger auto-restart)
- Source code mounted as volume for development

### Frontend
- **Multi-stage build**: Node 20 → Nginx Alpine
- Vite builds optimized production bundle
- Nginx serves static files with gzip compression
- SPA routing configured for React Router

## Development Workflow

1. **Make code changes** in `backend/` or `frontend/`
2. **Backend**: Changes auto-reload immediately
3. **Frontend**: Rebuild container with `docker-compose up -d --build frontend`

## Database Operations

### Connect to PostgreSQL
```bash
docker exec -it snake_postgres psql -U snake_user -d snake_playground
```

### Common SQL Commands
```sql
-- List tables
\dt

-- View users
SELECT * FROM users;

-- View leaderboard
SELECT * FROM leaderboard ORDER BY score DESC;

-- Quit
\q
```

### Run Migrations
```bash
# Upgrade to latest
docker exec snake_backend uv run alembic upgrade head

# Create new migration
docker exec snake_backend uv run alembic revision --autogenerate -m "description"

# Check current version
docker exec snake_backend uv run alembic current
```

## Migrating Existing SQLite Data

If you have existing SQLite data to migrate:

```bash
# Make sure containers are running
docker-compose up -d

# Run migration script
docker exec -it snake_backend uv run python scripts/migrate_sqlite_to_postgres.py
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :80

# Change ports in docker-compose.yml if needed
```

### Backend Can't Connect to Database
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection from backend
docker exec snake_backend pg_isready -h db -U snake_user
```

### Migrations Failing
```bash
# Check migration status
docker exec snake_backend uv run alembic current

# View migration history
docker exec snake_backend uv run alembic history

# Reset database (DESTRUCTIVE!)
docker-compose down -v
docker-compose up -d
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Test nginx config
docker exec snake_frontend nginx -t
```

### Clear Everything and Start Fresh
```bash
# Stop containers and remove volumes
docker-compose down -v

# Remove images
docker rmi snake-playground-pro-backend snake-playground-pro-frontend

# Rebuild from scratch
docker-compose up -d --build
```

## Container Management

```bash
# View container status
docker-compose ps

# View resource usage
docker stats

# View container details
docker inspect snake_backend

# Execute command in container
docker exec snake_backend env | grep DATABASE
```

## Production Deployment Notes

For production deployment, you should:

1. **Change passwords** in docker-compose.yml
2. **Use secrets** instead of environment variables
3. **Remove volume mounts** for backend
4. **Disable auto-reload** on backend
5. **Add SSL/TLS** certificates
6. **Configure resource limits**
7. **Set up proper backup strategy**
8. **Use production-grade PostgreSQL configuration**

## File Structure

```
.
├── docker-compose.yml       # Main orchestration file
├── docker-dev.sh            # Helper script
├── backend/
│   ├── Dockerfile          # Backend container definition
│   ├── .dockerignore       # Files to exclude from build
│   └── .env.docker         # Docker-specific env vars
└── frontend/
    ├── Dockerfile          # Frontend container definition
    ├── .dockerignore       # Files to exclude from build
    └── nginx.conf          # Nginx web server config
```

## Health Checks

All services have health checks configured:

- **PostgreSQL**: `pg_isready` every 10s
- **Backend**: `/health` endpoint every 30s
- **Frontend**: HTTP GET to root every 30s

View health status:
```bash
docker-compose ps
```

## Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail=50 backend

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00
```

## Need Help?

- Check the logs: `docker-compose logs -f`
- View container status: `docker-compose ps`
- Inspect a container: `docker inspect <container-name>`
- Access container shell: `docker exec -it <container-name> sh`

---

**Note**: The warning about `version` being obsolete in docker-compose.yml can be safely ignored. It's a deprecation notice from Docker Compose.
