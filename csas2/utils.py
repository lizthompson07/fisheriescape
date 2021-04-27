from django.contrib.auth.models import Group
# open basic access up to anybody who is logged in
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from csas2 import models
from lib.templatetags.verbose_names import get_verbose_label
from shared_models.models import Section, Division, Region, Branch


def in_csas_regional_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="csas_regional_admin")
    if user:
        return admin_group in user.groups.all()


def in_csas_national_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="csas_national_admin")
    if user:
        return admin_group in user.groups.all()


def in_csas_admin_group(user):
    # make sure the following group exist:
    if user:
        return in_csas_regional_admin_group(user) or in_csas_national_admin_group(user)


def get_section_choices(with_requests=False, full_name=True, region_filter=None, division_filter=None):
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

    if division_filter:
        div_kwargs = {
            "division_id": division_filter
        }
    else:
        div_kwargs = {
            "division_id__isnull": False
        }

    if not with_requests:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          Section.objects.all().order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name",
                          ).filter(**div_kwargs).filter(**reg_kwargs).filter(csas_requests__isnull=False)]
    else:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          Section.objects.filter(
                              division__branch__name__icontains="science").order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name"
                          ).filter(**div_kwargs).filter(**reg_kwargs)]
    return my_choice_list


def get_division_choices(with_requests=False, region_filter=None):
    division_list = set(
        [Section.objects.get(pk=s[0]).division_id for s in get_section_choices(with_requests=with_requests, region_filter=region_filter)])
    return [(d.id, str(d)) for d in
            Division.objects.filter(id__in=division_list).order_by("branch__region", "name")]


def get_branch_choices(with_requests=False, region_filter=None):
    branch_list = set(
        [Division.objects.get(pk=d[0]).branch_id for d in get_division_choices(with_requests=with_requests, region_filter=region_filter)])
    return [(b.id, str(b)) for b in
            Branch.objects.filter(id__in=branch_list).order_by("region", "name")]


def get_region_choices(with_requests=False):
    region_list = set(
        [Division.objects.get(pk=d[0]).branch.region_id for d in get_division_choices(with_requests=with_requests)])
    return [(r.id, str(r)) for r in
            Region.objects.filter(id__in=region_list).order_by("name", )]


def is_request_coordinator(user, request_id):
    if user.id:
        csas_request = get_object_or_404(models.CSASRequest, pk=request_id)
        return csas_request.coordinator == user


def is_process_coordinator(user, process_id):
    if user.id:
        process = get_object_or_404(models.Process, pk=process_id)
        return process.coordinator == user


def is_advisor(user, process_id):
    if user.id:
        process = get_object_or_404(models.Process, pk=process_id)
        return process.advisors.filter(id=user.id).exists()


def is_client(user, request_id):
    if user.id:
        csas_request = get_object_or_404(models.CSASRequest, pk=request_id)
        return csas_request.client == user


def is_creator(user, request_id):
    if user.id:
        csas_request = get_object_or_404(models.CSASRequest, pk=request_id)
        return csas_request.created_by == user


