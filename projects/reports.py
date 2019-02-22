import xlsxwriter as xlsxwriter
from django.db.models import Sum, Q
from django.conf import settings
from lib.functions.nz import nz
from lib.functions.verbose_field_name import verbose_field_name
from . import models
import os

def generate_master_spreadsheet(fiscal_year, user=None):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
    target_file = "temp_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    worksheet1 = workbook.add_worksheet(name="Project List")
    worksheet2 = workbook.add_worksheet(name="FTE List")
    worksheet3 = workbook.add_worksheet(name="Collaborators")
    worksheet4 = workbook.add_worksheet(name="Collaborative Agreements")
    worksheet5 = workbook.add_worksheet(name="O&M Requests")
    worksheet6 = workbook.add_worksheet(name="Capital Requests")
    worksheet7 = workbook.add_worksheet(name="G&C Requests")

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
         "text_wrap": True})
    total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'left', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
    bold_format = workbook.add_format({"align": 'center', 'bold': True})

    # spreadsheet: Project List #
    #############################

    # get a project list for the year
    if not user:
        project_list = models.Project.objects.filter(fiscal_year=fiscal_year)
    else:
        project_list = models.Project.objects.filter(fiscal_year=fiscal_year).filter(section__section_head__id=user)
    print(project_list.count())
    header = [
        "Project ID",
        verbose_field_name(project_list.first(), 'project_title'),
        "Section",
        "Division",
        verbose_field_name(project_list.first(), 'program'),
        "Coding",
        verbose_field_name(project_list.first(), 'status'),
        verbose_field_name(project_list.first(), 'approved'),
        verbose_field_name(project_list.first(), 'start_date'),
        verbose_field_name(project_list.first(), 'end_date'),
        verbose_field_name(project_list.first(), 'description'),
        verbose_field_name(project_list.first(), 'priorities'),
        verbose_field_name(project_list.first(), 'deliverables'),
        verbose_field_name(project_list.first(), 'data_collection'),
        verbose_field_name(project_list.first(), 'data_sharing'),
        verbose_field_name(project_list.first(), 'data_storage'),
        verbose_field_name(project_list.first(), 'metadata_url'),
        verbose_field_name(project_list.first(), 'regional_dm'),
        verbose_field_name(project_list.first(), 'regional_dm_needs'),
        verbose_field_name(project_list.first(), 'sectional_dm'),
        verbose_field_name(project_list.first(), 'sectional_dm_needs'),
        verbose_field_name(project_list.first(), 'vehicle_needs'),
        verbose_field_name(project_list.first(), 'it_needs'),
        verbose_field_name(project_list.first(), 'chemical_needs'),
        verbose_field_name(project_list.first(), 'ship_needs'),
        'Total FTE (weeks)',
        'Total Salary (in excess of FTE)',
        'Total OT (hours)',
        'Total O&M',
        'Total Capital',
        'Total G&Cs',
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet1.write_row(0, 0, header, header_format)

    i = 1
    for p in project_list:

        fte_total = 0
        salary_total = 0
        ot_total = 0
        om_total = 0
        gc_total = 0
        capital_total = 0

        # first calc for staff
        for staff in p.staff_members.all():
            # exclude full time employees
            if staff.employee_type.id != 1 or staff.employee_type.id != 6:
                # if salary
                if staff.employee_type.cost_type is 1:
                    salary_total += nz(staff.cost, 0)
                # if o&M
                elif staff.employee_type.cost_type is 2:
                    om_total += nz(staff.cost, 0)

            # include only FTEs
            if staff.employee_type.id == 1 or staff.employee_type.id == 6:
                fte_total += nz(staff.duration_weeks, 0)

            ot_total += nz(staff.overtime_hours, 0)

        # O&M costs
        for cost in p.om_costs.all():
            om_total += nz(cost.budget_requested, 0)

        # Capital costs
        for cost in p.capital_costs.all():
            capital_total += nz(cost.budget_requested, 0)

        # g&c costs
        for cost in p.gc_costs.all():
            gc_total += nz(cost.budget_requested, 0)

        try:
            budget_code = p.budget_code.code
        except:
            budget_code = "n/a"

        try:
            status = p.status.name
        except:
            status = "n/a"

        try:
            program = p.program.name
        except:
            program = "n/a"

        try:
            start = p.start_date.strftime('%Y-%m-%d')
        except:
            start = "n/a"

        try:
            end = p.end_date.strftime('%Y-%m-%d')
        except:
            end = "n/a"

        data_row = [
            p.id,
            p.project_title,
            p.section.division.name,
            p.section.name,
            program,
            p.coding,
            status,
            p.approved,
            start,
            end,
            p.description,
            p.priorities,
            p.deliverables,
            p.data_collection,
            p.data_sharing,
            p.data_storage,
            p.metadata_url,
            p.regional_dm,
            p.regional_dm_needs,
            p.sectional_dm,
            p.sectional_dm_needs,
            p.vehicle_needs,
            p.it_needs,
            p.chemical_needs,
            p.ship_needs,
            fte_total,
            salary_total,
            ot_total,
            om_total,
            capital_total,
            gc_total,
        ]

        # adjust the width of the columns based on the max string length in each col
        ## replace col_max[j] if str length j is bigger than stored value

        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet1.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet1.set_column(j, j, width=col_max[j] * 1.1)

    # spreadsheet: FTE List #
    #########################

    # create a queryset, showing all users and their total hours for FTE

    if not user:
        staff_list = models.Staff.objects.filter(project__fiscal_year=fiscal_year).filter(employee_type=1).values(
            'user__last_name', 'user__first_name',
        ).order_by('user__last_name', 'user__first_name', ).distinct().annotate(sum_of_weeks=Sum('duration_weeks'))
    else:
        staff_list = models.Staff.objects.filter(project__fiscal_year=fiscal_year).filter(project__section__section_head__id=user).filter(employee_type=1).values(
            'user__last_name', 'user__first_name',
        ).order_by('user__last_name', 'user__first_name', ).distinct().annotate(sum_of_weeks=Sum('duration_weeks'))

    header = [
        'Employee Name',
        'Total FTE (weeks)',
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet2.write_row(0, 0, header, header_format)

    i = 1
    for s in staff_list:
        data_row = [
            "{}, {}".format(s['user__last_name'], s['user__first_name'], ),
            s['sum_of_weeks'],
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet2.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet2.set_column(j, j, width=col_max[j] * 1.1)

    # TODO: insert conditional formatting regarding the number of hours

    # spreadsheet: collaborator List #
    ##################################
    if not user:
        collaborator_list = models.Collaborator.objects.filter(project__fiscal_year=fiscal_year)
    else:
        collaborator_list = models.Collaborator.objects.filter(project__fiscal_year=fiscal_year).filter(project__section__section_head__id=user)


    header = [
        "Project Id",
        verbose_field_name(collaborator_list.first(), 'name'),
        verbose_field_name(collaborator_list.first(), 'type'),
        verbose_field_name(collaborator_list.first(), 'critical'),
        verbose_field_name(collaborator_list.first(), 'notes'),
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet3.write_row(0, 0, header, header_format)

    i = 1
    for item in collaborator_list:
        data_row = [
            item.project.id,
            item.name,
            item.get_type_display(),
            item.critical,
            item.notes,
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet3.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet3.set_column(j, j, width=col_max[j] * 1.1)

    # spreadsheet: agreement List #
    ##################################

    if not user:
        agreement_list = models.CollaborativeAgreement.objects.filter(project__fiscal_year=fiscal_year)
    else:
        agreement_list = models.CollaborativeAgreement.objects.filter(project__fiscal_year=fiscal_year).filter(project__section__section_head__id=user)

    header = [
        "Project Id",
        verbose_field_name(agreement_list.first(), 'partner_organization'),
        verbose_field_name(agreement_list.first(), 'agreement_title'),
        verbose_field_name(agreement_list.first(), 'new_or_existing'),
        verbose_field_name(agreement_list.first(), 'notes'),
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet4.write_row(0, 0, header, header_format)

    i = 1
    for item in agreement_list:
        data_row = [
            item.project.id,
            item.partner_organization,
            item.agreement_title,
            item.get_new_or_existing_display(),
            item.notes,
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet4.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet4.set_column(j, j, width=col_max[j] * 1.1)


    # spreadsheet: OM List #
    ########################
    if not user:
        om_list = models.OMCost.objects.filter(project__fiscal_year=fiscal_year).filter(budget_requested__gt=0)
    else:
        om_list = models.OMCost.objects.filter(project__fiscal_year=fiscal_year).filter(budget_requested__gt=0).filter(project__section__section_head__id=user)

    header = [
        "Project Id",
        verbose_field_name(om_list.first(), 'om_category'),
        verbose_field_name(om_list.first(), 'description'),
        verbose_field_name(om_list.first(), 'budget_requested'),
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet5.write_row(0, 0, header, header_format)

    i = 1
    for item in om_list:
        data_row = [
            item.project.id,
            str(item.om_category),
            item.description,
            item.budget_requested,
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet5.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet5.set_column(j, j, width=col_max[j] * 1.1)


    # spreadsheet: Capital List #
    #############################
    if not user:
        capital_list = models.CapitalCost.objects.filter(project__fiscal_year=fiscal_year)
    else:
        capital_list = models.CapitalCost.objects.filter(project__fiscal_year=fiscal_year).filter(project__section__section_head__id=user)

    header = [
        "Project Id",
        verbose_field_name(capital_list.first(), 'category'),
        verbose_field_name(capital_list.first(), 'description'),
        verbose_field_name(capital_list.first(), 'budget_requested'),
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet6.write_row(0, 0, header, header_format)

    i = 1
    for item in capital_list:
        data_row = [
            item.project.id,
            item.get_category_display(),
            item.description,
            item.budget_requested,
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet6.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet6.set_column(j, j, width=col_max[j] * 1.1)


    # spreadsheet: GC List #
    ########################
    if not user:
        gc_list = models.GCCost.objects.filter(project__fiscal_year=fiscal_year)
    else:
        gc_list = models.GCCost.objects.filter(project__fiscal_year=fiscal_year).filter(project__section__section_head__id=user)

    header = [
        "Project Id",
        verbose_field_name(gc_list.first(), 'recipient_org'),
        verbose_field_name(gc_list.first(), 'project_lead'),
        verbose_field_name(gc_list.first(), 'proposed_title'),
        verbose_field_name(gc_list.first(), 'gc_program'),
        verbose_field_name(gc_list.first(), 'budget_requested'),
    ]


    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    worksheet7.write_row(0, 0, header, header_format)

    i = 1
    for item in gc_list:
        data_row = [
            item.project.id,
            item.recipient_org,
            item.project_lead,
            item.proposed_title,
            item.gc_program,
            item.budget_requested,
        ]

        # adjust the width of the columns based on the max string length in each col
        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        worksheet7.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        worksheet7.set_column(j, j, width=col_max[j] * 1.1)


    workbook.close()
    return target_url
