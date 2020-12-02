import os
from io import BytesIO

from django.conf import settings
from django.utils.translation import gettext as _
from docx import Document
from openpyxl import load_workbook

from lib.templatetags.custom_filters import nz
from . import models


def generate_acrdp_application(project):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
    target_file = "temp_export.docx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)

    template_file_path = os.path.join(settings.BASE_DIR, 'projects2', 'static', "projects2", "acrdp_template.docx")

    with open(template_file_path, 'rb') as f:
        source_stream = BytesIO(f.read())
    document = Document(source_stream)
    source_stream.close()

    lead = None
    contact_info = None
    if project.lead_staff.exists():
        lead = project.lead_staff.first().user
        contact_info = _("{full_address}\n\n{email}\n\n{phone}").format(
            full_address=project.organization.full_address if project.organization else "MISSING!",
            email=lead.email,
            phone=lead.profile.phone
        )

    priorities = str()
    for year in project.years.all():
        priorities += f'{year.fiscal_year}:\n\n{year.priorities}\n\n'

    deliverables = str()
    for year in project.years.all():
        if year.activities.filter(type=2).exists():
            deliverables += f'{year.fiscal_year}:\n\n'
            i = 1
            for d in year.activities.filter(type=2):
                deliverables += f'{i}) {d.name.upper()} - {d.description}\n\n'
                i += 1

    field_dict = dict(
        TAG_TITLE=project.title,
        TAG_ORG_NAME=project.organization.tname if project.organization else "MISSING!",
        TAG_ADDRESS=project.organization.address if project.organization else "MISSING!",
        TAG_CITY=project.organization.city if project.organization else "MISSING!",
        TAG_PROV=str(project.organization.location.tname) if project.organization else "MISSING!",
        TAG_POSTAL_CODE=project.organization.postal_code if project.organization else "MISSING!",
        TAG_SPECIES=project.species_involved if project.organization else "MISSING!",
        TAG_LEAD_NAME=lead.get_full_name() if lead else "MISSING!",
        TAG_LEAD_NUMBER=lead.profile.phone if lead else "MISSING!",
        TAG_LEAD_EMAIL=lead.email if lead else "MISSING!",
        TAG_LEAD_POSITION=lead.profile.tposition if lead else "MISSING!",
        TAG_LEAD_CONTACT_INFO=contact_info if contact_info else "MISSING!",
        TAG_SECTION_HEAD_NAME=project.section.head.get_full_name() if project.section else "MISSING!",
        TAG_DIVISION_MANAGER_NAME=project.section.division.head.get_full_name() if project.section else "MISSING!",
        TAG_START_YEAR=project.years.first().start_date.strftime("%d/%m/%Y") if project.years.exists() else "MISSING!",
        TAG_END_YEAR=project.years.last().end_date.strftime("%d/%m/%Y") if project.years.exists() and project.years.last().end_date else "MISSING!",
        TAG_TEAM_DESCRIPTION=project.team_description,
        TAG_RATIONALE=project.rationale,
        TAG_OVERVIEW=project.overview,
        TAG_PRIORITIES=priorities,
        TAG_EXPERIMENTAL_PROTOCOL=project.experimental_protocol,
        TAG_DELIVERABLES=deliverables
    )

    for item in field_dict:
        # replace the tagged placeholders in tables
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if item in paragraph.text:
                            try:
                                paragraph.text = paragraph.text.replace(item, field_dict[item])
                            except:
                                paragraph.text = "MISSING!"

        # replace the tagged placeholders in paragraphs
        for paragraph in document.paragraphs:
            if item in paragraph.text:
                try:
                    paragraph.text = paragraph.text.replace(item, field_dict[item])
                except:
                    paragraph.text = "MISSING!"

    # Find and populate the milestones and risk analysis table
    for table in document.tables:
        if "date/period" in table.rows[0].cells[0].paragraphs[0].text.lower():
            for milestone in models.Activity.objects.filter(type=1, project_year__project=project).order_by("target_date"):
                row = table.add_row()
                row.cells[0].paragraphs[0].text = milestone.target_date.strftime("%Y-%m-%d") if milestone.target_date else "MISSING!"
                row.cells[1].paragraphs[0].text = f"{milestone.name.upper()} - {milestone.description}"
                row.cells[2].paragraphs[0].text = milestone.responsible_party if milestone.responsible_party else "MISSING!"

        if "project risk analysis" in table.rows[0].cells[0].paragraphs[0].text.lower():
            for activity in models.Activity.objects.filter(project_year__project=project).order_by("target_date"):
                row = table.add_row()
                row.cells[0].paragraphs[0].text = f"{activity.name} ({activity.get_type_display()})"
                row.cells[1].paragraphs[0].text = activity.risk_description if activity.risk_description else "MISSING!"
                row.cells[2].paragraphs[0].text = f"{activity.likelihood}" if activity.likelihood else "MISSING!"
                row.cells[3].paragraphs[0].text = f"{activity.impact}" if activity.impact else "MISSING!"
                row.cells[4].paragraphs[0].text = activity.get_risk_rating_display() if activity.risk_rating else "MISSING!"
                row.cells[5].paragraphs[0].text = activity.mitigation_measures if activity.mitigation_measures else "MISSING!"
                row.cells[6].paragraphs[0].text = activity.responsible_party if activity.mitigation_measures else "MISSING!"

    document.save(target_file_path)

    return target_url


