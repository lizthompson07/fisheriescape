from django.db.models import Sum, Q
from django.utils.translation import gettext as _

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from . import models


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)

    return my_dict


def in_projects_admin_group(user):
    """
    Will return True if user is in project_admin group
    """
    if user:
        return user.groups.filter(name='projects_admin').exists()


def is_management(user):
    """
        Will return True if user is in project_admin group, or if user is listed as a head of a section, division or branch
    """
    if user.id:
        return shared_models.Section.objects.filter(head=user).exists() or \
               shared_models.Division.objects.filter(head=user).exists() or \
               shared_models.Branch.objects.filter(head=user).exists()


def is_management_or_admin(user):
    """
        Will return True if user is in project_admin group, or if user is listed as a head of a section, division or branch
    """
    if user.id:
        return in_projects_admin_group(user) or is_management(user)


def is_section_head(user, project):
    try:
        return True if project.section.head == user else False
    except AttributeError as e:
        print(e)


def is_division_manager(user, project):
    try:
        return True if project.section.division.head == user else False
    except AttributeError:
        pass


def is_rds(user, project=None):
    if project:
        try:
            return True if project.section.division.branch.head == user else False
        except AttributeError:
            pass
    else:
        return shared_models.Branch.objects.filter(head=user).exists()


def is_project_lead(user, project_id=None, project_year_id=None):
    """
    returns True if user is among the project's project leads
    """
    if user.id:
        project = None
        if project_year_id:
            project = models.ProjectYear.objects.get(pk=project_year_id).project
        elif project_id:
            project = models.Project.objects.get(pk=project_id)

        if project:
            return user in [s.user for s in models.Staff.objects.filter(project_year__project=project, is_lead=True)]


def can_modify_project(user, project_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify a project
    The answer of this question will depend on whether the project is submitted. Project leads cannot edit a submitted project
    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:

        my_dict["reason"] = "You are not a project lead or manager of this project"
        project = models.Project.objects.get(pk=project_id)

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if in_projects_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a system administrator"
            my_dict["can_modify"] = True

        # check to see if they are a section head
        elif is_section_head(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your section"
            my_dict["can_modify"] = True

        # check to see if they are a div. manager
        elif is_division_manager(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your division"
            my_dict["can_modify"] = True

        # check to see if they are an RDS
        elif is_rds(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your branch"
            my_dict["can_modify"] = True

        # check to see if they are a project lead
        elif is_project_lead(user, project_id=project.id):
            my_dict["reason"] = "You can modify this record because you are a project lead"
            my_dict["can_modify"] = True

        # check to see if they are a project lead
        elif not project.lead_staff.exists():
            my_dict["reason"] = "You can modify this record because there are currently no project leads"
            my_dict["can_modify"] = True

        return my_dict if return_as_dict else my_dict["can_modify"]


def is_admin_or_project_manager(user, project):
    """returns True if user is either in 'projects_admin' group OR if they are a manager of the project (section head, div. manager, RDS)"""
    if user.id:

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if "projects_admin" in [g.name for g in user.groups.all()]:
            return True

        # check to see if they are a section head, div. manager or RDS
        if is_section_head(user, project) or is_division_manager(user, project) or is_rds(user, project):
            return True


def get_manageable_sections(user):
    if in_projects_admin_group(user):
        return shared_models.Section.objects.filter(projects__isnull=False).distinct()
    return shared_models.Section.objects.filter(Q(head=user) | Q(division__head=user) | Q(division__branch__head=user))


def get_section_choices(all=False, full_name=True, region_filter=None, division_filter=None):
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

    if not all:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          shared_models.Section.objects.all().order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name"
                          ).filter(**div_kwargs).filter(**reg_kwargs) if s.projects2.count() > 0]
    else:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          shared_models.Section.objects.filter(
                              division__branch__name__icontains="science").order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name"
                          ).filter(**div_kwargs).filter(**reg_kwargs)]

    return my_choice_list


def get_division_choices(all=False, region_filter=None):
    division_list = set(
        [shared_models.Section.objects.get(pk=s[0]).division_id for s in get_section_choices(all=all, region_filter=region_filter)])
    return [(d.id, str(d)) for d in
            shared_models.Division.objects.filter(id__in=division_list).order_by("branch__region", "name")]


def get_region_choices(all=False):
    region_list = set(
        [shared_models.Division.objects.get(pk=d[0]).branch.region_id for d in get_division_choices(all=all)])
    return [(r.id, str(r)) for r in
            shared_models.Region.objects.filter(id__in=region_list).order_by("name", )]


def get_omcatagory_choices():
    return [(o.id, str(o)) for o in models.OMCategory.objects.all()]


