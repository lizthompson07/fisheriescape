import os

import pytz
from django.core import serializers
from django.core.files import File
from django.utils import timezone
from django.utils.timezone import make_aware
from textile import textile

from shared_models import models as shared_models
from . import models


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.Theme,
        models.ActivityType,
        models.FundingSourceType,
        models.Status,
        models.HelpText,
        models.EmployeeType,
        models.Level,
        models.OMCategory,
        shared_models.FiscalYear,
        # shared_models.ResponsibilityCenter,
        # shared_models.AllotmentCode,
        # shared_models.AllotmentCategory,
        # shared_models.BusinessLine,
        # shared_models.LineObject,
        # shared_models.Project,
        # models.FunctionalGroup,
        # models.FundingSource,

        # models.Project,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


# def resave_all(projects = models.Project.objects.all()):
#     for p in projects2:
#         for obj in models.OMCategory.objects.all():
#             if not models.OMCost.objects.filter(project=p, om_category=obj).count():
#                 new_item = models.OMCost.objects.create(project=p, om_category=obj)
#                 new_item.save()

def resave_all(projects=models.Project.objects.all()):
    for p in models.Project.objects.all():
        p.save()


def compare_html():
    projects = models.Project.objects.all()

    for p in projects2:
        if p.description:
            if not textile(p.description) == p.description_html:
                print("mismatch in project {}".format(p.id))
        if p.priorities:
            if not textile(p.priorities) == p.priorities_html:
                print("mismatch in project {}".format(p.id))
        if p.deliverables:
            if not textile(p.deliverables) == p.deliverables_html:
                print("mismatch in project {}".format(p.id))


def replace_html():
    projects = models.Project.objects.all()

    for p in projects2:
        should_save = False
        if p.description:
            p.description = p.description_html
            should_save = True

        if p.priorities:
            p.priorities = p.priorities_html
            should_save = True

        if p.deliverables:
            p.deliverables = p.deliverables_html
            should_save = True

        if should_save:
            p.save()


def clean_project():
    projects = models.Project.objects.all()

    for p in projects2:
        p.is_negotiable = None
        p.save()


def copy_over_project_codes():
    projects = models.Project.objects.filter(existing_project_code__isnull=False)

    for p in projects2:
        p.existing_project_codes.add(p.existing_project_code)


def recommend_approved_projects():
    projects = models.Project.objects.filter(approved=True)

    for p in projects2:
        p.recommended_for_funding = True
        p.approved = False
        p.save()


def clear_all_approvals():
    projects = models.Project.objects.filter(approved=False)
    for p in projects2:
        p.approved = None
        p.save()


