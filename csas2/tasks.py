from celery import shared_task
from django.utils import timezone

from . import emails
from .models import ToRReviewer


@shared_task(name="tor_reviewer_reminder_email")
def tor_reviewer_reminder_email():
    # get all reviewers whose status are pending (30) and whose decisions are null
    lazy_reviewers = ToRReviewer.objects.filter(review_started__isnull=False, review_completed__isnull=True)
    for r in lazy_reviewers:
        td = timezone.now() - r.review_started
        if td.days >= 5:
            send_email = False
            # they are in the warning zone...
            # if there was never a warning, we send one right away
            if not r.reminder_sent:
                send_email = True
            # otherwise we compare to when the reminder email was last sent
            else:
                td = timezone.now() - r.reminder_sent
                if td.days >= 5:
                    send_email = True
            if send_email:
                # update the reminder sent date
                email = emails.ToRReviewReminderEmail(r, td)
                email.send()
                r.reminder_sent = timezone.now()
                r.save()
