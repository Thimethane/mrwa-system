#!/bin/sh
# ============================================================================ 
# docker-entrypoint.sh - Frontend entrypoint
# Handles SIGINT/SIGTERM gracefully for Docker
# ============================================================================

# Catch SIGINT and SIGTERM
_term() {
  echo "Caught signal, shutting down..."
  kill -TERM "$child" 2>/dev/null
}

trap _term SIGINT SIGTERM

# Start Next.js in production mode
npm start &

child=$!
wait "$child"