def generate_acrdp_budget(project):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
    target_file = "temp_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)

    template_file_path = os.path.join(settings.BASE_DIR, 'projects2', 'static', "projects2", "acrdp_template.xlsx")

    om_category_2_cell = {
        # 1	Field Travel	Voyage sur le terrain(Travel)
        1: "24",
        # 2	DFO Business Travel (meeting etc.)	Voyage d'affaires du MPO (réunion, etc.) (Travel)
        2: "25",
        # 3	Training, domestic conferences	Formation, conférences domestiques (Travel)
        3: "26",
        # 4	Other Autre(Travel)
        4: "27",
        # 5	IM/IT - computers, hardware, software	GI / TI - ordinateurs, matériel informatique, logiciels (Equipment Purchase)
        5: "13",
        # 6	Lab Equipment	Équipement de laboratoire (Equipment Purchase)
        6: "14",
        # 7	Field Equipment	Équipement de terrain (Equipment Purchase)
        7: "15",
        # 8	Other	Autre (Equipment Purchase)
        8: "16",
        # 9	Office	Bureau (Material and Supplies)
        9: "21",
        # 10	Lab	Laboratoire (Material and Supplies)
        10: "19",
        # 11	Field	Terrain (Material and Supplies)
        11: "20",
        # 12	Other	Autre (Material and Supplies)
        12: "21",
        # 13	Students (FSWEP, Coop etc.)	Etudiants (PFETE, Coop, etc.) (Human Resources)
        13: "10",
        # 14	Post-Doctoral Candidates	Candidats postdoctoraux (Human Resources)
        14: "10",
        # 15	Contracts	Les contrats (Contracts, Leases, Services)
        15: "33",
        # 16	Translation	Traduction (Contracts, Leases, Services)
        16: "30",
        # 17	Publication costs	Frais de publication (Contracts, Leases, Services)
        17: "30",
        # 18	Vessels, Boats	Navires, Bateaux (Contracts, Leases, Services)
        18: "31",
        # 19	Facilities	Installations (Contracts, Leases, Services)
        19: "32",
        # 20	Other	Autre (Contracts, Leases, Services)
        20: "33",
        # 21	Fuel (e.g., boats)	Carburant (par exemple, bateaux) (Material and Supplies)
        21: "20",
        # 22	International travel for meetings, science collaboration and conferences	Voyages internationaux pour réunions, collaboration scientifique et conférences (Travel)
        22: "25",
        # 23	Equipment Maintenance	L'entretien de l'équipement (Other)
        23: "33",
    }

    capital_category_2_cell = {
        # 1, _("IM / IT - computers, hardware")),
        1: "13",
        # 2, _("Lab Equipment")),
        2: "14",
        # 3, _("Field Equipment")),
        3: "15",
        # 4, _("Other")),
        4: "16",
    }

    wb = load_workbook(filename=template_file_path)
    for year in project.years.all():
        try:
            ws = wb[str(year.fiscal_year)]
        except KeyError:
            print(str(year.fiscal_year), "is not a valid name of a worksheet")
        else:
            for cost in year.omcost_set.filter(funding_source__name__icontains="acrdp"):
                ref_cell = om_category_2_cell.get(cost.om_category_id)
                if ref_cell:
                    amount = ws['H' + ref_cell].value
                    description = ws['K' + ref_cell].value
                    ws['H' + ref_cell].value = nz(amount, 0) + nz(cost.amount, 0)
                    if not description:
                        ws['K' + ref_cell].value = cost.description
                    else:
                        ws['K' + ref_cell].value += "; " + cost.description

            for cost in year.capitalcost_set.filter(funding_source__name__icontains="acrdp"):
                ref_cell = capital_category_2_cell.get(cost.category)
                if ref_cell:
                    amount = ws['H' + ref_cell].value
                    description = ws['K' + ref_cell].value
                    ws['H' + ref_cell].value = nz(amount, 0) + nz(cost.amount, 0)
                    if not description:
                        ws['K' + ref_cell].value = cost.description
                    else:
                        ws['K' + ref_cell].value += "; " + cost.description

            for staff in year.staff_set.filter(funding_source__name__icontains="acrdp"):

                # determine the ref_cell
                if "student" in staff.employee_type.name.lower() or "post-doc" in staff.employee_type.name.lower() or staff.student_program:
                    ref_cell = 10
                elif not staff.level:
                    ref_cell = 7  # if we have no information about the level, we cannot choose a cell. Let's default to scientist
                elif "bi" in staff.level.name.lower():
                    ref_cell = 8  # if we have no information about the level, we cannot choose a cell. Let's default to scientist
                elif "eg" in staff.level.name.lower():
                    ref_cell = 9  # if we have no information about the level, we cannot choose a cell. Let's default to scientist
                elif "pc" in staff.level.name.lower() or "res" in staff.level.name.lower():
                    ref_cell = 7  # if we have no information about the level, we cannot choose a cell. Let's default to scientist
                else:
                    ref_cell = 7  # if we didn't catch it above, just through into the scientist bin again...
                ref_cell = str(ref_cell)
                # first need to determine if this is inkind or not:
                inkind = False
                if staff.amount == 0:  # in-kind
                    inkind = True

                amount = ws["H" + ref_cell].value
                description = ws["K" + ref_cell].value

                staff_description = staff.smart_name
                if staff.level: staff_description += f" ({staff.level})"
                if staff.duration_weeks: staff_description += f" @ {staff.duration_weeks} weeks"
                if inkind: staff_description += f" (in-kind)"

                ws["H" + ref_cell].value = nz(amount, 0) + nz(staff.amount, 0)
                if not description:
                    ws['K' + ref_cell].value = staff_description
                else:
                    ws['K' + ref_cell].value += "; " + staff_description

    wb.save(target_file_path)

    return target_url

