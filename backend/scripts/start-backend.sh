#!/bin/bash
set -e

echo "Waiting for database..."
max_retries=30
retry_count=0

# Use Python to parse DATABASE_URL reliably
DB_PARSED=$(python3 -c "
import urllib.parse
import sys
try:
    url = urllib.parse.urlparse('$DATABASE_URL')
    print(f'{url.hostname} {url.port or 5432} {url.username}')
except:
    print('db 5432 snake_user')
    sys.exit(1)
")

read DB_HOST DB_PORT DB_USER <<< "$DB_PARSED"

echo "Database host: $DB_HOST"
echo "Database port: $DB_PORT"
echo "Database user: $DB_USER"

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
  echo "Database not ready, waiting... ($retry_count/$max_retries)"
  retry_count=$((retry_count + 1))
  sleep 2
done

if [ $retry_count -eq $max_retries ]; then
  echo "ERROR: Database failed to become ready after $max_retries attempts"
  echo "Last connection attempt: pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER"
  exit 1
fi

echo "Database ready!"
echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting Uvicorn server..."
exec uv run uvicorn main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 2 \
  --log-level info
