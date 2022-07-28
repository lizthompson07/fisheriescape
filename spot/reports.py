from django.http import HttpResponse
from . import models
from . import filters
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.utils.cell import get_column_letter
from django.core.exceptions import ObjectDoesNotExist

green = 'C4D79B'


def export_data(request):
    data = models.Data.objects.all()
    data_filter = filters.DataFilter(request.GET, queryset=data).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Data.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Data'
    columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Samples Collected',
        'Samples Collected Comment',
        'Sample Collected Database',
        'Shared Drive',
        'Barriers to Sample Collection',
        'Was sample collection data entered into database(s)?',
        'Was sample data quality check complete?',
        'Sample Format(s)',
        'Data Product(s)',
        'Data Products Database(s)',
        'Data Products Comment',
        'date_last_modified',
        'last_modified_by',
    ]

    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    for obj in data_filter:
        proj = models.Project.objects.get(pk=obj.project.id)
        if obj.river and obj.river.species:
            species_tmp = obj.river.species.name
        else:
            species_tmp = None
        if obj.river and obj.river.cu_name:
            cu_tmp = obj.river.cu_name.name
        else:
            cu_tmp = None

        funding_year = models.FundingYears.objects.filter(project=obj.project.id)
        row_num += 1
        row = [
            proj.agreement_number,
            proj.project_number,
            ", ".join(i.funding_year for i in funding_year.all()),
            ", ".join(i.name for i in proj.funding_sources.all()),
            ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
            proj.project_type,
            ", ".join(i.name for i in proj.project_sub_type.all()),
            ", ".join(i.name for i in proj.project_theme.all()),
            proj.area,
            ", ".join(i.name for i in proj.river.all()),
            species_tmp,
            cu_tmp,
            proj.first_nation.name if proj.first_nation else None,
            proj.funding_recipient,
            proj.lead_organization,
            ", ".join(i.name for i in proj.hatchery_name.all()),
            obj.samples_collected,
            obj.samples_collected_comment,
            obj.samples_collected_database,
            obj.shared_drive,
            obj.sample_barrier,
            obj.sample_entered_database,
            obj.data_quality_check,
            obj.sample_format,
            obj.data_products,
            obj.data_products_database,
            obj.data_products_comment,
            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    workbook.save(response)

    return response


def export_method(request):
    method = models.Method.objects.all()
    method_filter = filters.MethodFilter(request.GET, queryset=method).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Method.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Method'
    columns = [
        'Agreement Number',
        'Unique Method Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Field Work Methods Type',
        'Planning Method Type',
        'Sample Processing Method Type',
        'Scale Processing Location',
        'Otolith Processing Location',
        'DNA Processing Location',
        'Heads Processing Location',
        'Instrument Data Processing Location',
        'date_last_modified',
        'last_modified_by',
    ]

    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    method_document_worksheet = workbook.create_sheet("Method Document", 1)
    method_document_columns = [
        'Agreement Number',
        'Unique Method Number',
        'Project Number',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Method Document Type',
        'Author',
        'Year of Publication',
        'Title',
        'Reference Number',
        'Document Link',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(method_document_columns, 1):
        method_document_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = method_document_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    meth_num = 1
    for obj in method_filter:
        proj = models.Project.objects.get(pk=obj.project.id)
        species_tmp = ""
        cu_tmp = ""
        for i in proj.river.all():
            if i.species:
                species_tmp += str(i.species.name + ", ")
            if i.cu_name:
                cu_tmp += str(i.cu_name.name + ", ")
        funding_year = models.FundingYears.objects.filter(project=obj.project.id)
        row_num += 1
        row = [
            proj.agreement_number,
            obj.unique_method_number,
            proj.project_number,
            ", ".join(i.funding_year for i in funding_year.all()),
            ", ".join(i.name for i in proj.funding_sources.all()),
            ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
            proj.project_type,
            ", ".join(i.name for i in proj.project_sub_type.all()),
            ", ".join(i.name for i in proj.project_theme.all()),
            proj.area,
            ", ".join(i.name for i in proj.river.all()),
            species_tmp,
            cu_tmp,
            proj.first_nation.name if proj.first_nation else None,
            proj.funding_recipient,
            proj.lead_organization,
            ", ".join(i.name for i in proj.hatchery_name.all()),
            obj.field_work_method_type,
            obj.planning_method_type,
            obj.sample_processing_method_type,
            obj.scale_processing_location,
            obj.otolith_processing_location,
            obj.DNA_processing_location,
            obj.heads_processing_location,
            obj.instrument_data_processing_location,
            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

        method_documents = models.MethodDocument.objects.filter(method=obj.id)
        for method in method_documents:
            meth_num += 1
            method_rows = [
                proj.agreement_number,
                method.unique_method_number,
                proj.project_number,
                ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
                proj.project_type,
                ", ".join(i.name for i in proj.project_sub_type.all()),
                ", ".join(i.name for i in proj.project_theme.all()),
                proj.area,
                ", ".join(i.name for i in proj.river.all()),
                species_tmp,
                cu_tmp,
                proj.first_nation.name if proj.first_nation else None,
                proj.funding_recipient,
                proj.lead_organization,
                ", ".join(i.name for i in proj.hatchery_name.all()),
                method.method_document_type,
                method.authors,
                method.publication_year,
                method.title,
                method.reference_number,
                method.document_link,
                method.date_last_modified,
                method.last_modified_by.get_full_name() if method.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(method_rows, 1):
                cell = method_document_worksheet.cell(row=meth_num, column=col_num)
                cell.value = cell_value

    workbook.save(response)
    return response


def export_reports(request):
    reports = models.Reports.objects.all()
    reports_filter = filters.ReportsFilter(request.GET, queryset=reports).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Reports.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Reports'
    columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Report Timeline',
        'Report Type',
        'Report Limitations and Concerns',
        'Document Name',
        'Document Author',
        'Document Reference Information',
        'Document Link',
        'Was this report Published?',
        'date_last_modified',
        'last_modified_by',

    ]
    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    for obj in reports_filter:
        proj = models.Project.objects.get(pk=obj.project.id)
        species_tmp = ""
        cu_tmp = ""
        for i in proj.river.all():
            if i.species:
                species_tmp += str(i.species.name + ", ")
            if i.cu_name:
                cu_tmp += str(i.cu_name.name + ", ")
        funding_year = models.FundingYears.objects.filter(project=obj.project.id)
        row_num += 1
        row = [
            proj.agreement_number,
            proj.project_number,
            ", ".join(i.funding_year for i in funding_year.all()),
            ", ".join(i.name for i in proj.funding_sources.all()),
            ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
            proj.project_type,
            ", ".join(i.name for i in proj.project_sub_type.all()),
            ", ".join(i.name for i in proj.project_theme.all()),
            obj.project.area,
            ", ".join(i.name for i in proj.river.all()),
            species_tmp,
            cu_tmp,
            proj.first_nation.name if proj.first_nation else None,
            proj.funding_recipient,
            proj.lead_organization,
            ", ".join(i.name for i in proj.hatchery_name.all()),
            obj.report_timeline,
            obj.report_type,
            obj.report_concerns,
            obj.document_name,
            obj.document_author,
            obj.document_reference_information,
            obj.document_link,
            obj.published,
            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    workbook.save(response)
    return response


def export_project_full(request):
    project = models.Project.objects.all()
    project_filter = filters.ProjectFilter(request.GET, queryset=project).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Full-Projects.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Projects'

    ########################
    # PROJECT SHEET/HEADER #
    columns = [
        'Agreement Number',
        'Project Number',

        'Agreement History',
        'Project Name',
        'Project Description',
        'Funding Year',
        'Start Date',
        'End Date',

        'Area',
        'Other Species',
        'Ecosystem Type',
        'Lake System(s)',
        'Watershed(s)',
        'Other Site Info',

        'Salmon Life Stage',
        'Aquaculture License Number',
        'Water License Number',
        'Hatchery Name',
        'DFO Tenure',

        'Project Stage',
        'Project Type',
        'Project Sub Type',
        'Monitoring Approach',
        'Project Theme',
        'Core Component',
        'Supportive Component',
        'Project Purpose',
        'Category Comments',

        'Link to other DFO Programs',
        'Linked DFO Program Project Reference',
        'Link to other Government Departments',
        'Policy Connections',

        'DFO Project Authority',
        'DFO Area Chief',
        'DFO IAA',
        'DFO Resource Manager',
        'Funding Recipient',
        'First Nation/Tribal Council',
        'Contact',
        'Contact Role',
        'DFO Technicians/Biologists',
        'Contractors',
        'Contractor Contact',
        'Partner',
        'Partner Contact',

        'Agreement Database',
        'Agreement Comment',
        'Funding Sources',
        'Other Funding Sources',
        'Agreement Type',
        'Project Lead Organization',

        'date_last_modified',
        'last_modified_by',


    ]
    row_num = 1
    for col_num, column_title in enumerate(columns, 1):
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ##############################
    # FUNDING YEARS SHEET/HEADER #
    funding_worksheet = workbook.create_sheet("Funding", 1)
    funding_columns = [
        'Agreement Number',
        'Project Number',
        'Project Name',
        'Funding Year',
        'Project Authority',
        'First Nation',
        'Funding Recipient',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Agreement Cost',
        'Project Cost',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1
    for col_num, column_title in enumerate(funding_columns, 1):
        funding_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = funding_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ##############################
    # Rivers SHEET/HEADER #
    river_worksheet = workbook.create_sheet("Rivers", 9)
    river_columns = [
        'Agreement Number',
        'Project Number',
        'Project Name',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Name',
        'Latitude',
        'Longitude',
        'Sub District Area',
        'Species',
        'Stock Management Unit',
        'CU index',
        'CU Name',
        'Pop ID',
        'DU',
        'DU Number',
    ]
    row_num = 1
    for col_num, column_title in enumerate(river_columns, 1):
        river_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = river_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ############################
    # PROJECT CERTIFIED HEADER #
    certified_worksheet = workbook.create_sheet("Project Certified", 10)
    certified_columns = [
        'Agreement Number',
        'Project Name',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Certified Date',
        'Certified By',
    ]
    row_num = 1
    for col_num, column_title in enumerate(certified_columns, 1):
        certified_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = certified_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title


    ##########################
    # OBJECTIVE SHEET/HEADER #
    objective_worksheet = workbook.create_sheet("Objectives", 2)
    objective_columns = [
        'Agreement Number',
        'Unique Objective',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Task Description',
        'Element Title',
        'Activity Title',
        'PST Requirement Identified?',
        'Objective Category',
        'SIL Requirement',
        'Expected Result(s)',
        'Products/Reports to Provide DFO',
        'Outcome Comment',
        'date_last_modified',
        'last_modified_by',

    ]
    row_num = 1
    for col_num, column_title in enumerate(objective_columns, 1):
        objective_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = objective_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    #########################
    # SAMPLE OUTCOME HEADER #
    sample_outcome_worksheet = workbook.create_sheet("Sample Outcomes", 3)
    sample_outcomes_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Unique Objective Number',
        'Sampling Outcome',
        'Were outcomes delivered?',
        'Quality of Outcome',
        'Sample Outcome Comment',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(sample_outcomes_columns, 1):
        sample_outcome_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = sample_outcome_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ##################################
    # REPORTING OUTCOME SHEET/HEADER #
    reporting_outcome_worksheet = workbook.create_sheet("Report Outcomes", 4)
    report_outcomes_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Unique Objective Number',
        'Reporting Outcome',
        'Was the outcome deliverable met?',
        'Site',
        'Report Link',
        'Reporting Outcome Comment',
        'Reporting Outcome Metric',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(report_outcomes_columns, 1):
        reporting_outcome_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = reporting_outcome_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    #####################
    # DATA SHEET/HEADER #
    data_worksheet = workbook.create_sheet("Data", 5)
    data_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Samples Collected',
        'Samples Collected Comment',
        'Sample Collected Database',
        'Shared Drive',
        'Barriers to Sample Collection',
        'Was sample collection data entered into database(s)?',
        'Was sample data quality check complete?',
        'Sample Format(s)',
        'Data Product(s)',
        'Data Products Database(s)',
        'Data Products Comment',
        'date_last_modified',
        'last_modified_by',
    ]

    row_num = 1

    for col_num, column_title in enumerate(data_columns, 1):
        cell = data_worksheet.cell(row=row_num, column=col_num)
        data_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    #######################
    # METHOD SHEET/HEADER #
    method_worksheet = workbook.create_sheet("Method", 6)
    method_columns = [
        'Agreement Number',
        'Unique Method Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Field Work Methods Type',
        'Planning Method Type',
        'Sample Processing Method Type',
        'Scale Processing Location',
        'Otolith Processing Location',
        'DNA Processing Location',
        'Heads Processing Location',
        'Instrument Data Processing Location',
        'date_last_modified',
        'last_modified_by',
    ]

    row_num = 1

    for col_num, column_title in enumerate(method_columns, 1):
        method_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = method_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ################################
    # METHOD DOCUMENT SHEET/HEADER #
    method_document_worksheet = workbook.create_sheet("Method Document", 7)
    method_document_columns = [
        'Agreement Number',
        'Unique Method Number',
        'Project Number',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Method Document Type',
        'Author',
        'Year of Publication',
        'Title',
        'Reference Number',
        'Document Link',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(method_document_columns, 1):
        method_document_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = method_document_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    #################
    # REPORT SHEET/HEADER #
    report_worksheet = workbook.create_sheet("Reports", 8)
    report_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Report Timeline',
        'Report Type',
        'Report Limitations and Concerns',
        'Document Name',
        'Document Author',
        'Document Reference Information',
        'Document Link',
        'Was this report Published?',
        'date_last_modified',
        'last_modified_by',

    ]
    row_num = 1

    for col_num, column_title in enumerate(report_columns, 1):
        report_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = report_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ###########
    # PROJECT #
    repo_num = 1
    sampo_num = 1
    row_num = 1
    meth_num = 1
    methd_num = 1
    river_num = 1
    cert_num = 1
    fund_num = 1
    obj_num = 1
    data_num = 1
    rep_num = 1

    for obj in project_filter:
        row_num += 1
        all_species_tmp = ""
        all_cu_tmp = ""
        for i in obj.river.all():
            if i.species:
                all_species_tmp += str(i.species.name + ", ")
            if i.cu_name:
                all_cu_tmp += str(i.cu_name.name + ", ")
        funding_year = models.FundingYears.objects.filter(project=obj.id)
        row = [
            obj.agreement_number,
            obj.project_number,

            ", ".join(i.name for i in obj.agreement_history.all()),
            obj.name,
            obj.project_description,
            ", ".join(i.funding_year for i in funding_year),
            obj.start_date,
            obj.end_date,

            obj.area,
            obj.other_species,
            ", ".join(i.name for i in obj.ecosystem_type.all()),
            ", ".join(i.name for i in obj.lake_system.all()),
            ", ".join(i.name for i in obj.watershed.all()),
            obj.other_site_info,

            ", ".join(i.name for i in obj.salmon_life_stage.all()),
            obj.aquaculture_license_number,
            obj.water_license_number,
            ", ".join(i.name for i in obj.hatchery_name.all()),
            obj.DFO_tenure,

            obj.project_stage,
            obj.project_type,
            ", ".join(i.name for i in obj.project_sub_type.all()),
            ", ".join(i.name for i in obj.monitoring_approach.all()),
            ", ".join(i.name for i in obj.project_theme.all()),
            ", ".join(i.name for i in obj.core_component.all()),
            ", ".join(i.name for i in obj.supportive_component.all()),
            ", ".join(i.name for i in obj.project_purpose.all()),
            obj.category_comments,

            obj.DFO_link,
            obj.DFO_program_reference,
            obj.government_organization,
            obj.policy_connection,

            ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
            ", ".join(i.full_name for i in obj.DFO_area_chief.all()),
            ", ".join(i.full_name for i in obj.DFO_IAA.all()),
            ", ".join(i.full_name for i in obj.DFO_resource_manager.all()),
            obj.funding_recipient,
            obj.first_nation.name if obj.first_nation else None,
            obj.contact.full_name if obj.contact else None,
            obj.contact_role,
            ", ".join(i.full_name for i in obj.DFO_technicians.all()),
            obj.contractor,
            obj.contractor_contact,
            ", ".join(i.name for i in obj.partner.all()),
            ", ".join(i.full_name for i in obj.partner_contact.all()),

            obj.agreement_database,
            obj.agreement_comment,
            ", ".join(i.name for i in obj.funding_sources.all()),
            obj.other_funding_sources,
            obj.agreement_type,
            obj.lead_organization,

            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,

        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

        ##########
        # RIVERS #
        for river_tmp in obj.river.all():
            river_num += 1
            river_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                river_tmp.name,
                river_tmp.latitude,
                river_tmp.longitude,
                river_tmp.sub_district_area.name if river_tmp.sub_district_area else None,
                river_tmp.species.name if river_tmp.species else None,
                river_tmp.stock_management_unit.name if river_tmp.stock_management_unit else None,
                river_tmp.cu_index.name if river_tmp.cu_index else None,
                river_tmp.cu_name.name if river_tmp.cu_name else None,
                river_tmp.pop_id if river_tmp.pop_id else None,
                river_tmp.du.name if river_tmp.du else None,
                river_tmp.du_number if river_tmp.du_number else None,

            ]
            for col_num, cell_value in enumerate(river_rows, 1):
                cell = river_worksheet.cell(row=river_num, column=col_num)
                cell.value = cell_value

        ##################
        # FUNDING YEARS #
        for fund in funding_year:
            fund_num += 1
            fund_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                fund.funding_year,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                fund.agreement_cost,
                fund.project_cost,
                fund.date_last_modified,
                fund.last_modified_by.get_full_name() if fund.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(fund_rows, 1):
                cell = funding_worksheet.cell(row=fund_num, column=col_num)
                cell.value = cell_value

        ##########################
        # PROJECT CERTIFIED ROWS #
        project_certified = models.ProjectCertified.objects.filter(project=obj.id)
        for certified in project_certified:
            cert_num += 1
            cert_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                certified.certified_date,
                certified.certified_by.get_full_name() if certified.certified_by else None,
            ]
            for col_num, cell_value in enumerate(cert_rows, 1):
                cell = certified_worksheet.cell(row=cert_num, column=col_num)
                cell.value = cell_value

        ##################
        # OBJECTIVE ROWS #
        objective_filter = models.Objective.objects.filter(project=obj.id)
        for objective in objective_filter:
            obj_num += 1
            if objective.location and objective.location.species:
                obj_species_tmp = objective.location.species.name
            else:
                obj_species_tmp = None
            if objective.location and objective.location.cu_name:
                obj_cu_tmp = objective.location.cu_name.name
            else:
                obj_cu_tmp = None
            objective_row = [
                obj.agreement_number,
                objective.unique_objective,
                obj.project_number,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in obj.funding_sources.all()),
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                objective.location.name if objective.location else None,
                obj_species_tmp,
                obj_cu_tmp,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                objective.task_description,
                objective.element_title,
                objective.activity_title,
                objective.pst_requirement,
                ", ".join(i.name for i in objective.objective_category.all()),
                objective.sil_requirement,
                objective.expected_results,
                objective.dfo_report,
                objective.outcomes_comment,
                objective.date_last_modified,
                objective.last_modified_by.get_full_name() if objective.last_modified_by else None,
            ]

            for col_num, cell_value in enumerate(objective_row, 1):
                cell = objective_worksheet.cell(row=obj_num, column=col_num)
                cell.value = cell_value

            #######################
            # SAMPLE OUTCOME ROWS #
            sample_outcomes = models.SampleOutcome.objects.filter(objective=objective.id)
            for sample in sample_outcomes:
                sampo_num += 1
                sample_rows = [
                    obj.agreement_number,
                    obj.project_number,
                    ", ".join(i.funding_year for i in funding_year.all()),
                    ", ".join(i.name for i in obj.funding_sources.all()),
                    ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                    obj.project_type,
                    ", ".join(i.name for i in obj.project_sub_type.all()),
                    ", ".join(i.name for i in obj.project_theme.all()),
                    obj.area,
                    objective.location.name if objective.location else None,
                    obj_species_tmp,
                    obj_cu_tmp,
                    obj.first_nation.name if obj.first_nation else None,
                    obj.funding_recipient,
                    obj.lead_organization,
                    ", ".join(i.name for i in obj.hatchery_name.all()),
                    sample.unique_objective_number,
                    sample.sampling_outcome,
                    sample.outcome_delivered,
                    sample.outcome_quality,
                    sample.sample_outcome_comment,
                    sample.date_last_modified,
                    sample.last_modified_by.get_full_name() if sample.last_modified_by else None,
                ]
                for col_num, cell_value in enumerate(sample_rows, 1):
                    cell = sample_outcome_worksheet.cell(row=sampo_num, column=col_num)
                    cell.value = cell_value
            #######################
            # REPORT OUTCOME ROWS #
            report_outcomes = models.ReportOutcome.objects.filter(objective=objective.id)
            for report in report_outcomes:
                repo_num += 1
                report_rows = [
                    report.objective.project.agreement_number if report.objective.project else None,
                    obj.project_number,
                    ", ".join(i.funding_year for i in funding_year.all()),
                    ", ".join(i.name for i in obj.funding_sources.all()),
                    ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                    obj.project_type,
                    ", ".join(i.name for i in obj.project_sub_type.all()),
                    ", ".join(i.name for i in obj.project_theme.all()),
                    obj.area,
                    objective.location.name if objective.location else None,
                    obj_species_tmp,
                    obj_cu_tmp,
                    obj.first_nation.name if obj.first_nation else None,
                    obj.funding_recipient,
                    obj.lead_organization,
                    ", ".join(i.name for i in obj.hatchery_name.all()),
                    report.unique_objective_number,
                    report.reporting_outcome,
                    report.outcome_delivered,
                    report.site,
                    report.report_link.document_name if report.report_link else None,
                    report.report_outcome_comment,
                    report.reporting_outcome_metric,
                    report.date_last_modified,
                    report.last_modified_by.get_full_name() if report.last_modified_by else None,
                ]
                for col_num, cell_value in enumerate(report_rows, 1):
                    cell = reporting_outcome_worksheet.cell(row=repo_num, column=col_num)
                    cell.value = cell_value

        #############
        # DATA ROWS #
        data_filter = models.Data.objects.filter(project=obj.id)
        for data in data_filter:
            if data.river and data.river.species:
                data_species_tmp = data.river.species.name
            else:
                data_species_tmp = None
            if data.river and data.river.cu_name:
                data_cu_tmp = data.river.cu_name.name
            else:
                data_cu_tmp = None
            data_num += 1
            data_row = [
                data.project.agreement_number if data.project else None,
                obj.project_number,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in obj.funding_sources.all()),
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                data.river.name if data.river else None,
                data_species_tmp,
                data_cu_tmp,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                data.samples_collected,
                data.samples_collected_comment,
                data.samples_collected_database,
                data.shared_drive,
                data.sample_barrier,
                data.sample_entered_database,
                data.data_quality_check,
                data.sample_format,
                data.data_products,
                data.data_products_database,
                data.data_products_comment,
                data.date_last_modified,
                data.last_modified_by.get_full_name() if data.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(data_row, 1):
                cell = data_worksheet.cell(row=data_num, column=col_num)
                cell.value = cell_value

        ###############
        # METHOD ROWS #
        method_filter = models.Method.objects.filter(project=obj.id)
        for method in method_filter:
            meth_num += 1
            method_row = [
                method.project.agreement_number if method.project else None,
                method.unique_method_number,
                obj.project_number,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in obj.funding_sources.all()),
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                ", ".join(i.name for i in obj.river.all()),
                all_species_tmp,
                all_cu_tmp,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                method.field_work_method_type,
                method.planning_method_type,
                method.sample_processing_method_type,
                method.scale_processing_location,
                method.otolith_processing_location,
                method.DNA_processing_location,
                method.heads_processing_location,
                method.instrument_data_processing_location,
                method.date_last_modified,
                method.last_modified_by.get_full_name() if method.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(method_row, 1):
                cell = method_worksheet.cell(row=meth_num, column=col_num)
                cell.value = cell_value

        ########################
        # METHOD DOCUMENT ROWS #
            method_documents = models.MethodDocument.objects.filter(method=method.id)
            for method_doc in method_documents:
                methd_num += 1
                method_doc_rows = [
                    obj.agreement_number,
                    method_doc.unique_method_number,
                    obj.project_number,
                    ", ".join(i.funding_year for i in funding_year.all()),
                    ", ".join(i.name for i in obj.funding_sources.all()),
                    ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                    obj.project_type,
                    ", ".join(i.name for i in obj.project_sub_type.all()),
                    ", ".join(i.name for i in obj.project_theme.all()),
                    obj.area,
                    ", ".join(i.name for i in obj.river.all()),
                    all_species_tmp,
                    all_cu_tmp,
                    obj.first_nation.name if obj.first_nation else None,
                    obj.funding_recipient,
                    obj.lead_organization,
                    ", ".join(i.name for i in obj.hatchery_name.all()),
                    method_doc.method_document_type,
                    method_doc.authors,
                    method_doc.publication_year,
                    method_doc.title,
                    method_doc.reference_number,
                    method_doc.document_link,
                    method_doc.date_last_modified,
                    method_doc.last_modified_by.get_full_name() if method_doc.last_modified_by else None,
                ]
                for col_num, cell_value in enumerate(method_doc_rows, 1):
                    cell = method_document_worksheet.cell(row=methd_num, column=col_num)
                    cell.value = cell_value

    ###############
    # REPORTS ROWS #
        reports_filter = models.Reports.objects.filter(project=obj.id)
        for report in reports_filter:
            rep_num += 1
            report_row = [
                report.project.agreement_number if report.project else None,
                obj.project_number,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in obj.funding_sources.all()),
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                ", ".join(i.name for i in obj.river.all()),
                all_species_tmp,
                all_cu_tmp,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                report.report_timeline,
                report.report_type,
                report.report_concerns,
                report.document_name,
                report.document_author,
                report.document_reference_information,
                report.document_link,
                report.published,
                report.date_last_modified,
                report.last_modified_by.get_full_name() if report.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(report_row, 1):
                cell = report_worksheet.cell(row=rep_num, column=col_num)
                cell.value = cell_value

    workbook.save(response)
    return response


def export_project(request):
    project = models.Project.objects.all()
    project_filter = filters.ProjectFilter(request.GET, queryset=project).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Projects.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Projects'

    columns = [
        'Agreement Number',
        'Project Number',

        'Agreement History',
        'Project Name',
        'Project Description',
        'Funding Year',
        'Start Date',
        'End Date',

        'Area',
        'Other Species',
        'Ecosystem Type',
        'Lake System(s)',
        'Watershed(s)',
        'Other Site Info',

        'Salmon Life Stage',
        'Aquaculture License Number',
        'Water License Number',
        'Hatchery Name',
        'DFO Tenure',

        'Project Stage',
        'Project Type',
        'Project Sub Type',
        'Monitoring Approach',
        'Project Theme',
        'Core Component',
        'Supportive Component',
        'Project Purpose',
        'Category Comments',

        'Link to other DFO Programs',
        'Linked DFO Program Project Reference',
        'Link to other Government Departments',
        'Policy Connections',

        'DFO Project Authority',
        'DFO Area Chief',
        'DFO IAA',
        'DFO Resource Manager',
        'Funding Recipient',
        'First Nation/Tribal Council',
        'Contact',
        'Contact Role',
        'DFO Technicians/Biologists',
        'Contractors',
        'Contractor Contact',
        'Partner',
        'Partner Contact',

        'Agreement Database',
        'Agreement Comment',
        'Funding Sources',
        'Other Funding Sources',
        'Agreement Type',
        'Project Lead Organization',

        'date_last_modified',
        'last_modified_by',


    ]
    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    ##############################
    # Rivers SHEET/HEADER #
    river_worksheet = workbook.create_sheet("Rivers", 2)
    river_columns = [
        'Agreement Number',
        'Project Number',
        'Project Name',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Name',
        'Latitude',
        'Longitude',
        'Sub District Area',
        'Species',
        'Stock Management Unit',
        'CU index',
        'CU Name',
        'Pop ID',
        'DU',
        'DU Number',
    ]
    row_num = 1
    for col_num, column_title in enumerate(river_columns, 1):
        river_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = river_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title


    ###########
    # FUNDING #
    funding_worksheet = workbook.create_sheet("Funding", 1)
    funding_columns = [
        'Agreement Number',
        'Project Number',
        'Project Name',
        'Funding Year',
        'Project Authority',
        'First Nation',
        'Funding Recipient',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Agreement Cost',
        'Project Cost',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1
    for col_num, column_title in enumerate(funding_columns, 1):
        funding_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = funding_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    #############
    # CERTIFIED #
    certified_worksheet = workbook.create_sheet("Project Certified", 3)
    certified_columns = [
        'Agreement Number',
        'Project Number',
        'Project Name',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Certified Date',
        'Certified By',
    ]
    row_num = 1
    for col_num, column_title in enumerate(certified_columns, 1):
        certified_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = certified_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    fund_num = 1
    cert_num = 1
    river_num = 1

    # PROJECT ROWS #
    for obj in project_filter:
        row_num += 1
        funding_year = models.FundingYears.objects.filter(project=obj.id)
        row = [
            obj.agreement_number,
            obj.project_number,

            ", ".join(i.name for i in obj.agreement_history.all()),
            obj.name,
            obj.project_description,
            ", ".join(i.funding_year for i in funding_year),
            obj.start_date,
            obj.end_date,

            obj.area,
            obj.other_species,
            ", ".join(i.name for i in obj.ecosystem_type.all()),
            ", ".join(i.name for i in obj.lake_system.all()),
            ", ".join(i.name for i in obj.watershed.all()),
            obj.other_site_info,

            ", ".join(i.name for i in obj.salmon_life_stage.all()),
            obj.aquaculture_license_number,
            obj.water_license_number,
            ", ".join(i.name for i in obj.hatchery_name.all()),
            obj.DFO_tenure,

            obj.project_stage,
            obj.project_type,
            ", ".join(i.name for i in obj.project_sub_type.all()),
            ", ".join(i.name for i in obj.monitoring_approach.all()),
            ", ".join(i.name for i in obj.project_theme.all()),
            ", ".join(i.name for i in obj.core_component.all()),
            ", ".join(i.name for i in obj.supportive_component.all()),
            ", ".join(i.name for i in obj.project_purpose.all()),
            obj.category_comments,

            obj.DFO_link,
            obj.DFO_program_reference,
            obj.government_organization,
            obj.policy_connection,

            ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
            ", ".join(i.full_name for i in obj.DFO_area_chief.all()),
            ", ".join(i.full_name for i in obj.DFO_IAA.all()),
            ", ".join(i.full_name for i in obj.DFO_resource_manager.all()),
            obj.funding_recipient,
            obj.first_nation.name if obj.first_nation else None,
            obj.contact.full_name if obj.contact else None,
            obj.contact_role,
            ", ".join(i.full_name for i in obj.DFO_technicians.all()),
            obj.contractor,
            obj.contractor_contact,
            ", ".join(i.name for i in obj.partner.all()),
            ", ".join(i.full_name for i in obj.partner_contact.all()),

            obj.agreement_database,
            obj.agreement_comment,
            ", ".join(i.name for i in obj.funding_sources.all()),
            obj.other_funding_sources,
            obj.agreement_type,
            obj.lead_organization,

            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,

        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

        ##############
        # RIVER ROWS #
        for river_tmp in obj.river.all():
            river_num += 1
            river_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.lead_organization,
                ", ".join(i.name for i in obj.hatchery_name.all()),
                river_tmp.name if river_tmp.name else None,
                river_tmp.latitude if river_tmp.latitude else None,
                river_tmp.longitude if river_tmp.longitude else None,
                river_tmp.sub_district_area.name if river_tmp.sub_district_area else None,
                river_tmp.species.name if river_tmp.species else None,
                river_tmp.stock_management_unit.name if river_tmp.stock_management_unit else None,
                river_tmp.cu_index.name if river_tmp.cu_index else None,
                river_tmp.cu_name.name if river_tmp.cu_name else None,
                river_tmp.pop_id if river_tmp.pop_id else None,
                river_tmp.du.name if river_tmp.du else None,
                river_tmp.du_number if river_tmp.du_number else None,
            ]
            for col_num, cell_value in enumerate(river_rows, 1):
                cell = river_worksheet.cell(row=river_num, column=col_num)
                cell.value = cell_value

            # FUNDING ROWS #
        funding_years = models.FundingYears.objects.filter(project=obj.id)
        for fund in funding_years:
            fund_num += 1
            fund_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                fund.funding_year,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.first_nation.name if obj.first_nation else None,
                obj.funding_recipient,
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                fund.agreement_cost,
                fund.project_cost,
                fund.date_last_modified,
                fund.last_modified_by.get_full_name() if fund.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(fund_rows, 1):
                cell = funding_worksheet.cell(row=fund_num, column=col_num)
                cell.value = cell_value

        # CERTIFIED ROWS #
        project_certified = models.ProjectCertified.objects.filter(project=obj.id)
        for certified in project_certified:
            cert_num += 1
            cert_rows = [
                obj.agreement_number,
                obj.project_number,
                obj.name,
                ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
                obj.project_type,
                ", ".join(i.name for i in obj.project_sub_type.all()),
                ", ".join(i.name for i in obj.project_theme.all()),
                obj.area,
                certified.certified_date,
                certified.certified_by.get_full_name() if certified.certified_by else None,
            ]
            for col_num, cell_value in enumerate(cert_rows, 1):
                cell = certified_worksheet.cell(row=cert_num, column=col_num)
                cell.value = cell_value

    workbook.save(response)

    return response


def export_objective(request):
    objective = models.Objective.objects.all()
    objective_filter = filters.ObjectiveFilter(request.GET, queryset=objective).qs
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-Objectives.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Objectives'

    columns = [
        'Agreement Number',
        'Unique Objective',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Task Description',
        'Element Title',
        'Activity Title',
        'PST Requirement Identified?',
        'Objective Category',
        'SIL Requirement',
        'Expected Result(s)',
        'Products/Reports to Provide DFO',
        'Outcome Comment',
        'date_last_modified',
        'last_modified_by',

    ]
    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    # Sample Outcome #
    sample_outcome_worksheet = workbook.create_sheet("Sample Outcomes", 1)
    sample_outcomes_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Unique Objective Number',
        'Sampling Outcome',
        'Were outcomes delivered?',
        'Quality of Outcome',
        'Sample Outcome Comment',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(sample_outcomes_columns, 1):
        sample_outcome_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = sample_outcome_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    # Reporting Outcome #
    reporting_outcome_worksheet = workbook.create_sheet("Report Outcomes", 2)
    report_outcomes_columns = [
        'Agreement Number',
        'Project Number',
        'Funding Year',
        'Funding Source',
        'Project Authority',
        'Project Type',
        'Project SubType',
        'Project Theme',
        'Area',
        'Location/River',
        'Species',
        'CU Name',
        'First Nations',
        'Funding Recipient',
        'Lead Organization',
        'Hatchery',
        'Unique Objective Number',
        'Reporting Outcome',
        'Was the outcome deliverable met?',
        'Site',
        'Report Link',
        'Reporting Outcome Comment',
        'Reporting Outcome Metric',
        'date_last_modified',
        'last_modified_by',
    ]
    row_num = 1

    for col_num, column_title in enumerate(report_outcomes_columns, 1):
        reporting_outcome_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = reporting_outcome_worksheet.cell(row=row_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    samp_num = 1
    row_num = 1
    rep_num = 1
    for obj in objective_filter:
        row_num += 1
        proj = models.Project.objects.get(pk=obj.project.id)
        if obj.location and obj.location.species:
            species_tmp = obj.location.species.name
        else:
            species_tmp = None
        if obj.location and obj.location.cu_name:
            cu_tmp = obj.location.cu_name.name
        else:
            cu_tmp = None

        funding_year = models.FundingYears.objects.filter(project=obj.project.id)
        row = [
            proj.agreement_number if proj else None,
            obj.unique_objective,
            proj.project_number if proj else None,
            ", ".join(i.funding_year for i in funding_year.all()),
            ", ".join(i.name for i in proj.funding_sources.all()),
            ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
            proj.project_type if proj else None,
            ", ".join(i.name for i in proj.project_sub_type.all()),
            ", ".join(i.name for i in proj.project_theme.all()),
            proj.area if proj else None,
            obj.location.name if obj.location else None,
            species_tmp,
            cu_tmp,
            proj.first_nation.name if proj.first_nation else None,
            proj.funding_recipient if proj else None,
            proj.lead_organization if proj else None,
            ", ".join(i.name for i in proj.hatchery_name.all()),
            obj.task_description,
            obj.element_title,
            obj.activity_title,
            obj.pst_requirement,
            ", ".join(i.name for i in obj.objective_category.all()),
            obj.sil_requirement,
            obj.expected_results,
            obj.dfo_report,
            obj.outcomes_comment,
            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,

        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

        ##################
        # SAMPLE OUTCOME #
        sample_outcomes = models.SampleOutcome.objects.filter(objective=obj.id)
        for sample in sample_outcomes:
            samp_num += 1
            sample_rows = [
                proj.agreement_number if proj else None,
                proj.project_number if proj else None,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in proj.funding_sources.all()),
                ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
                proj.project_type if proj else None,
                ", ".join(i.name for i in proj.project_sub_type.all()),
                ", ".join(i.name for i in proj.project_theme.all()),
                proj.area if proj else None,
                obj.location.name if obj.location else None,
                species_tmp,
                cu_tmp,
                proj.first_nation.name if proj.first_nation else None,
                proj.funding_recipient if proj else None,
                proj.lead_organization if proj else None,
                ", ".join(i.name for i in proj.hatchery_name.all()),
                sample.unique_objective_number,
                sample.sampling_outcome,
                sample.outcome_delivered,
                sample.outcome_quality,
                sample.sample_outcome_comment,
                sample.date_last_modified,
                sample.last_modified_by.get_full_name() if sample.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(sample_rows, 1):
                cell = sample_outcome_worksheet.cell(row=samp_num, column=col_num)
                cell.value = cell_value

        report_outcomes = models.ReportOutcome.objects.filter(objective=obj.id)
        for report in report_outcomes:
            rep_num += 1
            report_rows = [
                proj.agreement_number if proj else None,
                proj.project_number if proj else None,
                ", ".join(i.funding_year for i in funding_year.all()),
                ", ".join(i.name for i in proj.funding_sources.all()),
                ", ".join(i.full_name for i in proj.DFO_project_authority.all()),
                proj.project_type if proj else None,
                ", ".join(i.name for i in proj.project_sub_type.all()),
                ", ".join(i.name for i in proj.project_theme.all()),
                proj.area if proj else None,
                obj.location.name if obj.location else None,
                species_tmp,
                cu_tmp,
                proj.first_nation.name if proj.first_nation else None,
                proj.funding_recipient if proj else None,
                proj.lead_organization if proj else None,
                ", ".join(i.name for i in proj.hatchery_name.all()),
                report.unique_objective_number,
                report.reporting_outcome,
                report.outcome_delivered,
                report.site,
                report.report_link.document_name if report.report_link else None,
                report.report_outcome_comment,
                report.reporting_outcome_metric,
                report.date_last_modified,
                report.last_modified_by.get_full_name() if report.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(report_rows, 1):
                cell = reporting_outcome_worksheet.cell(row=rep_num, column=col_num)
                cell.value = cell_value

    workbook.save(response)

    return response