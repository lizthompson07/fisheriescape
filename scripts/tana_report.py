import os

from ppt import models
from shared_models import models as shared_models

import csv

""" ---- to run --------------------------------------- """
""" > python manage.py shell                            """
""" >>> from scripts import tana_report                 """
""" >>> tana_report.generate_susan_report()             """
"""---------------------------------------------------- """

"""---------------------------------------------------- """
""" ---- handy to know if you make changes to the script"""
""" ---- and want to reload it without having to exit   """
""" ---- the shell ------------------------------------ """
""" >>> from importlib import reload                    """
""" >>> reload(tana_report)                             """
""" >>> tana_report.generate_susan_report()             """
"""---------------------------------------------------- """


def generate_susan_report():

    """ select the fiscal year, note 2023 is for the 2022-2023 fiscal year """
    year = 2023

    """ select the section name """
    section_name = "Invertebrates and Species at Risk Section"
    section = shared_models.Section.objects.get(name=section_name)

    """ for this report we're using the fiscal year, the section name **and** if the ProjectYear has_field_component """
    project_years = models.ProjectYear.objects.filter(has_field_component=True, fiscal_year_id=year,
                                                      project__section_id=section)

    """ The project year has a list of numbers for its status_choices, we'll create a 'dictionary' to use to replace """
    """ the id values with the proper text values from the ProjectYear.status_choice list """
    status_list = models.ProjectYear.status_choices
    status = {status_list[i][0]: status_list[i][1] for i in range(0, len(status_list))}

    """ We're going to dump our output into the dm_apps/dm_apps/scripts/fixtures/ directory """
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

    """ if the directory doesn't exist create it or we'll get an error when trying to create a file in the next step """
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    """ create the file, the f'report_name...' is a fancy way to *format* strings, you can put variables between the """
    """ brackets to append variables on to the string """
    f = open(os.path.join(output_path, f'susan_report_{year}.csv'), 'w', newline='', encoding='utf-8')

    """ create a Comma Separated Value file writer because we're writing csv files and this makes it easier to format"""
    writer = csv.writer(f)

    """ write the first row of the file, this is the header row with a comma separated list of column headers """
    writer.writerow([
        'ID',
        'Approved',
        'Title',
        'Section',
        'Functional group',
        'Start date of project',
        'End date of project',
        'Project years',
        'Project leads',
        'Project overview',

        'ship_needs',
    ])

    """ now iterate over each project year, collecting the required variables and write the array matching the """
    """ column header row created above """
    for p in project_years:
        """ query the fiscal years for all the years we have project years for """
        years = ", ".join([y.fiscal_year.full for y in p.project.years.all()])

        """ get the list of project leads"""
        leads_as_users = p.get_project_leads_as_users()
        leads = ""
        if leads_as_users:
            leads = ", ".join([u.first_name + " " + u.last_name for u in leads_as_users])

        writer.writerow([p.project.pk, status.get(p.status), p.project.title, section_name, p.project.functional_group,
                         p.start_date, p.end_date, years, leads, p.project.overview,

                         p.vehicle_needs,])

    """ close the file or you won't be able to delete, or move it until you exit the django shell """
    f.close()