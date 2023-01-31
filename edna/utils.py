import math

import pytz
from django.conf import settings
import datetime as dt

from django.contrib import messages
from django.db.transaction import atomic
# open basic access up to anybody who is logged in
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _

from edna import models
from lib.templatetags.custom_filters import nz


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
        "comments",
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


@atomic
def sample_csv_parser(csv_reader, batch, request):
    for row in csv_reader:
        try:
            bottle_id = row["bottle_id"]
            sample_type = row["sample_type"]
            location = row["location"]
            site = row["site"]
            station = row["station"]
            samplers = row["samplers"]
            datetime = make_aware(dt.datetime.strptime(row["datetime"], "%m/%d/%Y %H:%M"),
                                  timezone=timezone.get_current_timezone())
            latitude = nz(row["latitude"], None)
            longitude = nz(row["longitude"], None)
            comments = row["comments"]

            sample, create = models.Sample.objects.get_or_create(bottle_id=bottle_id, sample_batch=batch,
                                                                 collection=batch.default_collection,
                                                                 sample_type_id=sample_type)
            sample.location = location
            sample.site = site
            sample.station = station
            sample.samplers = samplers
            sample.datetime = datetime
            sample.latitude = latitude
            sample.longitude = longitude
            sample.comments = comments
            sample.save()
        except Exception as err:
            messages.error(request, _('Invalid CSV. Error on row {}. Error: {}'.format(row, err)))
            raise


def get_pcr_result(result_qs, lod):
    # codes in pcr_assay model
    if not lod:
        return 91, _("LOD missing :(")
    checklist = []
    for pcr_result in result_qs:
        if pcr_result.ct == 0:
            checklist.append("Negative")
        elif pcr_result.ct <= lod:
            checklist.append("Positive")
        elif pcr_result.ct > lod:
            checklist.append("Weak positive")
        else:
            checklist.append("No Data")

    if all(assay == "Positive" for assay in checklist):
        return 1, _("positive")
    elif all(assay in ["Positive", "Weak positive"] for assay in checklist):
        return 93, _("Suspected")
    elif any(assay == "Positive" for assay in checklist):
        return 92, _("Inconclusive")
    else:
        return 0, _("negative")


