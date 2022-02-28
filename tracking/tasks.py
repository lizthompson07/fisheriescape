from celery import shared_task
from django.utils import timezone

from tracking.models import Pageview, VisitSummary


@shared_task(name="chunk_pageviews")
def chunk_pageviews():
    # capture all lines of page view table in 2 summary tables
    for view in Pageview.objects.filter(summarized=False):
        # what app were they using?
        url_parts = view.url.split("/")
        # get the app name:
        app_ignore_list = ["", "accounts", "login_required", "denied", "reset", "password-reset", "auth", "login",
                           "setlang", "shared", "tracking", 'a', ]
        part_ignore_list = ['', 'en', 'fr']

        app_name = None
        for part in url_parts:
            if part.lower() not in part_ignore_list:
                app_name = part.lower()
                break

        # who is the user?
        my_user = view.visitor.user

        if my_user and app_name and app_name not in app_ignore_list:
            # here are special operations...
            if app_name == "projects":
                app_name = "ppt"

            # what is the date?
            my_date = timezone.datetime(view.view_time.year, view.view_time.month, view.view_time.day)

            # add view to visitSummary table
            # print(app_name)
            visit_summary_obj, created = VisitSummary.objects.get_or_create(
                date=my_date,
                application_name=app_name,
                user=my_user,
            )

            visit_summary_obj.page_visits += 1
            visit_summary_obj.save()

        # mark the view as summarized.
        view.summarized = True
        view.save()

    # delete any records older then three days
    Pageview.objects.filter(summarized=True).filter(view_time__lte=timezone.now() - timezone.timedelta(days=3)).delete()
