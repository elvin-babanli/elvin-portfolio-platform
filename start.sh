#!/usr/bin/env bash
# Production start script for Render.
# Ensures PORT is set, binds to 0.0.0.0, uses stable gunicorn options.
set -e
export PORT="${PORT:-10000}"
echo "[start.sh] Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn core.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --worker-class gthread \
  --threads 4 \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level info