def get_funding_sources(all=False):
    return [(fs.id, str(fs)) for fs in models.FundingSource.objects.all()]


def get_user_fte_breakdown(user, fiscal_year_id):
    staff_instances = models.Staff.objects.filter(user=user, project_year__fiscal_year_id=fiscal_year_id)
    my_dict = dict()
    my_dict['fiscal_year'] = str(shared_models.FiscalYear.objects.get(pk=fiscal_year_id))
    my_dict['draft'] = nz(staff_instances.filter(
        project_year__status=1
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    my_dict['recommended'] = nz(staff_instances.filter(
        project_year__status=3
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    my_dict['approved'] = nz(staff_instances.filter(
        project_year__status=4
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    return my_dict


def financial_project_year_summary_data(project_year):
    """ this function will return a list, where each row corresponds to a funding source"""
    # for every funding source, we will want to summarize: Salary, O&M, Capital and TOTAL
    my_list = []

    for fs in project_year.get_funding_sources():
        my_dict = dict()
        my_dict["type"] = fs.get_funding_source_type_display()
        my_dict["name"] = str(fs)
        my_dict["salary"] = 0
        my_dict["om"] = 0
        my_dict["capital"] = 0

        # first calc for staff
        for staff in project_year.staff_set.filter(funding_source=fs):
            # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
            if not staff.employee_type.exclude_from_rollup:
                if staff.employee_type.cost_type == 1:
                    my_dict["salary"] += nz(staff.amount, 0)
                elif staff.employee_type.cost_type == 2:
                    my_dict["om"] += nz(staff.amount, 0)

        # O&M costs
        for cost in project_year.omcost_set.filter(funding_source=fs):
            my_dict["om"] += nz(cost.amount, 0)

        # Capital costs
        for cost in project_year.capitalcost_set.filter(funding_source=fs):
            my_dict["capital"] += nz(cost.amount, 0)

        my_dict["total"] = my_dict["salary"] + my_dict["om"] + my_dict["capital"]

        my_list.append(my_dict)

    return my_list


def financial_project_summary_data(project):
    my_list = []

    for fs in project.get_funding_sources():
        my_dict = dict()
        my_dict["type"] = fs.get_funding_source_type_display()
        my_dict["name"] = str(fs)
        my_dict["salary"] = 0
        my_dict["om"] = 0
        my_dict["capital"] = 0

        # first calc for staff
        for staff in models.Staff.objects.filter(funding_source=fs, project_year__project=project):
            # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
            if not staff.employee_type.exclude_from_rollup:
                if staff.employee_type.cost_type == 1:
                    my_dict["salary"] += nz(staff.amount, 0)
                elif staff.employee_type.cost_type == 2:
                    my_dict["om"] += nz(staff.amount, 0)

        # O&M costs
        for cost in models.OMCost.objects.filter(funding_source=fs, project_year__project=project):
            my_dict["om"] += nz(cost.amount, 0)

        # Capital costs
        for cost in models.CapitalCost.objects.filter(funding_source=fs, project_year__project=project):
            my_dict["capital"] += nz(cost.amount, 0)

        my_dict["total"] = my_dict["salary"] + my_dict["om"] + my_dict["capital"]

        my_list.append(my_dict)

    return my_list


def multiple_projects_financial_summary(project_list):
    my_dict = {}

    # first, get the list of funding sources
    funding_sources = []
    for project in project_list:
        funding_sources.extend(project.get_funding_sources())
    funding_sources = list(set(funding_sources))
    funding_sources_order = ["{} {}".format(fs.funding_source_type, fs.tname) for fs in funding_sources]
    for fs in [x for _, x in sorted(zip(funding_sources_order, funding_sources))]:
        my_dict[fs] = {}
        my_dict[fs]["salary"] = 0
        my_dict[fs]["om"] = 0
        my_dict[fs]["capital"] = 0
        my_dict[fs]["total"] = 0
        for project in project_list.all():
            # first calc for staff
            for staff in project.staff_members.filter(funding_source=fs):
                # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
                if not staff.employee_type.exclude_from_rollup:
                    if staff.employee_type.cost_type == 1:
                        my_dict[fs]["salary"] += nz(staff.cost, 0)
                    elif staff.employee_type.cost_type == 2:
                        my_dict[fs]["om"] += nz(staff.cost, 0)
            # O&M costs
            for cost in project.om_costs.filter(funding_source=fs):
                my_dict[fs]["om"] += nz(cost.budget_requested, 0)
            # Capital costs
            for cost in project.capital_costs.filter(funding_source=fs):
                my_dict[fs]["capital"] += nz(cost.budget_requested, 0)

    my_dict["total"] = {}
    my_dict["total"]["salary"] = 0
    my_dict["total"]["om"] = 0
    my_dict["total"]["capital"] = 0
    my_dict["total"]["total"] = 0
    for fs in funding_sources:
        my_dict[fs]["total"] = float(my_dict[fs]["capital"]) + float(my_dict[fs]["salary"]) + float(my_dict[fs]["om"])
        my_dict["total"]["salary"] += my_dict[fs]["salary"]
        my_dict["total"]["om"] += my_dict[fs]["om"]
        my_dict["total"]["capital"] += my_dict[fs]["capital"]
        my_dict["total"]["total"] += my_dict[fs]["total"]

    return my_dict


def get_project_field_list(project):
    my_list = [
        'id',
        'section',
        # 'title',
        'overview',  # do not call the html field directly or we loose the ability to get the model's verbose name
        'activity_type',
        'functional_group',
        'default_funding_source',
        'start_date',
        'end_date',
        'fiscal_years',
        'funding_sources',
        'lead_staff',
        'tags',
        'metadata|{}'.format(_("metadata")),
    ]
    return my_list


def get_project_year_field_list(project_year=None):
    my_list = [
        'dates|dates',
        'priorities',  # do not call the html field directly or we loose the ability to get the model's verbose name
        'deliverables',  # do not call the html field directly or we loose the ability to get the model's verbose name

        # SPECIALIZED EQUIPMENT COMPONENT
        #################################
        'requires_specialized_equipment',
        'technical_service_needs' if not project_year or project_year.requires_specialized_equipment else None,
        'mobilization_needs' if not project_year or project_year.requires_specialized_equipment else None,

        # FIELD COMPONENT
        #################
        'has_field_component',
        'vehicle_needs' if not project_year or project_year.has_field_component else None,
        'ship_needs' if not project_year or project_year.has_field_component else None,
        'coip_reference_id' if not project_year or project_year.has_field_component else None,
        'instrumentation' if not project_year or project_year.has_field_component else None,
        'owner_of_instrumentation' if not project_year or project_year.has_field_component else None,
        'requires_field_staff' if not project_year or project_year.has_field_component else None,
        'field_staff_needs' if not project_year or project_year.has_field_component and project_year.requires_field_staff else None,

        # DATA COMPONENT
        ################
        'has_data_component',
        'data_collected' if not project_year or project_year.has_data_component else None,
        'data_products' if not project_year or project_year.has_data_component else None,
        'open_data_eligible' if not project_year or project_year.has_data_component else None,
        'data_storage_plan' if not project_year or project_year.has_data_component else None,
        'data_management_needs' if not project_year or project_year.has_data_component else None,

        # LAB COMPONENT
        ###############
        'has_lab_component',
        'requires_abl_services' if not project_year or project_year.has_lab_component else None,
        'requires_lab_space' if not project_year or project_year.has_lab_component else None,
        'requires_other_lab_support' if not project_year or project_year.has_lab_component else None,
        'other_lab_support_needs' if not project_year or project_year.has_lab_component else None,

        'it_needs',
        'additional_notes',
        'coding',
        'submitted',
        'formatted_status|{}'.format(_("status")),
        'allocated_budget',
        'metadata|{}'.format(_("metadata")),
    ]

    # remove any instances of None
    while None in my_list: my_list.remove(None)

    return my_list


def get_staff_field_list():
    my_list = [
        'smart_name|{}'.format(_("name")),
        'funding_source',
        'is_lead',
        'employee_type',
        'level',
        'duration_weeks',
        'overtime_hours',
        # 'overtime_description',
        'student_program',
        'amount',
    ]
    return my_list


def get_om_field_list():
    my_list = [
        'category_type|{}'.format(_("category type")),
        'om_category',
        'description',
        'funding_source',
        'amount',
    ]
    return my_list


def get_capital_field_list():
    my_list = [
        'category',
        'description',
        'funding_source',
        'amount',
    ]
    return my_list


def get_milestone_field_list():
    my_list = [
        'name',
        'description',
        'target_date',
        'latest_update|{}'.format(_("latest status")),
    ]
    return my_list


def get_collaborator_field_list():
    my_list = [
        'name',
        'critical',
        'notes',
    ]
    return my_list


def get_gc_cost_field_list():
    my_list = [
        'recipient_org',
        'project_lead',
        'proposed_title',
        'gc_program',
        'amount',
    ]
    return my_list


def get_agreement_field_list():
    my_list = [
        'partner_organization',
        'project_lead',
        'agreement_title',
        'new_or_existing',
        'notes',
    ]
    return my_list


def get_file_field_list():
    my_list = [
        'name',
        'ref|{}'.format("reference"),
        'external_url',
        'file',
        'date_created',

    ]
    return my_list