def can_modify_request(user, request_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify a request
    The answer of this question will depend on the business rules...

    always: csas admin, coordinator
    if NOT submitted: client, created_by

    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:
        my_dict["reason"] = "You do not have the permissions to modify this request"
        csas_request = get_object_or_404(models.CSASRequest, pk=request_id)
        # check to see if they are the client
        if is_client(user, request_id=csas_request.id):
            my_dict["reason"] = "You can modify this record because you are the request client"
            my_dict["can_modify"] = True
        # check to see if they are the client
        elif is_creator(user, request_id=csas_request.id):
            my_dict["reason"] = "You can modify this record because you are the request client"
            my_dict["can_modify"] = True
        # check to see if they are the coordinator
        elif is_request_coordinator(user, request_id=csas_request.id):
            my_dict["reason"] = "You can modify this record because you are the CSAS coordinator"
            my_dict["can_modify"] = True
        # are they a national administrator?
        elif in_csas_national_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a national CSAS administrator"
            my_dict["can_modify"] = True
        # are they a regional administrator?
        elif in_csas_regional_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a regional CSAS administrator"
            my_dict["can_modify"] = True
        return my_dict if return_as_dict else my_dict["can_modify"]


def can_modify_process(user, process_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify a process
    The answer of this question will depend on the business rules...
    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:
        my_dict["reason"] = "You do not have the permissions to modify this process"
        process = get_object_or_404(models.Process, pk=process_id)
        # check to see if they are the client

        # are they an advisor?
        if is_advisor(user, process.id):
            my_dict["reason"] = "You can modify this record because you are a science advisor for this process"
            my_dict["can_modify"] = True
        # are they a coordinator?
        elif is_process_coordinator(user, process.id):
            my_dict["reason"] = "You can modify this record because you are the coordinator for this process"
            my_dict["can_modify"] = True
        # are they a national administrator?
        elif in_csas_national_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a national CSAS administrator"
            my_dict["can_modify"] = True
        # are they a regional administrator?
        elif in_csas_regional_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a regional CSAS administrator"
            my_dict["can_modify"] = True
        return my_dict if return_as_dict else my_dict["can_modify"]


def get_request_field_list(csas_request, user):
    my_list = [
        'id|{}'.format(_("request Id")),
        'fiscal_year',
        'status_display|{}'.format(_("status")),
        'is_carry_over|{}'.format(_("is carry over?")),
        'language',
        'section',
        'coordinator',
        'client',
        'multiregional_display|{}'.format(_("Multiregional / multisector?")),
        'issue_html|{}'.format(get_verbose_label(csas_request, "issue")),
        'assistance_display|{}'.format(_("Assistance from DFO Science?")),
        'rationale_html|{}'.format(get_verbose_label(csas_request, "rationale")),
        'risk_text',
        'advice_needed_by',
        'rationale_for_timeline',
        'funding_display|{}'.format(_("client funding?")),
        'prioritization_display|{}'.format(_("client prioritization")),
        'submission_date',
        'uuid',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_review_field_list():
    my_list = [
        'ref_number|{}'.format(_("reference number")),
        'prioritization_display|{}'.format(_("prioritization")),
        'decision_display|{}'.format(_("decision")),
        'advice_date',
        'deferred_display|{}'.format(_("What the original request date deferred?")),
        'notes',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_process_field_list(process):
    my_list = [
        'fiscal_year',
        'tname|{}'.format(_("Title")),
        'status_display|{}'.format(_("status")),
        'scope_type|{}'.format(_("advisory process type")),
        'coordinator',
        'advisors',
        'lead_region',
        'other_regions',
        'context_html|{}'.format(get_verbose_label(process, "context")),
        'objectives_html|{}'.format(get_verbose_label(process, "objectives")),
        'expected_publications_html|{}'.format(get_verbose_label(process, "expected_publications")),
        'type',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_meeting_field_list():
    my_list = [
        'process',
        'type',
        'location',
        'attendees',
        'display_dates|{}'.format(_("dates")),
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_document_field_list():
    my_list = [
        'process',
        'title_en',
        'title_fr',
        'title_in',
        'type',
        'status',
        'series',
        'year',
        'pub_number',
        'pages',
        'hide_from_list',
        'metadata|{}'.format(_("metadata")),

    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_related_requests(user):
    """give me a user and I'll send back a queryset with all related requests, i.e.
     they are a client || they are a coordinator || they are the request.created_by"""
    qs = models.CSASRequest.objects.filter(Q(created_by=user) | Q(coordinator=user)).distinct()
    return qs


def get_related_processes(user):
    """give me a user and I'll send back a queryset with all related processes, i.e.
     they are a client on a request ||
     they are a coordinator ||
     they are an advisor
     """
    qs = models.Process.objects.filter(Q(coordinator=user) | Q(advisors=user) | Q(csas_requests__client=user)).distinct()
    return qs



def get_related_docs(user):
    """give me a user and I'll send back a queryset with all related docs, i.e.
     they are an author ||
     they are a process coordinator ||
     they are a process advisor
     """
    qs = models.Process.objects.filter(Q(process__coordinator=user) | Q(process__advisors=user) | Q(authors=user)).distinct()
    return qs


def get_person_field_list():
    my_list = [
        'full_name|{}'.format(_("Full name")),
        'phone',
        'email',
        'language',
        'affiliation',
        'tposition|{}'.format(_("job title")),
        'dmapps_user',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list
