#!/bin/bash
# ============================================================================
# wait-for-services.sh
# Waits for Postgres and Redis to be ready before starting the backend
# ============================================================================
set -e

# ---------------------------------------------------------------------------
# Environment variables with defaults
# ---------------------------------------------------------------------------
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-mrwa}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-mrwa_password}
POSTGRES_DB=${DATABASE_NAME:-mrwa}

REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

# ---------------------------------------------------------------------------
# Timeout settings (in seconds)
# ---------------------------------------------------------------------------
MAX_WAIT=120   # max seconds to wait for a service
SLEEP_INTERVAL=2

# ---------------------------------------------------------------------------
# Function: wait for Postgres
# ---------------------------------------------------------------------------
echo "⏳ Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
TIME_WAITED=0
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  if [ "$TIME_WAITED" -ge "$MAX_WAIT" ]; then
    echo "❌ Timeout reached: Postgres is still not ready after $MAX_WAIT seconds"
    exit 1
  fi
  echo "Postgres not ready yet... sleeping ${SLEEP_INTERVAL}s"
  sleep $SLEEP_INTERVAL
  TIME_WAITED=$((TIME_WAITED+SLEEP_INTERVAL))
done
echo "✅ Postgres is ready!"

# ---------------------------------------------------------------------------
# Function: wait for Redis
# ---------------------------------------------------------------------------
echo "⏳ Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
TIME_WAITED=0
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q PONG; do
  if [ "$TIME_WAITED" -ge "$MAX_WAIT" ]; then
    echo "❌ Timeout reached: Redis is still not ready after $MAX_WAIT seconds"
    exit 1
  fi
  echo "Redis not ready yet... sleeping ${SLEEP_INTERVAL}s"
  sleep $SLEEP_INTERVAL
  TIME_WAITED=$((TIME_WAITED+SLEEP_INTERVAL))
done
echo "✅ Redis is ready!"

# ---------------------------------------------------------------------------
# Start backend
# ---------------------------------------------------------------------------
echo "🚀 Starting backend..."
exec "$@"
