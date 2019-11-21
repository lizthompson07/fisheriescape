from __future__ import division

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.utils import timezone

from .models import Pageview, VisitSummary

headers = (
    'HTTP_CLIENT_IP', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED',
    'HTTP_X_CLUSTERED_CLIENT_IP', 'HTTP_FORWARDED_FOR', 'HTTP_FORWARDED',
    'REMOTE_ADDR'
)


def get_ip_address(request):
    for header in headers:
        if request.META.get(header, None):
            ip = request.META[header].split(',')[0]

            try:
                validate_ipv46_address(ip)
                return ip
            except ValidationError:
                pass


def total_seconds(delta):
    day_seconds = (delta.days * 24 * 3600) + delta.seconds
    return (delta.microseconds + day_seconds * 10 ** 6) / 10 ** 6


def chunk_pageviews():
    # capture all lines of page view table in 2 summary tables
    for view in Pageview.objects.filter(summarized=False):
        # what app were they using?
        url_list = view.url.split("/")
        app_name = url_list[2] if len(url_list) > 2 else None

        # who is the user?
        my_user = view.visitor.user

        if my_user and app_name and app_name not in ["", "accounts", "login_required", "denied", "reset", "password-reset", "auth", "login",
                                                     "setlang", "shared", "tracking"]:
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
