#!/usr/bin/env bash
set -euo pipefail

FRONTEND_PORT=${FRONTEND_PORT:-5000}
BACKEND_PORT=${BACKEND_PORT:-8000}

# Ensure script runs from project root
cd /app || exit 1

# Start backend (from ml_engine directory)
cd /app/ml_engine
uvicorn api.inference_api:app --host 0.0.0.0 --port "${BACKEND_PORT}" &
PID_BACKEND=$!

# Start frontend
cd /app
# Ensure dev server listens on all interfaces
npm run dev -- --port "${FRONTEND_PORT}" --host 0.0.0.0 &
PID_FRONTEND=$!

# Trap signals and forward to child processes
_term() {
  echo "Shutting down..."
  kill -TERM "$PID_BACKEND" 2>/dev/null || true
  kill -TERM "$PID_FRONTEND" 2>/dev/null || true
}
trap _term SIGTERM SIGINT

# Wait for either process to exit
wait -n "$PID_BACKEND" "$PID_FRONTEND"

# Exit with the status of the process that exited
wait "$PID_BACKEND" || true
wait "$PID_FRONTEND" || true
