#!/bin/bash
-e
/usr/sbin/sshd
docker restart dmapps_img
gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application