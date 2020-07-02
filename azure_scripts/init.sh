#!/bin/bash
-e

#CMD ["gunicorn",  "--bind", "8000:8000", "mysite.wsgi:application"]

gunicorn -b 0.0.0.0:8000 dm_apps.wsgi:application