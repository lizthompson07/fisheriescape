from django.contrib.auth.models import Group
# open basic access up to anybody who is logged in
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _, gettext
from markdown import markdown

from res import models
from shared_models.models import Section, Division, Branch, Sector, Region


def in_res_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="res_admin")
    if user:
        return admin_group in user.groups.all()


def in_res_crud_group(user):
    # make sure the following group exist:
    crud_group, created = Group.objects.get_or_create(name="res_crud")
    if user:
        return in_res_admin_group(user) or crud_group in user.groups.all()


def get_related_applications(user):
    """give me a user and I'll send back a queryset with all related requests, i.e.
     they are a client || they are a coordinator || they are the request.created_by"""
    qs = models.Application.objects.filter(Q(created_by=user) | Q(applicant=user) | Q(manager=user)).distinct()
    return qs


def is_applicant(user, application_id):
    if user.id:
        application = get_object_or_404(models.Application, pk=application_id)
        return application.applicant == user


def is_creator(user, application_id):
    if user.id:
        application = get_object_or_404(models.Application, pk=application_id)
        return application.created_by == user


def is_manager(user, application_id):
    if user.id:
        application = get_object_or_404(models.Application, pk=application_id)
        return application.manager == user


def can_modify_application(user, application_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify an application
    The answer of this question will depend on the business rules...

    always: admin
    if NOT submitted: applicant, created_by, manager?

    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:
        my_dict["reason"] = "You do not have the permissions to modify this application"
        application = get_object_or_404(models.Application, pk=application_id)
        # check to see if they are the client
        if is_applicant(user, application_id=application.id) and not application.submission_date:
            my_dict["reason"] = "You can modify this record because you are the applicant!"
            my_dict["can_modify"] = True
        # check to see if they are the client
        elif is_creator(user, application_id=application.id) and not application.submission_date:
            my_dict["reason"] = "You can modify this record because you are the record creator"
            my_dict["can_modify"] = True
        # # check to see if they are the coordinator
        # elif is_request_coordinator(user, application_id=application.id):
        #     my_dict["reason"] = "You can modify this record because you are the CSAS coordinator"
        #     my_dict["can_modify"] = True
        # # are they a national administrator?
        elif in_res_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a system administrator"
            my_dict["can_modify"] = True
        # # are they a regional administrator?
        # elif in_csas_regional_admin_group(user):
        #     my_dict["reason"] = "You can modify this record because you are a regional CSAS administrator"
        #     my_dict["can_modify"] = True
        return my_dict if return_as_dict else my_dict["can_modify"]


def can_view_application(user, application_id):
    """
    returns True if user has permissions to delete or modify an application
    The answer of this question will depend on the business rules...

    always: admin
    if NOT submitted: applicant, created_by, manager?

    """
    if user.id:
        application = get_object_or_404(models.Application, pk=application_id)
        # check to see if they are the client
        if is_applicant(user, application_id=application.id):
            return True
        # check to see if they are the client
        elif is_creator(user, application_id=application.id):
            return True
        # # are they a national administrator?
        elif in_res_admin_group(user):
            return True


def can_modify_recommendation(user, application_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify an application
    The answer of this question will depend on the business rules...

    always: admin
    if NOT submitted: applicant, created_by, manager?

    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:
        my_dict["reason"] = "You do not have the permissions to modify this recommendation"
        application = get_object_or_404(models.Application, pk=application_id)
        if hasattr(application, "recommendation"):
            recommendation = application.recommendation
            # check to see if they are the client
            if is_manager(user, application_id=application.id) and not recommendation.manager_signed:
                my_dict["reason"] = "You can modify this record because you are the active manager!"
                my_dict["can_modify"] = True

            # # are they a national administrator?
            # elif in_res_admin_group(user):
            #     my_dict["reason"] = "You can modify this record because you are a system administrator"
            #     my_dict["can_modify"] = True

        return my_dict if return_as_dict else my_dict["can_modify"]



def can_modify_achievement(user, achievement_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify an achievement
    The answer of this question will depend on the business rules...

    always: admin
    if NOT submitted: applicant, created_by, manager?

    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))
    if user.id:
        my_dict["reason"] = "You do not have the permissions to modify this achievement"
        achievement = get_object_or_404(models.Achievement, pk=achievement_id)
        # check to see if they are the client
        if user == achievement.user:
            my_dict["reason"] = "You can modify this record because you are the owner!"
            my_dict["can_modify"] = True
        elif in_res_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a system administrator"
            my_dict["can_modify"] = True
        return my_dict if return_as_dict else my_dict["can_modify"]


def can_view_achievement(user, achievement_id):
    """
    returns True if user has permissions to delete or modify an achievement
    The answer of this question will depend on the business rules...

    always: admin
    if NOT submitted: applicant, created_by, manager?

    """
    if user.id:
        achievement = get_object_or_404(models.Achievement, pk=achievement_id)
        return user == achievement.user or in_res_admin_group(user)



def get_section_choices(with_application=False, full_name=True, region_filter=None, division_filter=None):
    my_attr = _("name")
    if full_name:
        my_attr = "full_name"

    reg_kwargs = dict(division__branch__region_id__isnull=False)
    if region_filter:
        reg_kwargs = dict(division__branch__region_id=region_filter)

    div_kwargs = dict(division_id__isnull=False)
    if division_filter:
        div_kwargs = dict(division_id=division_filter)

    request_kwargs = dict()
    if with_application:
        div_kwargs = dict(res_applications__isnull=False)

    my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                      Section.objects.all().order_by(
                          "division__branch__region",
                          "division__branch",
                          "division",
                          "name"
                      ).filter(**div_kwargs).filter(**reg_kwargs).filter(**request_kwargs).distinct()]
    return my_choice_list


