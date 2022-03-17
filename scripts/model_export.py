import os
import json

import django.contrib.auth.models
from django.core import serializers


# models_to_export is an array of models fed in from the shell script running this command.
# output dir is the directory to output the fixtures to, if None fixtures will be created
# in the scripts directory
#
# from scripts import model_export
# from maret import models
#
# models_to_export = [models.Interaction, models.Committee]
# model_export.export_fixtures(modesl_to_export, r'./maret/fixtures/)
import ppt.models
import shared_models.models


def export_fixtures(models_to_export, output_path=None):

    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for
    seeding new instances"""
    if not output_path:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        parsed = json.loads(data)
        my_label = model._meta.db_table
        f = open(os.path.join(output_path, f'{my_label}.json'), 'w', encoding='utf-8')
        f.write(json.dumps(parsed, indent=4, sort_keys=True))
        f.close()


def export_queryset_fixtures(label, querysets, output_path=None):

    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for
    seeding new instances"""
    if not output_path:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    f = open(os.path.join(output_path, f'{label}_qs.json'), 'w', encoding='utf-8')

    parsed = None
    for queryset in querysets:
        print("loading QS")
        data = serializers.serialize("json", queryset)
        load = json.loads(data)
        try:
            if parsed is None:
                parsed = load
            else:
                parsed = parsed + load

        except AttributeError:
            print("has no items from {} and {}".format(str(data)[:100]), str(parsed)[:100])
            break

    f.write(json.dumps(parsed, indent=4, sort_keys=True))
    f.close()


def export_ppt_fixtures(output_path=None):

    querysets = []
    users = None

    query_years = [2022,2023,]

    """ ppt_models.ProjectYear """
    print("Project years")
    prj_years = ppt.models.ProjectYear.objects.filter(fiscal_year__in=query_years)
    users = django.contrib.auth.models.User.objects.filter(last_mod_by_projects_projectyear__in=prj_years)

    """ -> ppt_models.Project """
    print("Project years, PPT Project")
    prjs = ppt.models.Project.objects.filter(years__in=prj_years)

    """ --> shared_models.Section """
    print("Project years, PPT Project, sections")
    sec = shared_models.models.Section.objects.filter(ppt__in=prjs)

    """ --> ppt_models.ActivityType """
    print("Project years, PPT Project, AcitivityTypes")
    act_type = ppt.models.ActivityType.objects.all()

    """ --> ppt_models.FunctionalGroup """
    print("Project years, PPT Project, FunctionalGroup")
    fun_group = ppt.models.FunctionalGroup.objects.filter(projects__in=prjs)

    """ ---> ppt_models.Theme """
    print("Project years, PPT Project, FunctionalGroup, Theme")
    fun_themes = ppt.models.Theme.objects.filter(functional_groups__in=fun_group)

    """ ---> shared_models.Section """
    print("Project years, PPT Project, FunctionalGroup, Section")
    sec = sec | shared_models.models.Section.objects.filter(functional_groups2__in=fun_group)

    """ --> ppt_models.FundingSource """
    print("Project years, PPT Project, FundingSource")
    fun_sor = ppt.models.FundingSource.objects.all()

    """ --> shared_models.Citation """
    print("Project years, PPT Project, Citation")
    cit = shared_models.models.Citation.objects.filter(projects__in=prjs)

    """ ---> shared_models.Publications """
    print("Project years, PPT Project, Citation, Publications")
    pubs = shared_models.models.Publication.objects.all()

    """ --> shared_models.Organization """
    print("Project years, PPT Project, Organization")
    orgs = shared_models.models.Organization.objects.filter(projects__in=prjs)

    """ ---> shared_models.Location """
    print("Project years, PPT Project, Organization, Location")
    org_loc = shared_models.models.Location.objects.all()

    """ --> ppt_models.CSRFClientInformation """
    print("Project years, PPT Project, CSRFClientInformation")
    csrf = ppt.models.CSRFClientInformation.objects.filter(projects__in=prjs)

    """ ---> ppt_models.CSRFPriority """
    print("CSRFPriority")
    csrf_pri = ppt.models.CSRFPriority.objects.all()

    """ --> shared_models.FiscalYear """
    print("FiscalYear")
    fis_year = shared_models.models.FiscalYear.objects.all()

    """ --> User """
    print("Project years, PPT Project, User")
    users = users | django.contrib.auth.models.User.objects.filter(last_mod_by_projects_project__in=prjs)

    """ -> shared_models.ResponsibilityCenter """
    print("Project years, ResponsibilityCenter")
    rep = shared_models.models.ResponsibilityCenter.objects.filter(projects_ppt__in=prj_years)

    """ clear out the managers for rep centers"""
    for r in rep:
        r.manager = None

    """ -> shared_models.AllotmentCode """
    print("Project years, AllotmentCode")
    all_code = shared_models.models.AllotmentCode.objects.filter(projects_ppt__in=prj_years)

    """ --> shared_models.AllotmentCategory """
    print("Project years, AllotmentCode, AllotmentCategory")
    all_cat = shared_models.models.AllotmentCategory.objects.filter(allotment_codes__in=all_code)

    """ -> shared_models.Project """
    print("Project years, shared_models projects")
    share_prjs = shared_models.models.Project.objects.filter(projects__in=prj_years)

    print("Compiling users, divisions, branches and regions")
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_sections__in=sec)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_admin_sections__in=sec)

    """ ---> shared_models.Division """
    div = shared_models.models.Division.objects.filter(sections__in=sec)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_divisions__in=div)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_admin_divisions__in=div)

    """ ---> shared_models.Branch """
    bra = shared_models.models.Branch.objects.filter(divisions__in=div)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_branches__in=bra)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_admin_branches__in=bra)

    """ ---> shared_models.Region """
    reg = shared_models.models.Region.objects.filter(branches__in=bra)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_regions__in=reg)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_admin_regions__in=reg)

    """ ---> shared_models.Sector """
    sect = shared_models.models.Sector.objects.filter(branches__in=bra)
    reg = reg | shared_models.models.Region.objects.filter(sectors__in=sect)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_sectors__in=sect)
    users = users | django.contrib.auth.models.User.objects.filter(shared_models_admin_sectors__in=sect)

    print("Compiling Query Sets")

    querysets.append(users)

    querysets.append(share_prjs)
    querysets.append(all_cat)
    querysets.append(all_code)
    querysets.append(rep)
    querysets.append(fis_year)
    querysets.append(csrf_pri)
    querysets.append(csrf)
    querysets.append(org_loc)
    querysets.append(orgs)
    querysets.append(pubs)
    querysets.append(cit)
    querysets.append(fun_sor)
    querysets.append(fun_themes)
    querysets.append(fun_group)
    querysets.append(act_type)
    querysets.append(sect)
    querysets.append(reg)
    querysets.append(bra)
    querysets.append(div)
    querysets.append(sec)
    querysets.append(prjs)
    querysets.append(prj_years)

    print("Exporting data to file")
    export_queryset_fixtures("ppt_load", querysets)
