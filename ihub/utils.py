
from collections import namedtuple
from datetime import datetime

from django.utils import timezone


def get_date_range_overlap(d0_start, d0_end, d1_start, d1_end):
    # inspired by
    # https://stackoverflow.com/questions/9044084/efficient-date-range-overlap-calculation-in-python

    d0_start = datetime(1990, 1, 1).replace(tzinfo=timezone.get_current_timezone()) if not d0_start else d0_start
    d1_start = datetime(1990, 1, 1).replace(tzinfo=timezone.get_current_timezone()) if not d1_start else d1_start
    d0_end = datetime(2200, 1, 1).replace(tzinfo=timezone.get_current_timezone()) if not d0_end else d0_end
    d1_end = datetime(2200, 1, 31).replace(tzinfo=timezone.get_current_timezone()) if not d1_end else d1_end
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=d0_start, end=d0_end)
    r2 = Range(start=d1_start, end=d1_end)
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start).days + 1
    overlap = max(0, delta)
    return overlap

