import os

from django.core import serializers
from django.core.files import File
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
    for p in projects2:
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
    """ objective of this function is to port over data from projects app to projects2"""
    projects = omodels.Project.objects.all()
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
        new_p.overview = old_p.description
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
