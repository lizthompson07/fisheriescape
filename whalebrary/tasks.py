from datetime import datetime

from celery import shared_task
from django.utils import timezone

from . import emails
from .models import Maintenance

from django.db.models import F, DateTimeField, ExpressionWrapper


@shared_task(name="maintenance_reminder_email")
def maintenance_reminder_email():
    # get all maintenance items that are overdue

    # Uses Expression Wrapper to assign 'maint' the date when maintenance would be due, then filter all objects where
    # that due date is less than the current date (i.e. in the past)

    # due_maintenance = Maintenance.objects.filter(days_until_maint__lte=0) # unfortunately can't filter on properties

    due_maintenance = Maintenance.objects.annotate(
        maint=ExpressionWrapper((F('last_maint_date') + F('schedule')), output_field=DateTimeField())
    ).filter(maint__lte=datetime.now(timezone.utc))

    for m in due_maintenance:
        email = emails.MaintenanceReminderEmail(m)
        email.send()
        m.save()
