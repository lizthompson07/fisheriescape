#!/bin/bash
service ssh start
GIT_VERSION=$(git rev-parse --short HEAD)
export GIT_VERSION
python create_env_file_from_json.py --environment-name "$ENVIRONMENT_NAME" --output-file-name=".env"
python manage.py compilemessages
python manage.py collectstatic --no-input
python manage.py migrate
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application