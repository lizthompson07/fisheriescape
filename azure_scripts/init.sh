#!/bin/bash
service ssh start
python manage.py compilemessages
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application