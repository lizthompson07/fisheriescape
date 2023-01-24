import math

import pytz
from django.conf import settings
# open basic access up to anybody who is logged in
from django.utils import timezone
from django.utils.translation import gettext as _


def is_admin(user):
    if user:
        return bool(hasattr(user, "edna_user") and user.edna_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(hasattr(user, "edna_user") and user.edna_user.is_crud_user)


def calc_nautical_dist(p0, p1):
    """
    p0 and p1 should be dicts with key 'lat' and 'lng'
    """
    nautical_miles = 3443.8985 * math.acos(
        math.sin(p0["x"] * math.pi / 180) * math.sin(p1["x"] * math.pi / 180) +
        math.cos(p0["x"] * math.pi / 180) * math.cos(p1["x"] * math.pi / 180) *
        math.cos(p1["y"] * math.pi / 180 - p0["y"] * math.pi / 180)
    )
    return nautical_miles


def get_sample_field_list():
    my_list = [
        'datetime',
        'site_description',
        'site_identifier',
        'collector',
        'sample_identifier',
        'latitude',
        'longitude',
        'comments',
    ]
    return my_list


def get_collection_field_list(collection):
    my_list = [
        'id',
        'name',
        'description',
        'region',
        'province',
        'contacts',
        'dates|dates',
        'tags',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_batch_field_list():
    my_list = [
        "datetime",
        "operators",
        "default_collection",
    ]
    return my_list


def get_sample_batch_field_list():
    my_list = [
        "default_collection",
        "datetime",
        "operators",
        "sent_by",
        "storage_location"
    ]
    return my_list


def get_pcr_batch_field_list():
    my_list = [
        "display_time|{}".format(_("date/time")),
        "default_collection",
        "operators",
        "plate_id",
        "machine_number",
        "run_program",
        "control_status",
        "comments",
    ]
    return my_list


def get_assay_field_list():
    my_list = [

        "sample|{}".format(_("sample")),
        "filter|{}".format(_("filter")),
        "pcr.extract|{}".format(_("DNA extraction")),
        "pcr| qPCR",
        "assay",
        "assay.species|{}".format(_("species")),
        "ct",
        "threshold",
        "comments",
        "result",
        "edna_conc",
    ]
    return my_list


def get_next_bottle_id():
    from .models import Sample

    samples = Sample.objects.filter(bottle_id__isnull=False).order_by("bottle_id")
    if not samples.exists():
        return 1
    return samples.last().bottle_id + 1


def get_timezone_time(dt):
    if dt:
        return timezone.localtime(dt)
