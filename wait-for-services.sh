#!/bin/bash
# ============================================================================
# wait-for-services.sh
# ----------------------------------------------------------------------------
# Purpose:
#   - Wait for PostgreSQL & Redis
#   - Validate superuser connection
#   - Create database if missing
#   - Create admin user if missing
#   - Grant privileges safely
#   - Run migrations (if Alembic installed)
#   - Start backend (Uvicorn)
#
# Safety:
#   - Does NOT recreate existing DB
#   - Does NOT overwrite existing users
#   - Data is persistent across container restarts
#   - Uses .pgpass for passwordless commands
# ============================================================================
set -e

# ============================================================================
# Load environment variables (with defaults)
# ============================================================================
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-mrwa}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-mrwa_password}
POSTGRES_DB=${DATABASE_NAME:-mrwa}

# Admin account
ADMIN_USER=${ADMIN_USER:-admin}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}

# Superuser
SUPERUSER=${SUPERUSER:-postgres}
SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD:-$POSTGRES_PASSWORD}

REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

STORAGE_PATH=${STORAGE_PATH:-/app/storage}

MAX_WAIT=120
SLEEP_INTERVAL=2

# ============================================================================
# Display configuration
# ============================================================================
echo "================================================"
echo "🚀 Backend startup configuration"
echo "DB Host     : $POSTGRES_HOST"
echo "DB Name     : $POSTGRES_DB"
echo "DB User     : $POSTGRES_USER"
echo "Admin       : $ADMIN_USER"
echo "Redis       : $REDIS_HOST:$REDIS_PORT"
echo "Storage     : $STORAGE_PATH"
echo "Superuser   : $SUPERUSER"
echo "================================================"

# ============================================================================
# Ensure storage folder exists
# ============================================================================
mkdir -p "$STORAGE_PATH"

# ============================================================================
# Create .pgpass for passwordless psql commands
# ============================================================================
PGPASS_FILE="$HOME/.pgpass"
echo "$POSTGRES_HOST:$POSTGRES_PORT:*:$POSTGRES_USER:$POSTGRES_PASSWORD" > "$PGPASS_FILE"
echo "$POSTGRES_HOST:$POSTGRES_PORT:*:$SUPERUSER:$SUPERUSER_PASSWORD" >> "$PGPASS_FILE"
chmod 600 "$PGPASS_FILE"
export PGPASSFILE="$PGPASS_FILE"
echo "✅ .pgpass file created at $PGPASS_FILE"

# ============================================================================
# Function: wait for PostgreSQL
# ============================================================================
wait_for_postgres() {
  echo "⏳ Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
  TIME_WAITED=0
  until psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c '\q' >/dev/null 2>&1; do
    if [ "$TIME_WAITED" -ge "$MAX_WAIT" ]; then
      echo "❌ PostgreSQL not ready after $MAX_WAIT seconds"
      exit 1
    fi
    sleep $SLEEP_INTERVAL
    TIME_WAITED=$((TIME_WAITED + SLEEP_INTERVAL))
  done
  echo "✅ PostgreSQL is ready"
}

# ============================================================================
# Function: validate superuser
# ============================================================================
validate_superuser() {
  echo "🔒 Validating PostgreSQL superuser '$SUPERUSER'..."
  if ! psql -h "$POSTGRES_HOST" -U "$SUPERUSER" -d postgres -c '\q' >/dev/null 2>&1; then
    echo "❌ Cannot connect as superuser '$SUPERUSER'. Check SUPERUSER_PASSWORD"
    exit 1
  fi
  echo "✅ Superuser validated"
}

# ============================================================================
# Function: create database if missing
# ============================================================================
create_database() {
  echo "🔍 Ensuring database '$POSTGRES_DB' exists..."
  psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB') THEN
      CREATE DATABASE $POSTGRES_DB;
   END IF;
END
\$\$;
SQL
  echo "✅ Database ensured"
}

# ============================================================================
# Function: create admin user if missing
# ============================================================================
create_admin_user() {
  echo "🔍 Ensuring admin user '$ADMIN_USER' exists..."
  psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$ADMIN_USER') THEN
      CREATE ROLE $ADMIN_USER LOGIN PASSWORD '$ADMIN_PASSWORD';
   END IF;
END
\$\$;
SQL
  echo "✅ Admin user ensured"
}

# ============================================================================
# Function: grant privileges
# ============================================================================
grant_privileges() {
  echo "🔑 Granting privileges on '$POSTGRES_DB' to '$ADMIN_USER'..."
  psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres <<SQL
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $ADMIN_USER;
SQL
  echo "✅ Privileges granted"
}

# ============================================================================
# Function: wait for Redis
# ============================================================================
wait_for_redis() {
  echo "⏳ Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
  TIME_WAITED=0
  until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q PONG; do
    if [ "$TIME_WAITED" -ge "$MAX_WAIT" ]; then
      echo "❌ Redis not ready after $MAX_WAIT seconds"
      exit 1
    fi
    sleep $SLEEP_INTERVAL
    TIME_WAITED=$((TIME_WAITED + SLEEP_INTERVAL))
  done
  echo "✅ Redis is ready"
}

# ============================================================================
# Function: run migrations (optional)
# ============================================================================
run_migrations() {
  if command -v alembic >/dev/null 2>&1; then
    echo "📦 Running Alembic migrations..."
    alembic upgrade head
    echo "✅ Migrations completed"
  else
    echo "⚠️ Alembic not installed; skipping migrations"
  fi
}

# ============================================================================
# Main execution
# ============================================================================
wait_for_postgres
validate_superuser
create_database
create_admin_user
grant_privileges
wait_for_redis
run_migrations

echo "🚀 Starting backend..."
exec "$@"
