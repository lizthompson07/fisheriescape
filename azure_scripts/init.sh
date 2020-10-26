#!/bin/bash
-e
docker restart dmapps_img
systemctl enable ssh
systemctl start ssh
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application