#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset
# Collect static files
python manage.py collectstatic --noinput

gunicorn --bind 0.0.0.0:5000 a_core.asgi:application -w 4 -k uvicorn_worker.UvicornWorker
