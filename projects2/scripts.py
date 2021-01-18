import csv
import os

import pytz
from django.conf import settings
from django.core import serializers
from django.core.files import File
from django.db import IntegrityError
from django.utils import timezone
from django.utils.timezone import make_aware
from textile import textile

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from . import models


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.ActivityType,
        models.EmployeeType,
        models.Level,
        models.OMCategory,
        shared_models.FiscalYear,
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


def resave_all_reviews(projects=models.Project.objects.all()):
    for obj in models.Review.objects.all():
        obj.save()


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
        new_py.approval_notification_email_sent = old_p.notification_email_sent
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
            new_obj, created = models.Activity.objects.get_or_create(
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
            new_obj, created = models.Activity.objects.get_or_create(
                id=obj.id,
                project_year=new_py,
                name=obj.name,
                description=obj.description,
            )

            # MILESTONE UPDATE
            qry1 = omodels.MilestoneUpdate.objects.filter(milestone=obj)
            for obj1 in qry1:
                new_obj1, created1 = models.ActivityUpdate.objects.get_or_create(
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


def fetch_project_approval_data():
    from projects import models as omodels
    projects = omodels.Project.objects.all()
    # projects = omodels.Project.objects.filter(id=414)
    for old_p in projects:
        new_p, created = models.Project.objects.get_or_create(
            id=old_p.id,
        )

        # YEAR
        qry = models.ProjectYear.objects.filter(project_id=old_p.id)
        if qry.exists():
            if qry.count() > 1:
                print("multiple project years for ", old_p.id)
            else:
                py = qry.first()
                if old_p.approved:
                    py.status = 4
                elif old_p.recommended_for_funding:
                    py.status = 3
                elif old_p.submitted:
                    py.status = 2
                else:
                    py.status = 1
                py.save()

        else:
            print("no project year for ", old_p)


def fix_project_formatting():
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
        if created: print("new project (!!)")

        if old_p.description:
            new_p.overview = html2markdown.convert(old_p.description)
            new_p.save()


def from_project_to_reviewer():
    from projects import models as omodels
    projects = omodels.Project.objects.all()

    for old_p in projects:
        qs = models.ProjectYear.objects.filter(project_id=old_p.id)
        if qs.exists():
            if qs.count() > 1:
                print("problem, more than one project year of this project exists: ", old_p.project_title, " (", old_p.id,
                      ") Going to choose this one: ",
                      qs.first(), " of ", listrify(qs))

            new_py = qs.first()
            review, created = models.Review.objects.get_or_create(
                project_year=new_py,
            )
            review.allocated_budget = new_py.allocated_budget
            review.approval_status = old_p.approved  # will be 1, 0 , None
            review.approval_notification_email_sent = old_p.notification_email_sent
            review.general_comment = old_p.meeting_notes
            review.approver_comment = old_p.meeting_notes
            review.save()
        else:
            print("cannot find matching project:", old_p.id, old_p.project_title)


def transform_deliverables():
    project_years = models.ProjectYear.objects.filter(deliverables__isnull=False)
    for py in project_years:
        models.Activity.objects.get_or_create(
            project_year=py,
            name="MISSING NAME",
            description=py.deliverables,
            type=2,
        )


def copy_orgs():
    from inventory.models import Organization, Location
    inventory_locs = Location.objects.filter(location_eng__isnull=False)
    for loc in inventory_locs:
        new_loc, created = shared_models.Location.objects.get_or_create(
            id=loc.id,
            location_en=loc.location_eng,
            location_fr=loc.location_fre,
            country=loc.country,
            abbrev_en=loc.abbrev_eng,
            abbrev_fr=loc.abbrev_fre,
            uuid_gcmd=loc.uuid_gcmd,

        )

    inventory_orgs = Organization.objects.filter(name_eng__isnull=False)
    i = 0
    for org in inventory_orgs:
        new_org, created = shared_models.Organization.objects.get_or_create(
            id=org.id,
        )
        new_org.name = org.name_eng
        new_org.nom = org.name_fre
        new_org.abbrev = org.abbrev
        new_org.address = org.address
        new_org.city = org.city
        new_org.postal_code = org.postal_code
        new_org.location_id = org.location_id

        try:
            new_org.save()
        except Exception as e:
            print(e, new_org.name)
            new_org.name += f" ({i})"
            new_org.save()

        i += 1


def fix_submitted_project_years():
    project_years = models.ProjectYear.objects.filter(status__in=[2, 3, 4, 5], submitted__isnull=True)
    for py in project_years:
        if py.updated_at:
            py.submitted = py.updated_at
        else:
            py.submitted = timezone.now()
        py.save()


def build_collaborations():
    for item in models.GCCost.objects.all():
        models.Collaboration.objects.get_or_create(
            type=2,
            project_year=item.project_year,
            organization=item.recipient_org,
            people=item.project_lead,
            agreement_title=item.proposed_title,
            gc_program=item.gc_program,
            amount=item.amount,
            new_or_existing=2,
        )

    for item in models.CollaborativeAgreement.objects.all():
        models.Collaboration.objects.get_or_create(
            type=3,
            project_year=item.project_year,
            organization=item.partner_organization,
            people=item.project_lead,
            agreement_title=item.agreement_title,
            new_or_existing=item.new_or_existing,
            notes=item.notes,
        )

    for item in models.Collaborator.objects.all():
        models.Collaboration.objects.get_or_create(
            type=1,
            project_year=item.project_year,
            organization=item.name,
            critical=item.critical,
            notes=item.notes,
            new_or_existing=2,
        )


def digest_priorities():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'projects2', 'csrf_priorities.csv')
    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # theme
            pin = row['Priority identification number (PIN)']
            theme_code = pin.split("-")[0]
            priority_code = pin.split("-")[1]
            theme_name = row['Theme'].strip().replace('\n', "")
            theme_nom = row['Thème']

            theme, created = models.CSRFTheme.objects.get_or_create(
                name=theme_name, code=theme_code
            )
            theme.nom = theme_nom
            theme.save()

            # sub-theme
            sub_theme_name = row['Sub-Theme'].strip().replace('\n', "")
            sub_theme_nom = row['Sous-thème']
            sub_theme, created = models.CSRFSubTheme.objects.get_or_create(
                csrf_theme=theme, name=sub_theme_name
            )
            sub_theme.nom = sub_theme_nom
            sub_theme.save()

            # priority
            priority_name = row['Priority for Research'].strip().replace('\n', "")
            priority_nom = row['Priorité de recherche']
            try:
                priority, created = models.CSRFPriority.objects.get_or_create(
                    csrf_sub_theme=sub_theme, code=pin, name=priority_name
                )
            except IntegrityError as E:
                print(E)
                print(row)
                print(sub_theme.id, pin, priority_name)

            priority.nom = priority_nom
            priority.save()

            # client information
            priority_desc = row['Additional information supplied by the client']
            priority_desc_fr = row['Informations complémentaires fournies par le client']

            client_information, created = models.CSRFClientInformation.objects.get_or_create(
                csrf_priority=priority, name=priority_desc
            )
            client_information.nom = priority_desc_fr
            client_information.save()


def copy_citations():
    from inventory.models import Citation as OldCitation, Resource
    old_citations = OldCitation.objects.all()

    for old_cit in old_citations:
        old_pub = old_cit.publication

        new_pub = None
        if old_pub:
            # make sure the publication exists
            new_pub, created = shared_models.Publication.objects.get_or_create(pk=old_pub.id, name=old_pub.name)

        # create the new citation based on the old one
        new_cit, created = shared_models.Citation.objects.get_or_create(
            id=old_cit.id,
            name=old_cit.title_eng,
            nom=old_cit.title_fre,
            authors=old_cit.authors,
            year=old_cit.year,
            publication=new_pub,
            pub_number=old_cit.pub_number,
            url_en=old_cit.url_eng,
            url_fr=old_cit.url_fre,
            abstract_en=old_cit.abstract_eng,
            abstract_fr=old_cit.abstract_fre,
            series=old_cit.series,
            region=old_cit.region,
        )

    for r in Resource.objects.all():
        for cit_old in r.citations.all():
            r.citations2.add(cit_old.id)



def populate_quicknames():
    for item in models.CSRFClientInformation.objects.all():
        if item.description_en:
            item.name = item.quickname_en
        if item.description_fr:
            item.nom = item.quickname_fr
        item.save()

