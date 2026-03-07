#!/usr/bin/env bash
# Render build script: install deps, run migrations, collect static
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Build complete."
