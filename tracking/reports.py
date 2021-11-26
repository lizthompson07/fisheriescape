import csv

from django.contrib.auth.models import User
from django.db.models import Sum, Count

from dm_apps.utils import Echo
from lib.functions.custom_functions import listrify
from lib.templatetags.verbose_names import get_field_value
from tracking.models import VisitSummary


def generate_user_report():
    """Returns a generator for an HTTP Streaming Response"""

    # write the header
    fields = [
        "first_name",
        "last_name",
        "email",
        "date_joined",
        "last_login",
        "pageviews",
        "apps_used",
        "cumulative_users",
    ]

    qs = User.objects.filter(last_login__isnull=False).order_by("date_joined")

    pseudo_buffer = Echo()
    pseudo_buffer.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(fields)

    i = 1
    for obj in qs:
        data_row = []  # starter
        for field in fields:
            if field == "pageviews":
                data_row.append(sum([v.page_visits for v in obj.visitsummary_set.all()]))
            elif field == "apps_used":
                data_row.append(listrify(set([v.application_name for v in obj.visitsummary_set.all()])))
            elif field == "cumulative_users":
                data_row.append(i)
            else:
                data_row.append(
                    get_field_value(obj, field, display_time=True)
                )
        yield writer.writerow(data_row)
        i += 1


def generate_page_visit_summary_report():
    """Returns a generator for an HTTP Streaming Response"""

    # write the header
    fields = [
        "date",
        "application_name",
        "sum_of_page_visits",
    ]
    qs = VisitSummary.objects.all().values(
        "date", "application_name"
    ).order_by("date", "application_name").distinct().annotate(
        sum_of_page_visits=Sum("page_visits")
    )

    pseudo_buffer = Echo()
    pseudo_buffer.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(fields)

    for obj in qs:
        print(obj)
        data_row = []  # starter
        for field in fields:
            data_row.append(
                obj[field]
            )
        yield writer.writerow(data_row)

    for obj in qs:
        data_row = []  # starter
        for field in fields:
            data_row.append(
                obj[field]
            )
        yield writer.writerow(data_row)


def generate_user_summary_report():
    """Returns a generator for an HTTP Streaming Response"""

    # write the header
    fields = [
        "date",
        "application_name",
        "user_count",
    ]
    qs = VisitSummary.objects.all().values(
        "date", "application_name"
    ).order_by("date", "application_name").distinct().annotate(
        user_count=Count("user")
    )

    pseudo_buffer = Echo()
    pseudo_buffer.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(fields)

    for obj in qs:
        data_row = []  # starter
        for field in fields:
            data_row.append(
                obj[field]
            )
        yield writer.writerow(data_row)

    for obj in qs:
        data_row = []  # starter
        for field in fields:
            data_row.append(
                obj[field]
            )
        yield writer.writerow(data_row)
