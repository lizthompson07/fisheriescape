import math

from django.contrib.auth.models import Group
# open basic access up to anybody who is logged in
from django.utils.translation import gettext as _


def in_edna_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="edna_admin")
    if user:
        return admin_group in user.groups.all()


def in_edna_crud_group(user):
    # make sure the following group exist:
    crud_group, created = Group.objects.get_or_create(name="edna_crud")
    if user:
        return in_edna_admin_group(user) or crud_group in user.groups.all()


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
        'program_description',
        'region',
        'location_description',
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
    ]
    return my_list


def get_pcr_batch_field_list():
    my_list = [
        "datetime",
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
