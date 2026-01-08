#!/bin/sh
# ============================================================================
# docker-entrypoint.sh - Frontend entrypoint
# Handles SIGINT/SIGTERM gracefully for Docker
# ============================================================================
set -e

echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting frontend container..."

# Optional: Run pre-start hooks here
# echo "Running pre-start checks..."
# ./scripts/prestart.sh || exit 1

# Function to handle termination signals
_term() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - Caught termination signal, shutting down..."
  if [ -n "$child" ] && kill -0 "$child" 2>/dev/null; then
    kill -TERM "$child" 2>/dev/null
    wait "$child"
  fi
  exit 0
}

trap _term SIGINT SIGTERM

# Start Next.js in production mode
echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting Next.js..."
npm start &

child=$!
wait "$child"
status=$?

echo "$(date +'%Y-%m-%d %H:%M:%S') - Frontend exited with status $status"
exit $status
