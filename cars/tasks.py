from celery import shared_task

from .models import Reservation


@shared_task(name="resave_open_rsvps")
def resave_open_rsvps():
    for r in Reservation.objects.filter(is_complete=False):
        r.save()
