#!/bin/bash
set -e

echo "Waiting for database..."
max_retries=30
retry_count=0

# Extract database connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')

until pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-snake_user} || [ $retry_count -eq $max_retries ]; do
  echo "Database not ready, waiting... ($retry_count/$max_retries)"
  retry_count=$((retry_count + 1))
  sleep 2
done

if [ $retry_count -eq $max_retries ]; then
  echo "ERROR: Database failed to become ready"
  exit 1
fi

echo "Database ready!"
echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting Uvicorn server..."
exec uv run uvicorn main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 4 \
  --log-level info
