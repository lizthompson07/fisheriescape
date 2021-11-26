import csv

from django.contrib.auth.models import User

from dm_apps.utils import Echo
from lib.functions.custom_functions import listrify
from lib.templatetags.verbose_names import get_field_value


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
