#!/usr/bin/env bash
# Render build: migrate runs here so Start Command stays simple (gunicorn only)
# Site stays up even if migrate has issues; Start never blocks on DB
set -o errexit
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