def fetch_project_data():
    from projects import models as omodels
    import html2markdown
    """ objective of this function is to port over data from projects app to projects2"""
    projects = omodels.Project.objects.all()
    # projects = omodels.Project.objects.filter(id=414)
    for old_p in projects:
        new_p, created = models.Project.objects.get_or_create(
            id=old_p.id,
        )
        # easy things to assign

        new_p.title = old_p.project_title
        new_p.section = old_p.section
        new_p.activity_type_id = old_p.activity_type_id
        new_p.functional_group_id = old_p.functional_group_id
        new_p.default_funding_source_id = old_p.default_funding_source_id
        if old_p.description: new_p.overview = html2markdown.convert(old_p.description)
        new_p.is_hidden = old_p.is_hidden
        new_p.updated_at = old_p.date_last_modified
        new_p.modified_by = old_p.last_modified_by

        new_p.save()

        # tags
        for t in old_p.tags.all():
            if not models.Tag.objects.filter(id=t.id).exists():
                models.Tag.objects.create(
                    id=t.id,
                    name=t.name,
                    nom=t.nom,
                )
            new_p.tags.add(t.id)

        # YEAR

        # let's create a project year based on the only info we have
        new_py, created = models.ProjectYear.objects.get_or_create(
            project_id=old_p.id,
        )
        # we will only be creating one entry per project so this is fine.

        if old_p.start_date:
            new_py.start_date = old_p.start_date
        else:
            new_py.start_date = make_aware(timezone.datetime(2020, 4, 1), timezone=pytz.timezone("UTC"))

        new_py.end_date = old_p.end_date
        if old_p.priorities: new_py.priorities = html2markdown.convert(old_p.priorities)
        if old_p.deliverables: new_py.deliverables = html2markdown.convert(old_p.deliverables)
        new_py.requires_specialized_equipment = old_p.requires_specialized_equipment
        new_py.technical_service_needs = old_p.technical_service_needs
        new_py.mobilization_needs = old_p.mobilization_needs

        if old_p.vehicle_needs or old_p.ship_needs:
            new_py.has_field_component = True
        else:
            new_py.has_field_component = False

        if old_p.vehicle_needs: new_py.vehicle_needs = html2markdown.convert(old_p.vehicle_needs)
        if old_p.ship_needs: new_py.ship_needs = html2markdown.convert(old_p.ship_needs)

        new_py.coip_reference_id = old_p.coip_reference_id
        new_py.instrumentation = old_p.instrumentation
        new_py.owner_of_instrumentation = old_p.owner_of_instrumentation
        new_py.requires_field_staff = old_p.requires_field_staff
        new_py.field_staff_needs = old_p.field_staff_needs

        if old_p.data_collection or old_p.regional_dm_needs or old_p.data_storage:
            new_py.has_data_component = True
        else:
            new_py.has_data_component = False

        if old_p.data_collection: new_py.data_collection = html2markdown.convert(old_p.data_collection)
        new_py.data_products = old_p.data_products
        new_py.open_data_eligible = old_p.open_data_eligible
        if old_p.regional_dm_needs: new_py.data_management_needs = html2markdown.convert(old_p.regional_dm_needs)
        if old_p.data_storage: new_py.data_storage = html2markdown.convert(old_p.data_storage)

        if old_p.other_lab_support_needs:
            new_py.has_lab_component = True
        else:
            new_py.has_lab_component = False

        new_py.requires_abl_services = old_p.abl_services_required
        new_py.requires_lab_space = old_p.lab_space_required
        new_py.requires_other_lab_support = old_p.requires_other_lab_support
        if old_p.other_lab_support_needs: new_py.other_lab_support_needs = html2markdown.convert(old_p.other_lab_support_needs)

        if old_p.it_needs:
            new_py.it_needs = html2markdown.convert(old_p.it_needs)
        new_py.additional_notes = old_p.notes

        new_py.responsibility_center = old_p.responsibility_center
        new_py.allotment_code = old_p.allotment_code
        new_py.notification_email_sent = old_p.notification_email_sent
        new_py.administrative_notes = old_p.meeting_notes
        new_py.updated_at = old_p.date_last_modified
        new_py.modified_by = old_p.last_modified_by
        new_py.allocated_budget = old_p.allocated_budget

        if old_p.submitted:
            new_py.submitted = old_p.date_last_modified

        new_py.save()

        # project codes
        for c in old_p.existing_project_codes.all():
            new_py.existing_project_codes.add(c)

        # STAFF
        qry = omodels.Staff.objects.filter(project=old_p)
        for obj in qry:
            try:
                new_staff, created = models.Staff.objects.get_or_create(
                    id=obj.id,
                    project_year=new_py,
                    employee_type_id=obj.employee_type_id,
                )
                new_staff.is_lead = obj.lead
                new_staff.funding_source_id = obj.funding_source_id
                new_staff.user = obj.user
                new_staff.name = obj.name
                new_staff.level_id = obj.level_id
                new_staff.student_program = obj.student_program
                new_staff.duration_weeks = obj.duration_weeks
                new_staff.overtime_hours = obj.overtime_hours
                new_staff.overtime_description = obj.overtime_description
                new_staff.amount = obj.cost
                new_staff.save()
            except Exception as e:
                print(e)

        # OM COST
        qry = omodels.OMCost.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.OMCost.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                om_category_id=obj.om_category_id
            )
            new_obj.funding_source_id = obj.funding_source_id
            new_obj.description = obj.description
            new_obj.amount = obj.budget_requested
            new_obj.save()

        # CAPITAL COST
        qry = omodels.CapitalCost.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.CapitalCost.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                category=obj.category
            )
            new_obj.funding_source_id = obj.funding_source_id
            new_obj.description = obj.description
            new_obj.amount = obj.budget_requested
            new_obj.save()

        # GC COST
        qry = omodels.GCCost.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.GCCost.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
            )
            new_obj.recipient_org = obj.recipient_org
            new_obj.project_lead = obj.project_lead
            new_obj.proposed_title = obj.proposed_title
            new_obj.gc_program = obj.gc_program
            new_obj.amount = obj.budget_requested
            new_obj.save()

        # Collaborator
        qry = omodels.Collaborator.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.Collaborator.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
            )
            new_obj.name = obj.name
            new_obj.critical = obj.critical
            new_obj.notes = obj.notes
            new_obj.save()

        # Collaborative agreement
        qry = omodels.CollaborativeAgreement.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.CollaborativeAgreement.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                new_or_existing=obj.new_or_existing
            )
            new_obj.partner_organization = obj.partner_organization
            new_obj.project_lead = obj.project_lead
            new_obj.agreement_title = obj.agreement_title
            new_obj.notes = obj.notes
            new_obj.save()

        # MILESTONE
        qry = omodels.Milestone.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.Milestone.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                name=obj.name,
                description=obj.description,
            )

        # STATUS REPORT
        qry = omodels.StatusReport.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.StatusReport.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
            )
            new_obj.status = obj.status_id
            new_obj.major_accomplishments = obj.major_accomplishments
            new_obj.major_issues = obj.major_issues

            new_obj.target_completion_date = obj.target_completion_date
            new_obj.rationale_for_modified_completion_date = obj.rationale_for_modified_completion_date
            new_obj.general_comment = obj.general_comment
            new_obj.section_head_comment = obj.section_head_comment
            new_obj.section_head_reviewed = obj.section_head_reviewed
            new_obj.date_created = obj.date_created
            new_obj.created_by = obj.created_by
            new_obj.save()

        # MILESTONE
        qry = omodels.Milestone.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.Milestone.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                name=obj.name,
                description=obj.description,
            )

            # MILESTONE UPDATE
            qry1 = omodels.MilestoneUpdate.objects.filter(milestone=obj)
            for obj1 in qry1:
                new_obj1, created1 = models.MilestoneUpdate.objects.get_or_create(
                    id=obj1.id,
                    milestone_id=new_obj.id,
                    status_report_id=obj1.status_report_id,
                )
                new_obj1.notes = obj1.notes
                new_obj1.status = obj1.status_id
                new_obj1.save()

        # FILE
        qry = omodels.File.objects.filter(project=old_p)
        for obj in qry:
            new_obj, created = models.File.objects.get_or_create(
                id=obj.id,
                project=new_p,
                name=obj.name,
                file=obj.file,
            )
            new_obj.project_year = new_py
            new_obj.external_url = obj.external_url
            new_obj.status_report_id = obj.status_report_id
            new_obj.date_created = obj.date_created
            new_obj.save()

        new_p.save()
"""

    


    # OTHER FIELDS
    status
    recommended_for_funding
    approved

"""
