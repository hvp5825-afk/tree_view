#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Django server exactly like local on port 8000..."
exec python manage.py runserver 0.0.0.0:8000
