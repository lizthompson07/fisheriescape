#!/bin/bash
service ssh start
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application