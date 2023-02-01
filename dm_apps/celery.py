from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dm_apps.settings')

app = Celery('dm_apps')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# see https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html as a reference
app.conf.beat_schedule = {
    # tracking
    'run_chunk_pageviews': {
        'task': 'chunk_pageviews',
        'schedule': 60 * 60,  # Execute every hour
    },
    # cars
    'run_resave_open_rsvps': {
        'task': 'resave_open_rsvps',
        'schedule': 60 * 60 * 12,  # execute every 12 hours
    },
    # ppt
    'resave_dmas': {
        'task': 'resave_dmas',
        'schedule': 60 * 60 * 24,  # execute every day
    },
    # csas2
    'tor_reviewer_reminder_email': {
        'task': 'tor_reviewer_reminder_email',
        'schedule': 60 * 60 * 4,  # execute every 4 hours
    },
    'request_reviewer_reminder_email': {
        'task': 'request_reviewer_reminder_email',
        'schedule': 60 * 60 * 4,  # execute every 4 hours
    },
    'maintenance_reminder_email': {
        'task': 'maintenance_reminder_email',
        'schedule': 60 * 60 * 12,  # execute every 12 hours
    },
}
