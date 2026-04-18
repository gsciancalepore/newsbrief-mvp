#!/bin/bash
set -e

echo "[ENTRYPOINT] Starting application..."

# Extract database connection details from DATABASE_URL
# Format: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL="${DATABASE_URL}"

if [ -z "$DATABASE_URL" ]; then
    echo "[ENTRYPOINT] ERROR: DATABASE_URL not set!"
    exit 1
fi

# Parse DB_HOST, DB_USER, DB_PASSWORD, DB_NAME from DATABASE_URL
# Remove the driver prefix
DB_URL_NO_DRIVER="${DATABASE_URL#*://}"

# Extract user:password@host:port/dbname
CREDENTIALS_HOST_DB="${DB_URL_NO_DRIVER%%@*}"
HOST_PORT_DB="${DB_URL_NO_DRIVER#*@}"

# Parse credentials
DB_USER=$(echo "$CREDENTIALS_HOST_DB" | cut -d':' -f1)
DB_PASSWORD=$(echo "$CREDENTIALS_HOST_DB" | cut -d':' -f2- | tr -d ':')

# Parse host:port/dbname
DB_HOST=$(echo "$HOST_PORT_DB" | cut -d':' -f1)
PORT_DB=$(echo "$HOST_PORT_DB" | cut -d':' -f2- | tr -d ':')
DB_NAME=$(echo "$PORT_DB" | cut -d'/' -f2)
DB_PORT=$(echo "$PORT_DB" | cut -d'/' -f1 | cut -d':' -f2)

echo "[ENTRYPOINT] DATABASE_URL: $DATABASE_URL"
echo "[ENTRYPOINT] Wait for database at $DB_HOST:$DB_PORT..."

# Wait for database to be ready
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    echo "[ENTRYPOINT] Database unavailable - sleeping"
    sleep 1
done

echo "[ENTRYPOINT] Database is ready!"

# Run Alembic migrations
echo "[ENTRYPOINT] Running database migrations..."
alembic upgrade head

echo "[ENTRYPOINT] Migrations completed successfully!"

# Start Uvicorn
echo "[ENTRYPOINT] Starting Uvicorn..."
exec uvicorn src.interfaces.api.main:app --host 0.0.0.0 --port 8000