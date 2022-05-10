from django.http import HttpResponse
from . import models
from . import filters
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.utils.cell import get_column_letter

green = 'C4D79B'


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
        'Start Date',
        'End Date',

        'Area',
        'Other Species',
        'Ecosystem Type',
        'Lake System(s)',
        'Watershed(s)',
        'Management Area',

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
        'Policy and Program Connection',

        'DFO Project Authority',
        'DFO Area Chief',
        'DFO AAA',
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

    fund_num = 1
    cert_num = 1
    river_num = 1
    for obj in project_filter:
        row_num += 1

        row = [
            obj.agreement_number,
            obj.project_number,

            ", ".join(i.name for i in obj.agreement_history.all()),
            obj.name,
            obj.project_description,
            obj.start_date,
            obj.end_date,

            obj.area,
            obj.other_species,
            ", ".join(i.name for i in obj.ecosystem_type.all()),
            ", ".join(i.name for i in obj.lake_system.all()),
            ", ".join(i.name for i in obj.watershed.all()),
            ", ".join(i.name for i in obj.management_area.all()),

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
            obj.policy_program_connection,

            ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
            ", ".join(i.full_name for i in obj.DFO_area_chief.all()),
            ", ".join(i.full_name for i in obj.DFO_AAA.all()),
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
                river_tmp.name if river_tmp.name else None,
                river_tmp.latitude if river_tmp.latitude else None,
                river_tmp.longitude if river_tmp.longitude else None,
                river_tmp.sub_district_area if river_tmp.sub_district_area else None,
                river_tmp.species.name if river_tmp.species else None,
                river_tmp.stock_management_unit if river_tmp.stock_management_unit else None,
                river_tmp.cu_index.name if river_tmp.cu_index else None,
                river_tmp.cu_name.name if river_tmp.cu_name else None,
                river_tmp.pop_id if river_tmp.pop_id else None,
                river_tmp.du if river_tmp.du else None,
                river_tmp.du_number if river_tmp.du_number else None,
            ]
            for col_num, cell_value in enumerate(river_rows, 1):
                cell = river_worksheet.cell(row=river_num, column=col_num)
                cell.value = cell_value

    # Funding #
    funding_worksheet = workbook.create_sheet("Funding", 1)
    funding_columns = [
        'Agreement Number',
        'Funding Year',
        'Agreement Cost',
        'Project Cost',
        'date_last_modified',
        'last_modified_by',
    ]

    for col_num, column_title in enumerate(funding_columns, 1):
        funding_worksheet.column_dimensions[get_column_letter(col_num)].width = 15
        cell = funding_worksheet.cell(row=fund_num, column=col_num)
        cell.fill = PatternFill(start_color=green, end_color=green, fill_type="solid")
        cell.font = Font(bold=True, size=12)
        cell.value = column_title

    for obj in project_filter:
        funding_years = models.FundingYears.objects.filter(project=obj.id)
        for fund in funding_years:
            fund_num += 1
            fund_rows = [
                fund.project.agreement_number if fund.project else None,
                fund.funding_year,
                fund.agreement_cost,
                fund.project_cost,
                fund.date_last_modified,
                fund.last_modified_by.get_full_name() if fund.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(fund_rows, 1):
                cell = funding_worksheet.cell(row=fund_num, column=col_num)
                cell.value = cell_value

    certified_worksheet = workbook.create_sheet("Project Certified", 3)
    certified_columns = [
        'Agreement Number',
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

    for obj in project_filter:
        project_certified = models.ProjectCertified.objects.filter(project=obj.id)
        for certified in project_certified:
            cert_num += 1
            cert_rows = [
                certified.project.agreement_number if certified.project else None,
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
        'Task Description',
        'Element Title',
        'Activity Title'
        'PST Requirement Identified?',
        'Location',
        'Objective Category',
        'Species',
        'SIL Requirement',
        'Expected Result(s)',
        'Products/Reports to Provide DFO',
        'Outcomes Contact',
        'Outcome Comment',
        'Barrier to Achieve Outcomes(?)',
        'What capacity building did this project provide?',
        'Key Lessons Learned',
        'Missed Opportunities',
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

    for obj in objective_filter:
        row_num += 1

        row = [
            obj.project.agreement_number if obj.project else None,
            obj.unique_objective,
            obj.task_description,
            obj.element_title,
            obj.activity_title,
            obj.pst_requirement,
            obj.location.name if obj.location else None,
            ", ".join(i.name for i in obj.objective_category.all()),
            obj.location.species.name if obj.location else None,
            obj.sil_requirement,
            obj.expected_results,
            obj.dfo_report,
            obj.outcomes_contact.full_name if obj.outcomes_contact else None,
            obj.outcomes_comment,
            ", ".join(i.name for i in obj.outcome_barrier.all()),
            ", ".join(i.name for i in obj.capacity_building.all()),
            obj.key_lesson,
            obj.missed_opportunities,
            obj.date_last_modified,
            obj.last_modified_by.get_full_name() if obj.last_modified_by else None,

        ]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    # Sample Outcome #
    sample_outcome_worksheet = workbook.create_sheet("Sample Outcomes", 1)

    sample_outcomes_columns = [
        'Agreement Number',
        'Unique Objective Number',
        'Sampling Outcome',
        'Was the Sampling Outcome Met?',
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

    for obj in objective_filter:
        sample_outcomes = models.SampleOutcome.objects.filter(objective=obj.id)
        for sample in sample_outcomes:
            row_num += 1
            sample_rows = [
                sample.objective.project.agreement_number if sample.objective.project else None,
                sample.unique_objective_number,
                sample.sampling_outcome,
                sample.outcome_delivered,
                sample.outcome_quality,
                sample.sample_outcome_comment,
                sample.date_last_modified,
                sample.last_modified_by.get_full_name() if sample.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(sample_rows, 1):
                cell = sample_outcome_worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value

    # Reporting Outcome #
    reporting_outcome_worksheet = workbook.create_sheet("Report Outcomes", 2)

    report_outcomes_columns = [
        'Agreement Number',
        'Unique Objective Number',
        'Reporting Outcome',
        'Was the outcome deliverable met?',
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

    for obj in objective_filter:
        report_outcomes = models.ReportOutcome.objects.filter(objective=obj.id)
        for report in report_outcomes:
            row_num += 1
            report_rows = [
                report.objective.project.agreement_number if report.objective.project else None,
                report.unique_objective_number,
                report.reporting_outcome,
                report.outcome_delivered,
                report.report_link.document_name if report.report_link else None,
                report.report_outcome_comment,
                report.reporting_outcome_metric,
                report.date_last_modified,
                report.last_modified_by.get_full_name() if report.last_modified_by else None,
            ]
            for col_num, cell_value in enumerate(report_rows, 1):
                cell = reporting_outcome_worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value

    workbook.save(response)

    return response


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
        'River',
        'Species',
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
        row_num += 1
        row = [
            obj.project.agreement_number if obj.project else None,
            obj.river.name if obj.river else None,
            obj.river.species.name if obj.river else None,
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
        'Unique Method Number'
        'Field Work Methods Type',
        'Planning Method Type',
        'Sample Processing Method Type',
        'Traditional Ecological Knowledge Consideration',
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

    for obj in method_filter:
        row_num += 1
        row = [
            obj.project.agreement_number if obj.project else None,
            obj.unique_method_number,
            obj.field_work_method_type,
            obj.planning_method_type,
            obj.sample_processing_method_type,
            obj.knowledge_consideration,
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

    method_document_worksheet = workbook.create_sheet("Method Document", 1)

    method_document_columns = [
        'Agreement Number',
        'Unique Method Number',
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

    for obj in method_filter:
        method_documents = models.MethodDocument.objects.filter(method=obj.id)
        for method in method_documents:
            row_num += 1
            method_rows = [
                method.method.project.agreement_number if method.method.project else None,
                method.unique_method_number,
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
                cell = method_document_worksheet.cell(row=row_num, column=col_num)
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
        row_num += 1
        row = [
            obj.project.agreement_number if obj.project else None,
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
        'Start Date',
        'End Date',

        'Area',
        'Other Species',
        'Ecosystem Type',
        'Lake System(s)',
        'Watershed(s)',
        'Management Area',

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
        'Policy and Program Connection',

        'DFO Project Authority',
        'DFO Area Chief',
        'DFO AAA',
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
        'Funding Year',
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
        'Task Description',
        'Element Title',
        'Activity Title'
        'PST Requirement Identified?',
        'Location',
        'Objective Category',
        'Species',
        'SIL Requirement',
        'Expected Result(s)',
        'Products/Reports to Provide DFO',
        'Outcomes Contact',
        'Outcome Comment',
        'Barrier to Achieve Outcomes(?)',
        'What capacity building did this project provide?',
        'Key Lessons Learned',
        'Missed Opportunities',
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
        'Unique Objective Number',
        'Sampling Outcome',
        'Was the Sampling Outcome Met?',
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
        'Unique Objective Number',
        'Reporting Outcome',
        'Was the outcome deliverable met?',
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
        'River',
        'Species',
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
        'Unique Method Number'
        'Field Work Methods Type',
        'Planning Method Type',
        'Sample Processing Method Type',
        'Traditional Ecological Knowledge Consideration',
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
        'Unique Method Number'
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
    methd_num = 1
    river_num = 1
    cert_num = 1

    for obj in project_filter:
        row_num += 1
        row = [
            obj.agreement_number,
            obj.project_number,

            ", ".join(i.name for i in obj.agreement_history.all()),
            obj.name,
            obj.project_description,
            obj.start_date,
            obj.end_date,

            obj.area,
            obj.other_species,
            ", ".join(i.name for i in obj.ecosystem_type.all()),
            ", ".join(i.name for i in obj.lake_system.all()),
            ", ".join(i.name for i in obj.watershed.all()),
            ", ".join(i.name for i in obj.management_area.all()),

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
            obj.policy_program_connection,

            ", ".join(i.full_name for i in obj.DFO_project_authority.all()),
            ", ".join(i.full_name for i in obj.DFO_area_chief.all()),
            ", ".join(i.full_name for i in obj.DFO_AAA.all()),
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
                river_tmp.name if river_tmp.name else None,
                river_tmp.latitude if river_tmp.latitude else None,
                river_tmp.longitude if river_tmp.longitude else None,
                river_tmp.sub_district_area if river_tmp.sub_district_area else None,
                river_tmp.species.name if river_tmp.species else None,
                river_tmp.stock_management_unit if river_tmp.stock_management_unit else None,
                river_tmp.cu_index.name if river_tmp.cu_index else None,
                river_tmp.cu_name.name if river_tmp.cu_name else None,
                river_tmp.pop_id if river_tmp.pop_id else None,
                river_tmp.du if river_tmp.du else None,
                river_tmp.du_number if river_tmp.du_number else None,

            ]
            for col_num, cell_value in enumerate(river_rows, 1):
                cell = river_worksheet.cell(row=river_num, column=col_num)
                cell.value = cell_value



    ##################
    # FUNDING YEARS #
    fund_num = 1
    for obj in project_filter:
        funding_years = models.FundingYears.objects.filter(project=obj.id)
        for fund in funding_years:
            fund_num += 1
            fund_rows = [
                fund.project.agreement_number if fund.project else None,
                fund.funding_year,
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
    cert_num = 1
    for obj in project_filter:
        project_certified = models.ProjectCertified.objects.filter(project=obj.id)
        for certified in project_certified:
            cert_num += 1
            cert_rows = [
                certified.project.agreement_number if certified.project else None,
                certified.certified_date,
                certified.certified_by.get_full_name() if certified.certified_by else None,
            ]
            for col_num, cell_value in enumerate(cert_rows, 1):
                cell = certified_worksheet.cell(row=cert_num, column=col_num)
                cell.value = cell_value

    ##################
    # OBJECTIVE ROWS #
    obj_num = 1
    for obj in project_filter:
        objective_filter = models.Objective.objects.filter(project=obj.id)
        for objective in objective_filter:
            obj_num += 1
            objective_row = [
                objective.project.agreement_number if objective.project else None,
                objective.unique_objective,
                objective.task_description,
                objective.element_title,
                objective.activity_title,
                objective.pst_requirement,
                objective.location.name if objective.location else None,
                ", ".join(i.name for i in objective.objective_category.all()),
                objective.location.species.name if objective.location else None,
                objective.sil_requirement,
                objective.expected_results,
                objective.dfo_report,
                objective.outcomes_contact.full_name if objective.outcomes_contact else None,
                objective.outcomes_comment,
                ", ".join(i.name for i in objective.outcome_barrier.all()),
                ", ".join(i.name for i in objective.capacity_building.all()),
                objective.key_lesson,
                objective.missed_opportunities,
                objective.date_last_modified,
                objective.last_modified_by.get_full_name() if objective.last_modified_by else None,
            ]

            for col_num, cell_value in enumerate(objective_row, 1):
                cell = objective_worksheet.cell(row=obj_num, column=col_num)
                cell.value = cell_value

        #######################
        # SAMPLE OUTCOME ROWS #

        for sampo_out in objective_filter:
            sample_outcomes = models.SampleOutcome.objects.filter(objective=sampo_out.id)
            for sample in sample_outcomes:
                sampo_num += 1
                sample_rows = [
                    sample.objective.project.agreement_number if sample.objective.project else None,
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
        for repo_out in objective_filter:
            report_outcomes = models.ReportOutcome.objects.filter(objective=repo_out.id)
            for report in report_outcomes:
                repo_num += 1
                report_rows = [
                    report.objective.project.agreement_number if report.objective.project else None,
                    report.unique_objective_number,
                    report.reporting_outcome,
                    report.outcome_delivered,
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
    data_num = 1
    for obj in project_filter:
        data_filter = models.Data.objects.filter(project=obj.id)
        for data in data_filter:
            data_num += 1
            data_row = [
                data.project.agreement_number if data.project else None,
                data.river.name if data.river else None,
                data.river.species.name if data.river else None,
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
    meth_num = 1
    for obj in project_filter:
        method_filter = models.Method.objects.filter(project=obj.id)
        for method in method_filter:
            meth_num += 1
            method_row = [
                method.project.agreement_number if method.project else None,
                method.unique_method_number,
                method.field_work_method_type,
                method.planning_method_type,
                method.sample_processing_method_type,
                method.knowledge_consideration,
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

        for method in method_filter:
            method_documents = models.MethodDocument.objects.filter(method=method.id)
            for method_doc in method_documents:
                methd_num += 1
                method_doc_rows = [
                    method_doc.method.project.agreement_number if method_doc.method.project else None,
                    method_doc.unique_method_number,
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
    rep_num = 1
    for obj in project_filter:
        reports_filter = models.Reports.objects.filter(project=obj.id)
        for report in reports_filter:
            rep_num += 1
            report_row = [
                report.project.agreement_number if report.project else None,
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