#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset
# Collect static files
python -m blacknoise.compress static/
python manage.py collectstatic --noinput

# Start uvicorn with reload for development
exec uvicorn a_core.asgi:application --host 0.0.0.0 --port 8002 --reload 