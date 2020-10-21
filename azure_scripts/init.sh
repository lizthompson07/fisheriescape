#!/bin/bash
-e
systemctl enable ssh
systemctl start ssh
docker restart dmapps_img
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application