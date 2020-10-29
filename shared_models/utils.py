from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from . import models


def get_section_choices(full_name=True, region_filter=None, branch_filter=None, division_filter=None):
    if full_name:
        my_attr = "full_name"
    else:
        my_attr = _("name")

    if region_filter:
        reg_kwargs = {
            "division__branch__region_id": region_filter
        }
    else:
        reg_kwargs = {
            "division__branch__region_id__isnull": False
        }

    if branch_filter:
        branch_kwargs = {
            "division__branch_id": branch_filter
        }
    else:
        branch_kwargs = {
            "division__branch__isnull": False
        }

    if division_filter:
        div_kwargs = {
            "division_id": division_filter
        }
    else:
        div_kwargs = {
            "division_id__isnull": False
        }

    my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                      models.Section.objects.order_by(
                          "division__branch__region",
                          "division__branch",
                          "division",
                          "name"
                      ).filter(**div_kwargs).filter(**reg_kwargs).filter(**branch_kwargs)]

    return my_choice_list


def get_division_choices(region_filter=None, branch_filter=None):
    division_list = set(
        [models.Section.objects.get(pk=s[0]).division_id for s in
         get_section_choices(region_filter=region_filter, branch_filter=branch_filter)])
    return [(d.id, str(d)) for d in
            models.Division.objects.filter(id__in=division_list).order_by("branch__region", "name")]


def get_branch_choices(region_filter=None):
    branch_list = set(
        [models.Division.objects.get(pk=d[0]).branch_id for d in get_division_choices(region_filter=region_filter)])
    return [(b.id, str(b)) for b in
            models.Branch.objects.filter(id__in=branch_list).order_by("region", "name")]


def get_region_choices():
    region_list = set(
        [models.Division.objects.get(pk=d[0]).branch.region_id for d in get_division_choices()])
    return [(r.id, str(r)) for r in
            models.Region.objects.filter(id__in=region_list).order_by("name", )]


def get_metadata_string(created_at=None, created_by=None, updated_at=None, last_modified_by=None):
    my_str = f"<u>Created:</u> {created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    if created_by:
        my_str += f" by {created_by}"
    if updated_at:
        my_str += f"<br><u>Updated:</u> {updated_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        if last_modified_by:
            my_str += f" by {last_modified_by}"

    return mark_safe(my_str)
