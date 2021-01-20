#!/bin/bash
service ssh start
python manage.py compilemessages
python create_env_file_from_json.py "$ENVIRONMENT_NAME"
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application