#
#
# class StdReport:
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
#     target_file = "temp_export.xlsx"
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)
#
#     formats = {
#         "section_header": {
#             'bold': True,
#             'border': 1,
#             'border_color': 'black',
#             "align": 'center',
#             "valign": 'top',
#             "text_wrap": True
#         },
#         "col_header": {
#             'bold': True,
#             'border': 1,
#             'border_color': 'black',
#             'bg_color': '#a6a6a6',
#             "align": 'center',
#             "text_wrap": True
#         },
#         "normal_text": {
#             "valign": 'top',
#             "align": 'left',
#             "text_wrap": True,
#             "border": 0,
#             "border_color": 'black',
#         },
#         "date_format": {
#             'num_format': "yy-mm-dd",
#             'align': 'left',
#         }
#     }
#
#     wb_format = {}
#
#     __workbook__ = None
#
#     __sheets__ = []
#
#     report_sections = "None"
#     report_divisions = "None"
#     report_regions = "None"
#     report_fiscal_year = "None"
#
#     def __init__(self, regions="None", divisions="None", sections="None", fiscal_year="None"):
#         self.report_regions = regions
#         self.report_divisions = divisions
#         self.report_sections = sections
#         self.report_fiscal_year = fiscal_year
#
#     def get_section_list(self):
#         # need to assemble a section list
#         #  first look at the sections arg; if not null, we don't need anything else
#         if self.report_sections != "None":
#             section_list = shared_models.Section.objects.filter(id__in=self.report_sections.split(","))
#         #  next look at the divisions arg; if not null, we don't need anything else
#         elif self.report_divisions != "None":
#             section_list = shared_models.Section.objects.filter(division_id__in=self.report_divisions.split(","))
#         #  next look at the divisions arg; if not null, we don't need anything else
#         elif self.report_regions != "None":
#             section_list = shared_models.Section.objects.filter(
#                 division__branch__region_id__in=self.report_regions.split(","))
#         else:
#             section_list = shared_models.Section.objects.all()
#
#         return section_list
#
#     def get_workbook(self) -> xlsxwriter.Workbook:
#         if not self.__workbook__:
#             self.__workbook__ = xlsxwriter.Workbook(self.target_file_path, {'remove_timezone': True})
#
#         return self.__workbook__
#
#     def get_worksheet(self, title="Sheet1") -> xlsxwriter.Workbook.worksheet_class:
#         sheet = self.get_workbook().get_worksheet_by_name(title)
#         if not sheet:
#             sheet = self.get_workbook().add_worksheet(name=title)
#
#             sheets = [s['title'] for s in self.__sheets__]
#             if title not in sheets:
#                 self.__sheets__.append({"title": title})
#
#         return sheet
#
#     def get_format(self, format_name):
#         # For some reason sometimes StdReport keeps a reference to wb_format, so it might remember a format, but
#         # that format isn't in the workbooks formats
#         if format_name not in self.wb_format or self.wb_format[format_name] not in self.get_workbook().formats:
#             self.wb_format[format_name] = self.get_workbook().add_format(self.formats[format_name])
#
#         return self.wb_format[format_name]
#
#     def create_headers(self):
#
#         sec_head = self.get_format("section_header")
#         col_head = self.get_format("col_header")
#         nor_text = self.get_format("normal_text")
#
#         for i in range(0, len(self.__sheets__)):
#             sh = self.__sheets__[i]
#             sheet = self.get_worksheet(title=sh['title'])
#
#             running_col_idx = 0
#             for i in range(0, len(sh['sub'])):
#                 sec = sh['sub'][i]
#                 subsec = sec['sub'] if 'sub' in sec else None
#
#                 if subsec:
#                     for s in subsec:
#                         sheet.set_column(running_col_idx, running_col_idx,
#                                          (s['width'] if 'width' in s else 20),
#                                          (self.get_format(s["format"]) if "format" in s else nor_text)
#                                          )
#
#                     if len(subsec) > 1:
#                         sheet.merge_range(0, running_col_idx, 0, running_col_idx + (len(subsec) - 1), sec['title'],
#                                           sec_head)
#                     else:
#                         sheet.write_row(0, running_col_idx, [sec['title']], sec_head)
#
#                     subsec_array = [s["title"] for s in subsec]
#                     sheet.write_row(1, running_col_idx, subsec_array, col_head)
#
#                 else:
#                     sheet.set_column(running_col_idx, running_col_idx,
#                                      (sec['width'] if 'width' in sec else 20),
#                                      (self.get_format(sec["format"]) if "format" in sec else nor_text)
#                                      )
#                     # if the section has no sub-sections, merge it with the column heading row
#                     sheet.merge_range(0, running_col_idx, 1, running_col_idx, sec['title'], sec_head)
#
#                 running_col_idx += len(subsec) if subsec else 1
#
#     def add_section(self, section, worksheet='Sheet1'):
#         # create the worksheet if it doesn't exist and make sure it's added to the __sheets__ array
#         sheet = self.get_worksheet(title=worksheet)
#
#         sheet_meta = self.__sheets__[self.get_workbook().worksheets().index(sheet)]
#         if 'sub' not in sheet_meta:
#             sheet_meta['sub'] = list()
#
#         sheet_meta['sub'].append(section)
#
#
# class CovidReport(StdReport):
#
#     __sections__ = [
#         {
#             "title": "Original Project Information",
#             "sub": [
#                 {
#                     "title": "Project/Activity title",
#                     "width": 50
#                 },
#                 {
#                     "title": "Project ID",
#                 },
#                 {
#                     "title": "Division",
#                 },
#                 {
#                     "title": "Section",
#                 },
#                 {
#                     "title": "Activity Type",
#                 },
#                 {
#                     "title": "# of DFO staff involved",
#                 },
#                 {
#                     "title": "# of non-DFO staff involved",
#                 },
#                 {
#                     "title": "Location(s) of activity",
#                 },
#                 {
#                     "title": "Original start date",
#                     "format": "date_format"
#                 },
#                 {
#                     "title": "Original end date",
#                     "format": "date_format"
#                 },
#             ]
#         },
#         {
#             "title": "Recommendation",
#             "sub": [
#                 {
#                     "title": "COVID Recommendation",
#                 },
#                 {
#                     "title": "Drop dead start date",
#                 },
#                 {
#                     "title": "Rationale",
#                 },
#             ]
#         },
#         {
#             "title": "Analysis",
#             "sub": [
#                 {
#                     "title": "Critical Service?",
#                 },
#                 {
#                     "title": "Able to maintain social distance?",
#                 },
#                 {
#                     "title": "Staffing?",
#                 },
#                 {
#                     "title": "Travel?",
#                 },
#                 {
#                     "title": "External services?",
#                 },
#                 {
#                     "title": "Timing",
#                 },
#             ]
#         },
#         {
#             "title": "Impact",
#             "sub": [
#                 {
#                     "title": "Impact of Ministerial Advice",
#                 },
#                 {
#                     "title": "Impact on Departmental Deliverables",
#                 },
#                 {
#                     "title": "Impact on Operations",
#                 },
#             ]
#         },
#         {
#             "title": "Mitigation",
#             "sub": [
#                 {
#                     "title": "Other measures to reduce risk",
#                 },
#             ]
#         }
#     ]
#
#     __sheets__ = [
#         {
#             "title": "COVID Assessment",
#             "sub": __sections__
#         }
#     ]
#
#     def generate_spread_sheet(self):
#         self.create_headers()
#
#         # start on row 2 because sections is row 0, subsections is row 1
#         row = 2
#         sheet = self.get_worksheet(title=self.__sheets__[0]["title"])
#         row_format = list()
#         for s in self.__sections__:
#             if "sub" in s:
#                 for c in s["sub"]:
#                     if "width" in c:
#                         col_idx = len(row_format)
#                         sheet.set_column(col_idx, col_idx, width=c["width"])
#                     row_format.append(self.get_format(c["format"] if "format" in c else "normal_text"))
#             else:
#                 if "width" in s:
#                     col_idx = len(row_format)
#                     sheet.set_column(col_idx, col_idx, width=c["width"])
#                 row_format.append(self.get_format(s["format"] if "format" in s else "normal_text"))
#
#         section_list = self.get_section_list()
#
#         project_list = models.Project.objects.all()
#
#         if section_list:
#             project_list = project_list.filter(section__in=section_list)
#
#         if self.report_fiscal_year != "None":
#             project_list = project_list.filter(year=self.report_fiscal_year)
#
#         for project in project_list:
#
#             staff = project.staff_members.all()
#             dfo_staff = staff.filter(employee_type__cost_type=1)
#             non_dfo_staff = staff.filter(employee_type__cost_type=2)
#
#             travel = "yes" if project.om_costs.filter(om_category__group=1, budget_requested__gt=0) else "No"
#
#             sheet.write(row, 0, project.project_title, row_format[0])
#             sheet.write(row, 1, project.pk, row_format[1])
#             sheet.write(row, 2, project.section.division.tname, row_format[2])
#             sheet.write(row, 3, project.section.tname, row_format[3])
#             sheet.write(row, 4, project.activity_type.name if project.activity_type else "", row_format[4])
#             sheet.write(row, 5, dfo_staff.count(), row_format[5])
#             sheet.write(row, 6, non_dfo_staff.count(), row_format[6])
#
#             sheet.write(row, 8, project.start_date.strftime("%Y-%m-%d") if project.start_date else "", row_format[8])
#             sheet.write(row, 9, project.end_date.strftime("%Y-%m-%d") if project.end_date else "", row_format[9])
#
#             sheet.write(row, 16, travel, row_format[16])
#             row += 1
#
#         self.get_workbook().close()
#
#
# def generate_funding_spreadsheet(fiscal_year, funding, regions, divisions, sections, omcatagory=None):
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
#     target_file = "temp_export.xlsx"
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#
#     # create formatting
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#9ae0f5', "align": 'normal',
#          "text_wrap": True})
#     normal_format = workbook.add_format({"valign": 'top', "align": 'left', "text_wrap": True, 'border': 1,
#                                          'border_color': 'black', })
#
#     number_format = workbook.add_format({"valign": 'top', "align": 'left', 'border': 1,
#                                          'border_color': 'black', })
#     number_format.set_num_format(8)
#
#     # need to assemble a section list
#     #  first look at the sections arg; if not null, we don't need anything else
#     if sections != "None":
#         section_list = shared_models.Section.objects.filter(id__in=sections.split(","))
#     #  next look at the divisions arg; if not null, we don't need anything else
#     elif divisions != "None":
#         section_list = shared_models.Section.objects.filter(division_id__in=divisions.split(","))
#     #  next look at the divisions arg; if not null, we don't need anything else
#     elif regions != "None":
#         section_list = shared_models.Section.objects.filter(division__branch__region_id__in=regions.split(","))
#     else:
#         section_list = shared_models.Section.objects.all()
#
#     project_list = models.Project.objects.filter(year=fiscal_year, section__in=section_list)
#
#     if omcatagory and omcatagory != "None":
#         # get a list of OM Categories matching what the user selected in the web form
#         om_list = models.OMCategory.objects.filter(pk__in=omcatagory.split(','))
#
#         # Use the OMCost table to get a list of projects that have one of the categories assiged to it
#         om_costs_projects = [omc.project.pk for omc in models.OMCost.objects.filter(om_category__in=om_list,
#                                                                                     budget_requested__gt=0)]
#
#         # filter down the list of projects to projects in both the project list and in the OMCost list
#         project_list = project_list.filter(pk__in=om_costs_projects)
#
#         header = {"Project ID": [normal_format, 20], "Project Title": [normal_format, 20],
#                   "Project Leads": [normal_format, 20], "O&M Cost": [number_format, 20]}
#         # Use the header key as the col label, then use the array[0] for the col format and array[1] for col size
#         for om in om_list:
#             header[om.name] = [number_format, 20]
#         header["Project Objectives & Description"] = [normal_format, 150]
#
#         worksheet1 = workbook.add_worksheet(name="Submitted Projects")
#         write_funding_omcategory_sheet(worksheet1, header_format, header, project_list.filter(approved=False), om_list)
#
#         worksheet2 = workbook.add_worksheet(name="Approved Projects")
#         write_funding_omcategory_sheet(worksheet2, header_format, header, project_list.filter(approved=True), om_list)
#         workbook.close()
#     else:
#
#         # We're only using B-Base funding
#         # funding_type = models.FundingSourceType.objects.get(pk=funding)
#         # funding_src = models.FundingSource.objects.filter(name="SARA", funding_source_type=funding_type)
#         funding_src = models.FundingSource.objects.get(pk=funding)
#
#         project_list = project_list.filter(default_funding_source=funding_src)
#
#         # Use the header key as the col label, then use the array[0] for the col format and array[1] for col size
#         header = {
#             "Project ID": [normal_format, 20],
#             "Project Title": [normal_format, 20],
#             "Salary": [number_format, 20],
#             "O&M Cost": [number_format, 20],
#             "Capital Cost": [number_format, 20],
#             "Project Staff": [normal_format, 20],
#             "Start Date of Project": [normal_format, 20],
#             "End Date of Project": [normal_format, 20],
#             "Project-Specific Priorities": [normal_format, 150],
#             "Project Objectives & Description": [normal_format, 150],
#             "Project Deliverables / Activities": [normal_format, 150],
#             "Activities": [normal_format, 150],
#             "Additional Notes": [normal_format, 150],
#         }
#
#         worksheet1 = workbook.add_worksheet(name="Submitted Projects")
#         write_funding_sheet(worksheet1, header_format, header, project_list.filter(approved=False), funding_src)
#
#         worksheet2 = workbook.add_worksheet(name="Approved Projects")
#         write_funding_sheet(worksheet2, header_format, header, project_list.filter(approved=True), funding_src)
#
#         workbook.close()
#
#     return target_url
#
#
# def write_funding_header(worksheet, header_format, header):
#     keys = [k for k in header.keys()]
#     worksheet.write_row(0, 0, keys, header_format)
#
#     for i in range(0, len(keys)):
#         worksheet.set_column(i, i, header[keys[i]][1], header[keys[i]][0])
#
#
# # used to generate a common sheet format
# def write_funding_omcategory_sheet(worksheet, header_format, header, projects, om_list):
#     write_funding_header(worksheet=worksheet, header_format=header_format, header=header)
#
#     row = 1
#     for project in projects2:
#
#         prj_desc = html2text.html2text(project.description) if project.description else None
#
#         staff_leads = project.project_leads
#
#         om_cost = project.om_costs.aggregate(Sum("budget_requested"))
#
#         data = [
#             project.id,
#             project.project_title,
#             staff_leads,
#             nz(om_cost['budget_requested__sum'], 0),
#         ]
#         for om in om_list:
#             cost = {'budget_requested__sum': 0}
#             if project.om_costs.all().filter(om_category=om):
#                 cost = project.om_costs.all().filter(om_category=om).aggregate(Sum("budget_requested"))
#             data.append(nz(cost['budget_requested__sum'], 0))
#
#         data.append(
#             prj_desc.replace("\n\n", "[_EOL_]").replace("\n", " ").replace("[_EOL_]", "\n\n") if prj_desc else "")
#
#         worksheet.write_row(row, 0, data)
#
#         row += 1
#
#
# # used to generate a common sheet format
# def write_funding_sheet(worksheet, header_format, header, projects, funding):
#     write_funding_header(worksheet=worksheet, header_format=header_format, header=header)
#
#     row = 1
#     for project in projects2:
#         om_cost = project.om_costs.filter(funding_source=funding).aggregate(Sum("budget_requested"))
#
#         staff_list = project.staff_members.all()
#
#         staff_names = listrify([(staff.user if staff.user else staff.name) for staff in staff_list])
#         staff_cost = staff_list.filter(funding_source=funding).aggregate(Sum('cost'))
#
#         capital_cost = project.capital_costs.filter(funding_source=funding).aggregate(Sum("budget_requested"))
#
#         activity = listrify([m.name + ": " + m.description for m in project.activities.all()], "\n\n*")
#
#         data = [
#             project.id,
#             project.project_title,
#             nz(staff_cost['cost__sum'], 0),
#             nz(om_cost['budget_requested__sum'], 0),
#             nz(capital_cost['budget_requested__sum'], 0),
#             staff_names,
#             project.start_date.strftime('%Y-%m-%d') if project.start_date else "---",
#             project.end_date.strftime('%Y-%m-%d') if project.end_date else "---",
#             html2text.html2text(project.priorities).replace("\n\n", "[_EOL_]").replace("\n", " ").replace("[_EOL_]",
#                                                                                                           "\n\n"),
#             html2text.html2text(project.description).replace("\n\n", "[_EOL_]").replace("\n", " ").replace("[_EOL_]",
#                                                                                                            "\n\n"),
#             html2text.html2text(project.deliverables).replace("\n\n", "[_EOL_]").replace("\n", " ").replace("[_EOL_]",
#                                                                                                             "\n\n"),
#             activity,
#             project.notes]
#         worksheet.write_row(row, 0, data)
#
#         row += 1
#
#
# def generate_dougs_spreadsheet(fiscal_year, regions, divisions, sections):
#     # Upson, P - used by those weird Maritimes people because they have to be different <insert eye roll>
#     mar_id = shared_models.Region.objects.get(name="Maritimes").pk
#
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
#     target_file = "temp_export.xlsx"
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#     worksheet1 = workbook.add_worksheet(name="Programs by section")
#     worksheet2 = workbook.add_worksheet(name="Core projects by section")
#     worksheet3 = workbook.add_worksheet(name="Flex projects by section")
#     worksheet4 = workbook.add_worksheet(name="No-Gos")
#     # worksheet3 = workbook.add_worksheet(name="Unapproved projects")
#
#     # create formatting
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#9ae0f5', "align": 'normal',
#          "text_wrap": True})
#     header_format_centered = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#9ae0f5', "align": 'center',
#          "text_wrap": True})
#     divider_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#d1dfe3', "align": 'left', "text_wrap": False,
#          'italic': True,
#          'num_format': '#,##0'})
#     normal_num_format = workbook.add_format(
#         {"align": 'left', "text_wrap": True, 'border': 1, 'border_color': 'black', 'num_format': '#,##0'})
#     normal_format = workbook.add_format({"align": 'left', "text_wrap": True, 'border': 1, 'border_color': 'black', })
#     summary_right_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#d1dfe3', "align": 'right', 'italic': True,
#          'num_format': '#,##0', "text_wrap": False, })
#     summary_left_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#d1dfe3', "align": 'left', 'italic': True,
#          'num_format': '#,##0', "text_wrap": False, })
#     bold_format_lg = workbook.add_format({"align": 'left', 'bold': True, 'font_size': 16})
#     bold_format = workbook.add_format({"align": 'left', 'bold': True, 'font_size': 14})
#
#     # need to assemble a section list
#     ## first look at the sections arg; if not null, we don't need anything else
#     if sections != "None":
#         section_list = shared_models.Section.objects.filter(id__in=sections.split(","))
#     ## next look at the divisions arg; if not null, we don't need anything else
#     elif divisions != "None":
#         section_list = shared_models.Section.objects.filter(division_id__in=divisions.split(","))
#     ## next look at the divisions arg; if not null, we don't need anything else
#     elif regions != "None":
#         section_list = shared_models.Section.objects.filter(division__branch__region_id__in=regions.split(","))
#     else:
#         section_list = shared_models.Section.objects.all()
#
#     # 1) spreadsheet: Programs by section #
#     #############################
#     # This is too complicated a worksheet. let's create column widths manually
#     col_max = [30, 30, 50, 8, 10, 30, 10, 10, 10]
#     col_max.extend(repeat("10,", 12)[:-1].split(","))
#     for j in range(0, len(col_max)):
#         worksheet1.set_column(j, j, width=int(col_max[j]))
#
#     worksheet1.write_row(0, 0, [
#         "SCIENCE BRANCH WORKPLANNING - SUMMARY OF PROGRAMS BY SECTION (Projects Submitted and Approved by Section Heads)", ],
#                          bold_format_lg)
#     worksheet1.write_row(1, 0, [timezone.now().strftime('%Y-%m-%d'), ], bold_format)
#     # worksheet1.merge_range('j3:l3'.upper(), 'A-Base', header_format_centered)
#     # worksheet1.merge_range('m3:o3'.upper(), 'B-Base', header_format_centered)
#     # worksheet1.merge_range('p3:r3'.upper(), 'C-Base', header_format_centered)
#     # worksheet1.merge_range('s3:u3'.upper(), 'Total', header_format_centered)
#
#     header = [
#         "Division",
#         "Section",
#         "Program",
#         "Core / flex",
#         "Tagged projects",
#         "Project leads",
#         "Contains projects with more than one program?",
#         'Total FTE\n(weeks)',
#         'Total OT\n(hours)',
#     ]
#     # financial_headers = [
#     #     'Salary\n(in excess of FTE)',
#     #     'O & M\n(including staff)',
#     #     'Capital',
#     # ]
#     # header.extend(financial_headers)
#     # header.extend(financial_headers)
#     # header.extend(financial_headers)
#     # header.extend(financial_headers)
#
#     # create the col_max column to store the length of each header
#     # should be a maximum column width to 100
#
#     worksheet1.write_row(3, 0, header, header_format)
#
#     i = 4
#     for s in section_list.order_by("division", "name"):
#         # get a list of projects..
#
#         if regions == str(mar_id):
#             project_list = s.projects.filter(year=fiscal_year, submitted=True)
#         else:
#             project_list = s.projects.filter(year=fiscal_year, submitted=True, section_head_approved=True)
#
#         # get a list of programs..
#         program_id_list = []
#         for p in project_list:
#             if p.programs.count() > 0:
#                 program_id_list.extend([program.id for program in p.programs.all()])
#         program_list = models.Program2.objects.filter(id__in=program_id_list).order_by("-is_core")
#         for program in program_list:
#             project_count = listrify([p.id for p in project_list.filter(programs=program)])
#             leads = listrify(
#                 list(set([str(staff.user) for staff in
#                           models.Staff.objects.filter(project__in=project_list.filter(programs=program), lead=True) if
#                           staff.user])))
#             is_double_count = len(
#                 [project for project in project_list.filter(programs=program).all() if
#                  project.programs.count() > 1]) > 0
#
#             total_fte = models.Staff.objects.filter(
#                 project__in=project_list.filter(programs=program)
#             ).order_by("duration_weeks").aggregate(dsum=Sum("duration_weeks"))['dsum']
#             total_ot = models.Staff.objects.filter(
#                 project__in=project_list.filter(programs=program)
#             ).order_by("overtime_hours").aggregate(dsum=Sum("overtime_hours"))['dsum']
#
#             data_row = [
#                 s.division.name,
#                 s.name,
#                 program.short_name,
#                 program.get_is_core_display(),
#                 project_count,
#                 leads,
#                 yesno(is_double_count),
#                 zero2val(total_fte, None),
#                 zero2val(total_ot, None),
#             ]
#             # total_salary = 0
#             # total_om = 0
#             # total_capital = 0
#             # for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#             #     staff_salary = models.Staff.objects.filter(project__in=project_list.filter(programs=program)).filter(
#             #         employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#             #     ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             #     staff_om = models.Staff.objects.filter(project__in=project_list.filter(programs=program)).filter(
#             #         employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#             #     ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             #
#             #     other_om = models.OMCost.objects.filter(
#             #         project__in=project_list.filter(programs=program), funding_source=source
#             #     ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#             #
#             #     capital = models.CapitalCost.objects.filter(
#             #         project__in=project_list.filter(programs=program), funding_source=source
#             #     ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#             #
#             #     total_salary += nz(staff_salary, 0)
#             #     total_om += nz(staff_om, 0) + nz(other_om, 0)
#             #     total_capital += nz(capital, 0)
#             #
#             #     data_row.extend([
#             #         zero2val(nz(staff_salary, 0), '--'),
#             #         zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#             #         zero2val(nz(capital, 0), '--'),
#             #     ])
#             # data_row.extend([
#             #     zero2val(total_salary, '--'),
#             #     zero2val(total_om, '--'),
#             #     zero2val(total_capital, '--'),
#             # ])
#
#             j = 0
#
#             worksheet1.write_row(i, 0, data_row, normal_format)
#             i += 1
#         # if there are no projects, don't add a line!
#         if project_list.count() > 0:
#             worksheet1.write_row(i, 0, repeat(" ,", len(header) - 1).split(","), divider_format)
#             i += 1
#
#     worksheet1.conditional_format(4, 9, i, 20, {
#         'type': 'cell',
#         'criteria': 'greater than',
#         'value': 0,
#         'format': normal_num_format,
#     })
#
#     # 2) spreadsheet: Core Projects by section #
#     #############################
#     # This is too complicated a worksheet. let's create column widths manually
#     division_list = []
#     col_max = [30, 30, 8, 35, 15, 8, 40, 20, 10, 10]
#     col_max.extend(repeat("10,", 12)[:-1].split(","))
#     for j in range(0, len(col_max)):
#         worksheet2.set_column(j, j, width=int(col_max[j]))
#
#     worksheet2.write_row(0, 0, [
#         "SCIENCE BRANCH WORKPLANNING - SUMMARY OF CORE PROJECTS BY SECTION (Projects Submitted and Approved by Section Heads)", ],
#                          bold_format_lg)
#     worksheet2.write_row(1, 0, [timezone.now().strftime('%Y-%m-%d'), ], bold_format)
#     worksheet2.merge_range('k3:m3'.upper(), 'A-Base', header_format_centered)
#     worksheet2.merge_range('n3:p3'.upper(), 'B-Base', header_format_centered)
#     worksheet2.merge_range('q3:s3'.upper(), 'C-Base', header_format_centered)
#     worksheet2.merge_range('t3:v3'.upper(), 'Total', header_format_centered)
#
#     header = [
#         "Division",
#         "Section",
#         "Core / flex",
#         verbose_field_name(models.Project.objects.first(), 'programs'),
#         verbose_field_name(models.Project.objects.first(), 'tags'),
#         "Project ID",
#         verbose_field_name(models.Project.objects.first(), 'project_title'),
#         "Project leads",
#         'Total FTE\n(weeks)',
#         'Total OT\n(hours)',
#     ]
#
#     financial_headers = [
#         'Salary\n(in excess of FTE)',
#         'O & M\n(including staff)',
#         'Capital',
#     ]
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#
#     worksheet2.write_row(3, 0, header, header_format)
#     i = 4
#     for s in section_list.order_by("division", "name"):
#         # get a list of projects..
#         project_list = s.projects.filter(year=fiscal_year, submitted=True, section_head_approved=True,
#                                          programs__is_core=True).order_by("id")
#         for project in set(project_list):
#             core_flex = "/".join(list(set(([program.get_is_core_display() for program in project.programs.all()]))))
#             leads = listrify(
#                 list(set([str(staff.user) for staff in
#                           models.Staff.objects.filter(project=project, lead=True) if staff.user])))
#             programs = listrify(["{}".format(program.short_name) for program in
#                                  project.programs.all()])
#             tags = listrify([str(tag) for tag in project.tags.all()])
#             total_fte = models.Staff.objects.filter(
#                 project=project).order_by("duration_weeks").aggregate(dsum=Sum("duration_weeks"))['dsum']
#             total_ot = models.Staff.objects.filter(
#                 project=project).order_by("overtime_hours").aggregate(dsum=Sum("overtime_hours"))['dsum']
#
#             data_row = [
#                 s.division.name,
#                 s.name,
#                 core_flex,
#                 programs,
#                 tags,
#                 project.id,
#                 project.project_title,
#                 leads,
#                 zero2val(total_fte, None),
#                 zero2val(total_ot, None),
#             ]
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#
#                 other_om = models.OMCost.objects.filter(project=project, funding_source=source
#                                                         ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))['dsum']
#
#                 capital = models.CapitalCost.objects.filter(project=project, funding_source=source
#                                                             ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))['dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 data_row.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             data_row.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#             worksheet2.write_row(i, 0, data_row, normal_format)
#             i += 1
#         # if there are no projects, don't add a line!
#         if project_list.count() > 0:
#             division_list.append(s.division)
#             section_summary = repeat(" ,", 9).split(",")
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 other_om = models.OMCost.objects.filter(
#                     project__in=project_list, funding_source=source
#                 ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#                 capital = models.CapitalCost.objects.filter(
#                     project__in=project_list, funding_source=source).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))[
#                     'dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 section_summary.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             section_summary.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#             worksheet2.write_row(i, 0, section_summary, divider_format)
#             i += 1
#
#     worksheet2.conditional_format(4, 10, i, 21, {
#         'type': 'cell',
#         'criteria': 'greater than',
#         'value': 0,
#         'format': normal_num_format,
#     })
#
#     i += 1
#     for division in list(set(division_list)):
#         projects = models.Project.objects.filter(section__division=division).filter(
#             year=fiscal_year, submitted=True, section_head_approved=True, programs__is_core=True)
#
#         j = 9
#         # worksheet2.write(i, j, division.name, summary_right_format)
#         worksheet2.merge_range(i, j - 2, i, j, division.name, summary_right_format)
#
#         j += 1
#         total_salary = 0
#         total_om = 0
#         total_capital = 0
#         for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#             staff_salary = models.Staff.objects.filter(project__in=projects).filter(
#                 employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#             ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             staff_om = models.Staff.objects.filter(project__in=projects).filter(
#                 employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#             ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             other_om = models.OMCost.objects.filter(
#                 project__in=projects, funding_source=source
#             ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#             capital = models.CapitalCost.objects.filter(
#                 project__in=projects, funding_source=source).order_by("budget_requested").aggregate(
#                 dsum=Sum("budget_requested"))[
#                 'dsum']
#
#             total_salary += nz(staff_salary, 0)
#             total_om += nz(staff_om, 0) + nz(other_om, 0)
#             total_capital += nz(capital, 0)
#             worksheet2.write(i, j, zero2val(nz(staff_salary, 0), '--'), summary_left_format)
#             j += 1
#             worksheet2.write(i, j, zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'), summary_left_format)
#             j += 1
#             worksheet2.write(i, j, zero2val(nz(capital, 0), '--'), summary_left_format)
#             j += 1
#
#         worksheet2.write(i, j, zero2val(total_salary, '--'), summary_left_format)
#         j += 1
#         worksheet2.write(i, j, zero2val(total_om, '--'), summary_left_format)
#         j += 1
#         worksheet2.write(i, j, zero2val(total_capital, '--'), summary_left_format)
#         i += 1
#
#     # 3) spreadsheet: Flex Projects by section #
#     #############################
#     # This is too complicated a worksheet. let's create column widths manually
#     col_max = [30, 30, 8, 35, 15, 8, 40, 20, 10, 10]
#     col_max.extend(repeat("10,", 12)[:-1].split(","))
#     for j in range(0, len(col_max)):
#         worksheet3.set_column(j, j, width=int(col_max[j]))
#
#     worksheet3.write_row(0, 0, [
#         "SCIENCE BRANCH WORKPLANNING - SUMMARY OF FLEX PROJECTS BY SECTION (Projects Submitted and Approved by Section Heads)", ],
#                          bold_format_lg)
#     worksheet3.write_row(1, 0, [timezone.now().strftime('%Y-%m-%d'), ], bold_format)
#     worksheet3.merge_range('k3:m3'.upper(), 'A-Base', header_format_centered)
#     worksheet3.merge_range('n3:p3'.upper(), 'B-Base', header_format_centered)
#     worksheet3.merge_range('q3:s3'.upper(), 'C-Base', header_format_centered)
#     worksheet3.merge_range('t3:v3'.upper(), 'Total', header_format_centered)
#
#     header = [
#         "Division",
#         "Section",
#         "Core / flex",
#         verbose_field_name(models.Project.objects.first(), 'programs'),
#         verbose_field_name(models.Project.objects.first(), 'tags'),
#         "Project ID",
#         verbose_field_name(models.Project.objects.first(), 'project_title'),
#         "Project leads",
#         'Total FTE\n(weeks)',
#         'Total OT\n(hours)',
#     ]
#
#     financial_headers = [
#         'Salary\n(in excess of FTE)',
#         'O & M\n(including staff)',
#         'Capital',
#     ]
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#
#     worksheet3.write_row(3, 0, header, header_format)
#     i = 4
#     for s in section_list.order_by("division", "name"):
#         # get a list of projects..
#         if regions == str(mar_id):
#             project_list = s.projects.filter(year=fiscal_year, submitted=True, programs__is_core=False).order_by("id")
#         else:
#             project_list = s.projects.filter(year=fiscal_year, submitted=True, section_head_approved=True,
#                                              programs__is_core=False).order_by("id")
#
#         for project in set(project_list):
#             core_flex = "/".join(list(set(([program.get_is_core_display() for program in project.programs.all()]))))
#
#             leads = listrify(
#                 list(set([str(staff.user) for staff in
#                           models.Staff.objects.filter(project=project, lead=True) if staff.user])))
#             programs = listrify(["{}".format(program.short_name) for program in
#                                  project.programs.all()])
#             tags = listrify([str(tag) for tag in project.tags.all()])
#             total_fte = models.Staff.objects.filter(
#                 project=project).order_by("duration_weeks").aggregate(dsum=Sum("duration_weeks"))['dsum']
#             total_ot = models.Staff.objects.filter(
#                 project=project).order_by("overtime_hours").aggregate(dsum=Sum("overtime_hours"))['dsum']
#
#             data_row = [
#                 s.division.name,
#                 s.name,
#                 core_flex,
#                 programs,
#                 tags,
#                 project.id,
#                 project.project_title,
#                 leads,
#                 zero2val(total_fte, None),
#                 zero2val(total_ot, None),
#             ]
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#
#                 other_om = models.OMCost.objects.filter(project=project, funding_source=source
#                                                         ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))['dsum']
#
#                 capital = models.CapitalCost.objects.filter(project=project, funding_source=source
#                                                             ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))[
#                     'dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 data_row.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             data_row.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#
#             j = 0
#
#             worksheet3.write_row(i, 0, data_row, normal_format)
#             i += 1
#         # if there are no projects, don't add a line!
#         if project_list.count() > 0:
#             section_summary = repeat(" ,", 9).split(",")
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 other_om = models.OMCost.objects.filter(
#                     project__in=project_list, funding_source=source
#                 ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#                 capital = models.CapitalCost.objects.filter(
#                     project__in=project_list, funding_source=source).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))[
#                     'dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 section_summary.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             section_summary.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#             worksheet3.write_row(i, 0, section_summary, divider_format)
#             i += 1
#
#     worksheet3.conditional_format(4, 10, i, 21, {
#         'type': 'cell',
#         'criteria': 'greater than',
#         'value': 0,
#         'format': normal_num_format,
#     })
#
#     i += 1
#     for division in list(set(division_list)):
#
#         if regions == str(mar_id):
#             project_list = models.Project.objects.filter(section__division=division).filter(year=fiscal_year,
#                                                                                             submitted=True,
#                                                                                             programs__is_core=False)
#         else:
#             project_list = models.Project.objects.filter(section__division=division).filter(year=fiscal_year,
#                                                                                             submitted=True,
#                                                                                             section_head_approved=True,
#                                                                                             programs__is_core=False)
#
#         j = 9
#         # worksheet2.write(i, j, division.name, summary_right_format)
#         worksheet3.merge_range(i, j - 2, i, j, division.name, summary_right_format)
#
#         j += 1
#         total_salary = 0
#         total_om = 0
#         total_capital = 0
#         for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#             staff_salary = models.Staff.objects.filter(project__in=project_list).filter(
#                 employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#             ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             staff_om = models.Staff.objects.filter(project__in=project_list).filter(
#                 employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#             ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#             other_om = models.OMCost.objects.filter(
#                 project__in=project_list, funding_source=source
#             ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#             capital = models.CapitalCost.objects.filter(
#                 project__in=project_list, funding_source=source).order_by("budget_requested").aggregate(
#                 dsum=Sum("budget_requested"))[
#                 'dsum']
#
#             total_salary += nz(staff_salary, 0)
#             total_om += nz(staff_om, 0) + nz(other_om, 0)
#             total_capital += nz(capital, 0)
#             worksheet3.write(i, j, zero2val(nz(staff_salary, 0), '--'), summary_left_format)
#             j += 1
#             worksheet3.write(i, j, zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'), summary_left_format)
#             j += 1
#             worksheet3.write(i, j, zero2val(nz(capital, 0), '--'), summary_left_format)
#             j += 1
#
#         worksheet3.write(i, j, zero2val(total_salary, '--'), summary_left_format)
#         j += 1
#         worksheet3.write(i, j, zero2val(total_om, '--'), summary_left_format)
#         j += 1
#         worksheet3.write(i, j, zero2val(total_capital, '--'), summary_left_format)
#         i += 1
#
#     # 4) spreadsheet: No Gos#
#     #############################
#     # This is too complicated a worksheet. let's create column widths manually
#     col_max = [30, 30, 8, 35, 15, 8, 40, 20, 10, 10, 20, 10, 10]
#     col_max.extend(repeat("10,", 12)[:-1].split(","))
#     for j in range(0, len(col_max)):
#         worksheet4.set_column(j, j, width=int(col_max[j]))
#
#     worksheet4.write_row(0, 0, [
#         "SCIENCE BRANCH WORKPLANNING - SUMMARY OF UNSUMBITTED OR UNAPPROVED PROJECTS BY SECTION", ], bold_format_lg)
#     worksheet4.write_row(1, 0, [timezone.now().strftime('%Y-%m-%d'), ], bold_format)
#     worksheet4.merge_range('m3:o3'.upper(), 'A-Base', header_format_centered)
#     worksheet4.merge_range('p3:r3'.upper(), 'B-Base', header_format_centered)
#     worksheet4.merge_range('s3:u3'.upper(), 'C-Base', header_format_centered)
#     worksheet4.merge_range('v3:x3'.upper(), 'Total', header_format_centered)
#
#     header = [
#         "Division",
#         "Section",
#         "Core / flex",
#         verbose_field_name(models.Project.objects.first(), 'programs'),
#         verbose_field_name(models.Project.objects.first(), 'tags'),
#         "Project ID",
#         verbose_field_name(models.Project.objects.first(), 'project_title'),
#         "Project leads",
#         "Submitted",
#         "Approved by section head",
#         "Section head feedback",
#         'Total FTE\n(weeks)',
#         'Total OT\n(hours)',
#     ]
#
#     financial_headers = [
#         'Salary\n(in excess of FTE)',
#         'O & M\n(including staff)',
#         'Capital',
#     ]
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#     header.extend(financial_headers)
#
#     worksheet4.write_row(3, 0, header, header_format)
#     i = 4
#     for s in section_list.order_by("division", "name"):
#         # get a list of projects..
#
#         if regions == str(mar_id):
#             project_list = s.projects.filter(year=fiscal_year).filter(Q(submitted=False)).order_by("id")
#         else:
#             project_list = s.projects.filter(year=fiscal_year).filter(
#                 Q(submitted=False) | Q(section_head_approved=False)).order_by("id")
#
#         for project in set(project_list):
#             core_flex = "/".join(list(set(([program.get_is_core_display() for program in project.programs.all()]))))
#
#             leads = listrify(
#                 list(set([str(staff.user) for staff in
#                           models.Staff.objects.filter(project=project, lead=True) if staff.user])))
#             programs = listrify(["{}".format(program.short_name) for program in
#                                  project.programs.all()])
#             tags = listrify([str(tag) for tag in project.tags.all()])
#             total_fte = models.Staff.objects.filter(
#                 project=project).order_by("duration_weeks").aggregate(dsum=Sum("duration_weeks"))['dsum']
#             total_ot = models.Staff.objects.filter(
#                 project=project).order_by("overtime_hours").aggregate(dsum=Sum("overtime_hours"))['dsum']
#
#             data_row = [
#                 s.division.name,
#                 s.name,
#                 core_flex,
#                 programs,
#                 tags,
#                 project.id,
#                 project.project_title,
#                 leads,
#                 yesno(project.submitted),
#                 yesno(project.section_head_approved),
#                 project.section_head_feedback,
#                 zero2val(total_fte, None),
#                 zero2val(total_ot, None),
#             ]
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project=project).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#
#                 other_om = models.OMCost.objects.filter(project=project, funding_source=source
#                                                         ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))['dsum']
#
#                 capital = models.CapitalCost.objects.filter(project=project, funding_source=source
#                                                             ).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))[
#                     'dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 data_row.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             data_row.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#
#             j = 0
#
#             worksheet4.write_row(i, 0, data_row, normal_format)
#             i += 1
#         # if there are no projects, don't add a line!
#         if project_list.count() > 0:
#             section_summary = repeat(" ,", 9).split(",")
#             total_salary = 0
#             total_om = 0
#             total_capital = 0
#             for source in models.FundingSource.objects.filter(id__in=[1, 2, 3]):
#                 staff_salary = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 staff_om = models.Staff.objects.filter(project__in=project_list).filter(
#                     employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source=source
#                 ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
#                 other_om = models.OMCost.objects.filter(
#                     project__in=project_list, funding_source=source
#                 ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
#                 capital = models.CapitalCost.objects.filter(
#                     project__in=project_list, funding_source=source).order_by("budget_requested").aggregate(
#                     dsum=Sum("budget_requested"))[
#                     'dsum']
#
#                 total_salary += nz(staff_salary, 0)
#                 total_om += nz(staff_om, 0) + nz(other_om, 0)
#                 total_capital += nz(capital, 0)
#
#                 section_summary.extend([
#                     zero2val(nz(staff_salary, 0), '--'),
#                     zero2val(nz(staff_om, 0) + nz(other_om, 0), '--'),
#                     zero2val(nz(capital, 0), '--'),
#                 ])
#             section_summary.extend([
#                 zero2val(total_salary, '--'),
#                 zero2val(total_om, '--'),
#                 zero2val(total_capital, '--'),
#             ])
#             worksheet4.write_row(i, 0, section_summary, divider_format)
#             i += 1
#
#     worksheet4.conditional_format(4, 10, i, 21, {
#         'type': 'cell',
#         'criteria': 'greater than',
#         'value': 0,
#         'format': normal_num_format,
#     })
#
#     workbook.close()
#     return target_url
#
#
# def generate_master_spreadsheet(fiscal_year, regions, divisions, sections, user=None):
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
#     target_file = "temp_export.xlsx"
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#     worksheet1 = workbook.add_worksheet(name="Project List")
#     # worksheet2 = workbook.add_worksheet(name="FTE List")
#     # worksheet3 = workbook.add_worksheet(name="Collaborators")
#     # worksheet4 = workbook.add_worksheet(name="Collaborative Agreements")
#     # worksheet5 = workbook.add_worksheet(name="O & M")
#     # worksheet6 = workbook.add_worksheet(name="Capital")
#     # worksheet7 = workbook.add_worksheet(name="Gs & Cs")
#
#     # create formatting
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
#          "text_wrap": True})
#     total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'left', "text_wrap": True})
#     normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
#     bold_format = workbook.add_format({"align": 'left', 'bold': True})
#
#     # need to assemble a section list
#     ## first look at the sections arg; if not null, we don't need anything else
#     if sections != "None":
#         section_list = shared_models.Section.objects.filter(id__in=sections.split(","))
#     ## next look at the divisions arg; if not null, we don't need anything else
#     elif divisions != "None":
#         section_list = shared_models.Section.objects.filter(division_id__in=divisions.split(","))
#     ## next look at the divisions arg; if not null, we don't need anything else
#     elif regions != "None":
#         section_list = shared_models.Section.objects.filter(division__branch__region_id__in=regions.split(","))
#     else:
#         section_list = []
#
#         # If there is no user, it means that this report is being called throught the report_search view (as opposed to my_section view)
#
#     if not user:
#         project_list = models.Project.objects.filter(year=fiscal_year, section__in=section_list)
#
#     else:
#         project_list = models.Project.objects.filter(year=fiscal_year).filter(section__head_id=user)
#
#     # spreadsheet: Project List #
#     #############################
#     if len(project_list) == 0:
#         worksheet1.write_row(0, 0, ["There are no projects to report", ], bold_format)
#     else:
#         # get a project list for the year
#
#         header = [
#             "Project ID",
#             verbose_field_name(project_list.first(), 'project_title'),
#             "Section",
#             "Division",
#             verbose_field_name(project_list.first(), 'activity_type'),
#             verbose_field_name(project_list.first(), 'default_funding_source'),
#             verbose_field_name(project_list.first(), 'functional_group'),
#             "Theme",
#             verbose_field_name(project_list.first(), 'tags'),
#             "Coding",
#             verbose_field_name(project_list.first(), 'status'),
#             "Project lead",
#             verbose_field_name(project_list.first(), 'is_approved'),
#             verbose_field_name(project_list.first(), 'start_date'),
#             verbose_field_name(project_list.first(), 'end_date'),
#             verbose_field_name(project_list.first(), 'description'),
#             verbose_field_name(project_list.first(), 'priorities'),
#             verbose_field_name(project_list.first(), 'deliverables'),
#             verbose_field_name(project_list.first(), 'data_collection'),
#             verbose_field_name(project_list.first(), 'data_sharing'),
#             verbose_field_name(project_list.first(), 'data_storage'),
#             verbose_field_name(project_list.first(), 'metadata_url'),
#             verbose_field_name(project_list.first(), 'regional_dm_needs'),
#             verbose_field_name(project_list.first(), 'vehicle_needs'),
#             verbose_field_name(project_list.first(), 'it_needs'),
#             verbose_field_name(project_list.first(), 'chemical_needs'),
#             verbose_field_name(project_list.first(), 'ship_needs'),
#             'Total FTE (weeks)',
#             'Total Salary (in excess of FTE)',
#             'Total OT (hours)',
#             'Total O & M (including staff)',
#             'Total Capital',
#             'Total G&Cs',
#             verbose_field_name(project_list.first(), 'submitted'),
#             verbose_field_name(project_list.first(), 'approved'),
#             verbose_field_name(project_list.first(), 'notes'),
#             verbose_field_name(project_list.first(), 'meeting_notes'),
#
#         ]
#
#         # create the col_max column to store the length of each header
#         # should be a maximum column width to 100
#         col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
#
#         worksheet1.write_row(0, 0, header, header_format)
#
#         i = 1
#         for p in project_list:
#
#             fte_total = 0
#             salary_total = 0
#             ot_total = 0
#             om_total = 0
#             gc_total = 0
#             capital_total = 0
#
#             # first calc for staff
#             for staff in p.staff_members.all():
#                 # exclude full time employees
#                 if staff.employee_type.id != 1 or staff.employee_type.id != 6:
#                     # if salary
#                     if staff.employee_type.cost_type == 1:
#                         salary_total += nz(staff.cost, 0)
#                     # if o&M
#                     elif staff.employee_type.cost_type == 2:
#                         om_total += nz(staff.cost, 0)
#
#                 # include only FTEs
#                 fte_total += nz(staff.duration_weeks, 0)
#
#                 ot_total += nz(staff.overtime_hours, 0)
#
#             # O&M costs
#             for cost in p.om_costs.all():
#                 om_total += nz(cost.budget_requested, 0)
#
#             # Capital costs
#             for cost in p.capital_costs.all():
#                 capital_total += nz(cost.budget_requested, 0)
#
#             # g&c costs
#             for cost in p.gc_costs.all():
#                 gc_total += nz(cost.budget_requested, 0)
#
#             try:
#                 budget_code = p.budget_code.code
#             except:
#                 budget_code = "n/a"
#
#             try:
#                 status = p.status.name
#             except:
#                 status = "n/a"
#
#             try:
#                 lead = str(
#                     ["{} {}".format(lead.user.first_name, lead.user.last_name) for lead in
#                      p.staff_members.filter(lead=True)]).replace(
#                     "[", "").replace("]", "").replace("'", "").replace('"', "")
#             except:
#                 lead = "n/a"
#
#             try:
#                 programs = get_field_value(p, "programs")
#             except:
#                 programs = "n/a"
#
#             try:
#                 tags = get_field_value(p, "tags")
#             except:
#                 tags = "n/a"
#
#             try:
#                 start = p.start_date.strftime('%Y-%m-%d')
#             except:
#                 start = "n/a"
#
#             try:
#                 end = p.end_date.strftime('%Y-%m-%d')
#             except:
#                 end = "n/a"
#
#             try:
#                 division = p.section.division.name
#             except:
#                 division = "MISSING"
#
#             try:
#                 section = p.section.name
#             except:
#                 section = "MISSING"
#
#             data_row = [
#                 p.id,
#                 p.project_title,
#                 section,
#                 division,
#                 str(p.activity_type),
#                 str(p.default_funding_source),
#                 str(p.functional_group),
#                 str(p.functional_group.theme) if p.functional_group else "",
#                 tags,
#                 p.coding,
#                 status,
#                 lead,
#                 yesno(p.is_approved),
#                 start,
#                 end,
#                 html2text.html2text(nz(p.description, "")),
#                 html2text.html2text(nz(p.priorities, "")),
#                 html2text.html2text(nz(p.deliverables, "")),
#                 html2text.html2text(nz(p.data_collection, "")),
#                 html2text.html2text(nz(p.data_sharing, "")),
#                 html2text.html2text(nz(p.data_storage, "")),
#                 p.metadata_url,
#                 html2text.html2text(nz(p.regional_dm_needs, "")),
#                 html2text.html2text(nz(p.vehicle_needs, "")),
#                 html2text.html2text(nz(p.it_needs, "")),
#                 html2text.html2text(nz(p.chemical_needs, "")),
#                 html2text.html2text(nz(p.ship_needs, "")),
#                 fte_total,
#                 salary_total,
#                 ot_total,
#                 om_total,
#                 capital_total,
#                 gc_total,
#                 yesno(p.submitted),
#                 yesno(p.approved),
#                 html2text.html2text(nz(p.notes, "")),
#                 html2text.html2text(nz(p.meeting_notes, "")),
#             ]
#
#             # adjust the width of the columns based on the max string length in each col
#             ## replace col_max[j] if str length j is bigger than stored value
#
#             j = 0
#             for d in data_row:
#                 # if new value > stored value... replace stored value
#                 if len(str(d)) > col_max[j]:
#                     if len(str(d)) < 100:
#                         col_max[j] = len(str(d))
#                     else:
#                         col_max[j] = 100
#                 j += 1
#
#             worksheet1.write_row(i, 0, data_row, normal_format)
#             i += 1
#
#         for j in range(0, len(col_max)):
#             worksheet1.set_column(j, j, width=col_max[j] * 1.1)
#
#     workbook.close()
#     return target_url
#
#
# def generate_program_list():
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
#     target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#
#     # create formatting variables
#     title_format = workbook.add_format({'bold': True, "align": 'normal', 'font_size': 24, })
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#D6D1C0', "align": 'normal',
#          "text_wrap": True})
#     total_format = workbook.add_format({'bold': True, "align": 'left', "text_wrap": True, 'num_format': '$#,##0'})
#     normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
#
#     # get the program list
#     program_list = models.Program2.objects.all()
#
#     field_list = [
#         'national_responsibility_eng',
#         'national_responsibility_fra',
#         'program_inventory',
#         'funding_source_and_type',
#         'regional_program_name_eng',
#         'regional_program_name_fra',
#         'examples',
#         'is_core',
#     ]
#
#     # define the header
#     header = [get_verbose_label(program_list.first(), field) for field in field_list]
#     header.append('Number of projects tagged')
#
#     title = "Science Program List"
#     # define a worksheet
#     my_ws = workbook.add_worksheet(name=title)
#
#     i = 3
#     for program in program_list:
#         # create the col_max column to store the length of each header
#         # should be a maximum column width to 100
#         col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
#         my_ws.write(0, 0, title, title_format)
#         my_ws.write_row(2, 0, header, header_format)
#
#         data_row = [get_field_value(program, field) for field in field_list]
#         data_row.append(program.projects.count())
#         # adjust the width of the columns based on the max string length in each col
#         ## replace col_max[j] if str length j is bigger than stored value
#
#         j = 0
#         for d in data_row:
#             # if new value > stored value... replace stored value
#             if len(str(d)) > col_max[j]:
#                 if len(str(d)) < 75:
#                     col_max[j] = len(str(d))
#                 else:
#                     col_max[j] = 75
#             j += 1
#
#         my_ws.write_row(i, 0, data_row, normal_format)
#         i += 1
#
#         # set column widths
#         for j in range(0, len(col_max)):
#             my_ws.set_column(j, j, width=col_max[j] * 1.1)
#
#     workbook.close()
#     return target_url