def get_division_choices(with_application=False, region_filter=None):
    division_list = set(
        [Section.objects.get(pk=s[0]).division_id for s in get_section_choices(with_application=with_application, region_filter=region_filter)])
    return [(d.id, str(d)) for d in
            Division.objects.filter(id__in=division_list).order_by("branch__region", "name")]


def get_branch_choices(with_application=False, region_filter=None):
    branch_list = set(
        [Division.objects.get(pk=d[0]).branch_id for d in get_division_choices(with_application=with_application, region_filter=region_filter)])
    return [(b.id, str(b)) for b in
            Branch.objects.filter(id__in=branch_list).order_by("sector__region", "sector", "name")]


def get_sector_choices(with_application=False, region_filter=None):
    sector_list = set(
        [Branch.objects.get(pk=b[0]).sector_id for b in get_branch_choices(with_application=with_application, region_filter=region_filter)])
    return [(s.id, str(s)) for s in
            Sector.objects.filter(id__in=sector_list).order_by("region", "name")]


def get_region_choices(with_application=False):
    region_list = set([Sector.objects.get(pk=s[0]).region_id for s in get_sector_choices(with_application=with_application)])
    return [(r.id, str(r)) for r in
            Region.objects.filter(id__in=region_list).order_by("name", )]


def connect_refs(txt, achievements_qs):
    # comb through the text and see if you can connect to an achievement
    text_list = txt.split("[")
    ref_list = list()
    for word in text_list:
        if word.lower().startswith("ref"):
            ref_list.append(word.split("]")[0])
    ref_set = set(ref_list)
    for ref in ref_set:
        # try to get the achievement
        pk = ref.lower().replace("ref", "").strip()
        try:
            a = achievements_qs.get(pk=pk)
            tip = a.achievement_display_no_code
            if a.category:
                code = a.category.code
            text_class = "text-primary"
            text = f"{a.code}"
            href = f"#achievement{a.id}"
        except:
            tip = gettext("Bad reference!!")
            text_class = "text-danger"
            text = "???"
            href = "??"
        replace_text = f"<a href='{href}' class='{text_class} helper' data-toggle='tooltip' title='{tip}'>{text}</a>"
        txt = txt.replace(f"[{ref}]", replace_text)
    return markdown(txt)


def achievements_summary_table(user):
    payload = list()
    last_application = user.res_applications.filter(last_promotion__isnull=False).order_by("last_promotion").last()
    before_last_promotion = "---"
    since_last_promotion = "---"
    for publication_type in models.PublicationType.objects.all():
        qs = user.achievements.filter(publication_type=publication_type, category__is_publication=True)
        if last_application:
            last_promotion = last_application.last_promotion
            before_last_promotion = qs.filter(date__lt=last_promotion).count()
            since_last_promotion = qs.filter(date__gte=last_promotion).count()
        payload.append(
            dict(
                publication_type=f"{publication_type.code}. {publication_type.tname}",
                before_last_promotion=before_last_promotion,
                since_last_promotion=since_last_promotion,
                total=qs.count(),
            )
        )

    qs = user.achievements.filter(category__is_publication=True)
    if last_application:
        last_promotion = last_application.last_promotion
        before_last_promotion = qs.filter(date__lt=last_promotion).count()
        since_last_promotion = qs.filter(date__gte=last_promotion).count()
    payload.append(
            dict(
                publication_type=_("TOTAL"),
                before_last_promotion=before_last_promotion,
                since_last_promotion=since_last_promotion,
                total=qs.count(),
            )
        )
    return payload
