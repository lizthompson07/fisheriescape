from . import models
import csv
import os
from dm_apps import settings
from . import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def import_watershed():
    path = os.path.join('/Users/orpenr/Desktop/import', 'watersheds.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if models.Watershed.objects.filter(name__exact=row['name']) or row['name'] == "":
                continue
            else:
                created, _ = models.Watershed.objects.get_or_create(
                    group_code=row['group_code'],
                    name=row['name'],
                )


def import_rivers():
    path = os.path.join('/Users/orpenr/Desktop/import', 'rivers_finals.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['SPECIES_QUALIFIED'] and row['SPECIES_QUALIFIED'] != "":
                species_tmp, _ = models.Species.objects.get_or_create(name=row['SPECIES_QUALIFIED'])
            else:
                species_tmp = None

            if row['FULL_CU_IN'] and row['FULL_CU_IN'] != "":
                cu_index_tmp, _ = models.CUIndex.objects.get_or_create(name=row['FULL_CU_IN'])
            else:
                cu_index_tmp = None

            if row['CU_NAME'] and row['CU_NAME'] != "":
                cu_name_tmp, _ = models.CUName.objects.get_or_create(name=row['CU_NAME'])
            else:
                cu_name_tmp = None

            if row['DU'] and row['DU'] != "":
                du_name_tmp, _ = models.DU.objects.get_or_create(name=row['DU'])
            else:
                du_name_tmp = None

            if row['SMU'] and row['SMU'] != "":
                SMU_name_tmp, _ = models.StockManagementUnit.objects.get_or_create(name=row['SMU'])
            else:
                SMU_name_tmp = None

            if row['AREA'] and row['AREA'] != "":
                area_name_tmp, _ = models.SubDistrictArea.objects.get_or_create(name=row['AREA'])
            else:
                area_name_tmp = None

            if row['X_LONGT'] == "Unknown":
                long_tmp = None
            else:
                long_tmp = row['X_LONGT']

            if row['Y_LAT'] == "Unknown":
                lat_tmp = None
            else:
                lat_tmp = row['Y_LAT']

            if row['POP_ID'] == "Unknown":
                pop_tmp = None
            else:
                pop_tmp = row['POP_ID']

            if models.River.objects.filter(name=row['SYSTEM_SITE'], sub_district_area_id=int(area_name_tmp.id), species_id=int(species_tmp.id), popid=pop_tmp):
                continue


            created, _ = models.River.objects.get_or_create(
                name=row['SYSTEM_SITE'],
                longitude=long_tmp,
                latitude=lat_tmp,
                sub_district_area_id=int(area_name_tmp.id) if species_tmp else None,
                species_id=int(species_tmp.id) if species_tmp else None,
                cu_index_id=int(cu_index_tmp.id) if cu_index_tmp else None,
                cu_name_id=int(cu_name_tmp.id) if cu_name_tmp else None,
                stock_management_unit_id=int(SMU_name_tmp.id) if SMU_name_tmp else None,
                popid=pop_tmp,
                du_id=int(du_name_tmp.id) if du_name_tmp else None,
                du_number=row['DU Number'],

            )


def import_generic(file_name, model_name, row_name):
    path = os.path.join('/Users/orpenr/Desktop/import', file_name)
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if model_name.objects.filter(name__exact=row[row_name]) or row[row_name] == "":
                continue
            else:
                created, _ = model_name.objects.get_or_create(
                    name=row[row_name].strip(),
                )


def import_all():
    import_generic('lake_systems.csv', models.LakeSystem, 'lake_systems')
    import_generic('drop_downs.csv', models.Species, 'Species')
    import_generic('rivers_finals.csv', models.CUIndex, 'FULL_CU_IN')
    import_generic('rivers_finals.csv', models.CUName, 'CU_NAME')
    import_generic('drop_downs.csv', models.FirstNations, 'First Nations')
    import_generic('drop_downs.csv', models.SalmonLifeStage, 'Salmon Life Stage')
    import_generic('drop_downs.csv', models.ProjectSubType, 'Project Sub-Type')
    import_generic('drop_downs.csv', models.ProjectTheme, 'Project Theme')
    import_generic('drop_downs.csv', models.CoreComponent, 'Project Core Element')
    import_generic('drop_downs.csv', models.SupportiveComponent, 'Project Supportive Element')
    import_generic('drop_downs.csv', models.ProjectPurpose, 'Project Purpose')
    import_generic('drop_downs.csv', models.FundingSources, 'Funding Sources')
    import_generic('drop_downs.csv', models.ObjectiveCategory, 'Objective Category')
    import_generic('drop_downs.csv', models.CapacityBuilding, 'What capacity building did this project provide?')
    import_generic('drop_downs.csv', models.OutComeBarrier, 'Barrier to achieving outcomes?')
    import_generic('drop_downs.csv', models.HatcheryName, 'Hatchery Name')
    import_generic('drop_downs.csv', models.ManagementArea, 'Pacific Fisheries Management Area')
    import_generic('drop_downs.csv', models.EcosystemType, 'Ecosystem Type')
    import_generic('drop_downs.csv', models.MonitoringApproach, 'Monitoring Approach')
    import_watershed()
    import_rivers()
    import_organization()
    import_person()
    import_project()
    project_river()
    import_costing()
    import_objective()
    import_report()
    import_data()
    import_method()
    import_reporting_outcome()
    import_sample_outcome()
    #import_method_document()


def import_organization():
    path = os.path.join('/Users/orpenr/Desktop/import', 'organizations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if models.Organization.objects.filter(name__iexact=row['Organization Name']) or row['Organization Name'] == "":
                continue
            else:
                created, _ = models.Organization.objects.get_or_create(
                    name=row['Organization Name'],
                    is_active=row['Is Active'],
                    organization_type=row['Organization Type'],
                    section=row['Section'],
                    address=row['Address'],
                    city=row['City'],
                    province_state=row['Province/State'],
                    country=row['Country'],
                    phone=row['Phone'],
                    email=row['Primary email'],
                    website=row['Website']
                )


def import_person():
    path = os.path.join('/Users/orpenr/Desktop/import', 'persons.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or models.Person.objects.filter(first_name__iexact=row['First name'], last_name__iexact=row['Last name']):
                continue
            else:
                created, _ = models.Person.objects.get_or_create(
                    is_active=row['Is Active'],
                    last_name=row['Last name'],
                    first_name=row['First name'],
                    phone=row['Work phone'],
                    email=row['Work email'],
                    city=row['Office location - city'],
                    province_state=row['Office location - state/province'],
                    country=row['Office Location'],
                    section=row['Section'],
                    role=row['Role'],
                    other_membership=row['Other membership'],
                )
                many_var(row['Primary Organization'], created.organizations, models.Organization)


def import_project():
    path = os.path.join('/Users/orpenr/Desktop/import', 'projects.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue

            if row['Project Start Date'] == "" or row['Project Start Date'] == "NA":
                tmp_start = None
            else:
                tmp_start = row['Project Start Date']

            if row['Project End Date'] == "" or row['Project End Date'] == "NA":
                tmp_end = None
            else:
                tmp_end = row['Project End Date']

            if row['First Nations'] and row['First Nations'] != "":
                first_nations_tmp, _ = models.FirstNations.objects.get_or_create(name=row['First Nations'])
            else:
                first_nations_tmp = None

            if row['Contact'] and row['Contact'] != "":
                tmp_whole_name = row['Contact'].split(' ')
                tmp_first_name = tmp_whole_name[0].strip()
                if len(tmp_whole_name) > 1:
                    tmp_last_name = tmp_whole_name[1].strip()
                else:
                    tmp_last_name = None
                contact_tmp, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
            else:
                contact_tmp = None

            created, _ = models.Project.objects.get_or_create(
                project_number=row['Project Number'],
                agreement_number=row['Agreement Number'],
                name=row['Project Name'],
                project_description=row['Project Description'],
                start_date=tmp_start,
                end_date=tmp_end,
                area=row['Area'],
                other_species=row['Other Species'],
                project_type=row['Project_Type'],
                project_stage=row['Project Stage'],
                category_comments=row['Category Comments'],
                DFO_link=row['Links to other DFO Programs'],
                funding_recipient=row['Funding Recipient'],
                aquaculture_license_number=row['Aquaculture License Number'],
                water_license_number=row['Water License Number'],
                DFO_tenure=row['DFO Tenure'],
                DFO_program_reference=row['Linked DFO Program Project Reference'],
                government_organization=row['Links to other Government Departments'],
                policy_connection=row['Policy and Program Connections'],
                first_nation_id=int(first_nations_tmp.id) if first_nations_tmp else None,
                contact_id=int(contact_tmp.id) if contact_tmp else None,
                contact_role=row['Contact Role'],
                contractor=row['Contractors'],
                contractor_contact=row['Contractors Primary Contact'],
                agreement_database=row['Agreement Database'],
                agreement_comment=row['Agreement Comment'],
                other_funding_sources=row['Other Funding Sources'],
                agreement_type=row['Agreement Type'],
                lead_organization=row['Lead Organization'],
                #other_site_info=row['other site info],
            )
            many_var(row['Agreement History'], created.agreement_history, models.Project)
            many_var(row['Hatchery Name'], created.hatchery_name, models.HatcheryName)
            many_var(row['Monitoring_Approach'], created.monitoring_approach, models.MonitoringApproach)
            many_var(row['Ecosystem Type'], created.ecosystem_type, models.EcosystemType)
            many_var(row['Salmon Life Stage'], created.salmon_life_stage, models.SalmonLifeStage)
            many_var(row['Project_Subtype'], created.project_sub_type, models.ProjectSubType)
            many_var(row['Project_Theme'], created.project_theme, models.ProjectTheme)
            many_var(row['Project_Core_Element'], created.core_component, models.CoreComponent)
            many_var(row['Project_Supportive_Element'], created.supportive_component, models.SupportiveComponent)
            many_var(row['Project Purpose'], created.project_purpose, models.ProjectPurpose)
            many_var(row['Funding Sources'], created.funding_sources, models.FundingSources)
            many_var(row['Lake System'], created.lake_system, models.LakeSystem)
            many_var(row['Watershed Name'], created.watershed, models.Watershed)
            many_var(row['Partners'], created.partner, models.Organization)
            first_last(row['DFO Project Authority'], created.DFO_project_authority)
            first_last(row['Area Chief'], created.DFO_area_chief)
            first_last(row['DFO Aboriginal Affairs Advisor'], created.DFO_IAA)
            first_last(row['DFO Resource manager'], created.DFO_resource_manager)
            first_last(row['DFO Biologists or Technicians'], created.DFO_technicians)
            first_last(row['Partners Primary Contact'], created.partner_contact)


def import_objective():
    path = os.path.join('/Users/orpenr/Desktop/import', 'objectives.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue

            species_tmp, _ = models.Species.objects.get_or_create(name=row['Species'].strip())

            river_tmp = None
            for obj in project_tmp.river.all():
                if obj.name == row['Location'].upper() and obj.species.name == species_tmp.name:
                    river_tmp = obj
                    break
                else:
                    river_tmp = None

            created, _ = models.Objective.objects.get_or_create(
                project_id=int(project_tmp.id),
                location_id=int(river_tmp.id) if river_tmp else None,
                unique_objective=row['Index'],
                task_description=row['Task Description'],
                element_title=row['Element Title'],
                activity_title=row['Activity Title'],
                pst_requirement=row['PST requirement indentified'],
                sil_requirement=row['SIL_requirement'],
                expected_results=row['Expected Results'],
                dfo_report=row['Products/Reports to provide to DFO'],
                outcomes_comment=row['Outcomes Comment'],
            )
            many_var(row['Objective_Category'], created.objective_category, models.ObjectiveCategory)


def import_report():
    path = os.path.join('/Users/orpenr/Desktop/import', 'reports.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement Number'].strip())
            except ObjectDoesNotExist:
                continue

            created, _ = models.Reports.objects.get_or_create(
                project_id=int(project_tmp.id),
                report_timeline=row['Report Timeline'],
                report_type=row['Report Types'],
                report_concerns=row['Report Concerns'],
                document_name=row['Document Name'],
                document_author=row['Document Owner/Author'],
                document_reference_information=row['Document Reference Information'],
                document_link=row['Document Link'],
                published=row['Is this report published?'],
            )


def import_data():
    path = os.path.join('/Users/orpenr/Desktop/import', 'data.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue

            if row['Species'] and row['Species'] != "":
                species_tmp, _ = models.Species.objects.get_or_create(name=row['Species'])
            else:
                species_tmp = None

            river_tmp = None
            for obj in project_tmp.river.all():
                if obj.name == row['River'].upper() and obj.species.name == species_tmp.name:
                    river_tmp = obj
                    break
                else:
                    river_tmp = None

            created, _ = models.Data.objects.get_or_create(
                project_id=int(project_tmp.id),
                sample_barrier=row['Barriers to Sample Collection and Data entry?'],
                samples_collected_comment=row['Comment'],
                samples_collected=row['Samples_Collected'],
                samples_collected_database=row['Samples Collected Database'],
                shared_drive=row['Shared Drive'],
                data_quality_check=row['Data Quality Check'],
                river_id=int(river_tmp.id) if river_tmp else None,
                sample_entered_database=row['Sample Entered Into Database'],
                sample_format=row['Sample Format'],
                data_products=row['Data Products'],
                data_products_database=row['Data Products Database'],
                data_products_comment=row['Data Products Comment']

            )


def import_method():
    path = os.path.join('/Users/orpenr/Desktop/import', 'methods.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue


            created, _ = models.Method.objects.get_or_create(
                project_id=int(project_tmp.id),
                sample_processing_method_type=row['Sample Processing Method Type'],
                planning_method_type=row['Planning Method Type'],
                field_work_method_type=row['Field_Work'],
                scale_processing_location=row['Scale Processng Location'],
                otolith_processing_location=row['Otolith Processing Location'],
                DNA_processing_location=row['DNA Processing Location'],
                heads_processing_location=row['Heads Processing Location'],
                instrument_data_processing_location=row['Instrument Data Processing Location'],
                #unique_method_number=row['Unique ID'],
            )


def import_method_document():
    path = os.path.join('/Users/orpenr/Desktop/import', 'projects.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement Number'].strip())
            except ObjectDoesNotExist:
                continue
            try:
                method_tmp = models.Method.objects.get(project=project_tmp)
            except ObjectDoesNotExist:
                continue
            created, _ = models.MethodDocument.objects.get_or_create(
                method_id=int(method_tmp.id),
                method_document_type=row['Type'],
                reference_number=row['Reference Number'],
                document_link=row['Document Link'],
                authors=row['Author'],
                publication_year=row['Publication Year'],
                title=row['Title'],
                unique_method_number=row['Unique ID'],
            )


def import_costing():
    path = os.path.join('/Users/orpenr/Desktop/import', 'costing.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['agreement_number'].strip())
            except ObjectDoesNotExist:
                continue
            created, _ = models.FundingYears.objects.get_or_create(
                project_id=int(project_tmp.id),
                funding_year=row['year'],
                agreement_cost=row['annual_agreement_cost'],
                project_cost=row['annual_project_cost'],
            )


def import_sample_outcome():
    path = os.path.join('/Users/orpenr/Desktop/import', 'sample_outcome.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue
            try:
                object_tmp = models.Objective.objects.get(project=project_tmp, unique_objective=row['Index'])
            except ObjectDoesNotExist:
                continue

            created, _ = models.SampleOutcome.objects.get_or_create(
                objective_id=int(object_tmp.id),
                sampling_outcome=row['Sampling_Outcome'],
                outcome_delivered=row['Outcome delivered?-was the sampling outcome met?'],
                unique_objective_number=row['Index'],
                outcome_quality=row['Outcome quality?'],
                sample_outcome_comment=row['Sampling Outcome Comment'],
            )


def import_reporting_outcome():
    path = os.path.join('/Users/orpenr/Desktop/import', 'reporting_outcome.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue

            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue
            try:
                object_tmp = models.Objective.objects.get(project=project_tmp, unique_objective=row['Index'])
            except ObjectDoesNotExist:
                continue
            if row['Reporting Link'] != "" and row['Reporting Link']:
                report_tmp = models.Reports.objects.get_or_create(document_link=row['Reporting Link'])
            else:
                report_tmp = None
            created, _ = models.ReportOutcome.objects.get_or_create(
                objective_id=int(object_tmp.id),
                reporting_outcome=row['Reporting_Outcome'],
                unique_objective_number=row['Index'],
                #site=row['Site'],
                outcome_delivered=row['Reporting Met'],
                report_outcome_comment=row['Comment'],
                reporting_outcome_metric=row['Metric'],
                report_link_id=int(report_tmp.id) if report_tmp else None,
            )


def first_last(row_name, instance_name):
    if row_name != "" and row_name:
        tmp_str = row_name.split(',')
        for tmp in tmp_str:
            tmp_whole_name = tmp.split(' ')
            tmp_first_name = tmp_whole_name[0].strip()
            if len(tmp_whole_name) > 1:
                tmp_last_name = tmp_whole_name[1].strip()
            else:
                tmp_last_name = None
            tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
            instance_name.add(int(tmp_person.id))
        return
    else:
        return


def many_var(row_name, instance_name, model_name):
    if row_name != "" and row_name:
        tmp_arr = row_name.split(',')
        for tmp in tmp_arr:
            tmp_obj, _ = model_name.objects.get_or_create(name=tmp.strip())
            instance_name.add(int(tmp_obj.id))
        return
    else:
        return


def output_select():
    path = os.path.join('/Users/orpenr/Desktop/import','drop_downs.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            print("('" + row['Outcomes Category'] + "','" + row['Outcomes Category'] + "')," )


def project_river():
    path = os.path.join('/Users/orpenr/Desktop/import', 'rivers.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue

            if row['Species'] and row['Species'] != "":
                species_tmp, _ = models.Species.objects.get_or_create(name=row['Species'])
            else:
                species_tmp = None

            if row['Sub-District Area'] and row['Sub-District Area'] != "":
                sub_tmp, _ = models.SubDistrictArea.objects.get_or_create(name=row['Sub-District Area'])
            else:
                sub_tmp = None

            created_river, _ = models.River.objects.get_or_create(
                name=row['River_Site'],
                species_id=int(species_tmp.id) if species_tmp else None,
                sub_district_area_id=int(sub_tmp.id) if sub_tmp else None,
                popid=row['popID']
            )
            project.river.add(int(created_river.id))


def delete_species():
    models.River.objects.all().delete()
    models.Species.objects.all().delete()


def delete_restart_2():
    models.SampleOutcome.objects.all().delete()


def delete_restart():
    '''
    models.SampleOutcome.objects.all().delete()
    models.ReportOutcome.objects.all().delete()
    models.FundingYears.objects.all().delete()
    models.MethodDocument.objects.all().delete()
    models.ProjectCertified.objects.all().delete()
    models.Method.objects.all().delete()
    models.Reports.objects.all().delete()
    models.Data.objects.all().delete()
    models.Objective.objects.all().delete()
    models.Project.objects.all().delete()
    '''
    #models.River.objects.all().delete()
    models.Species.objects.all().delete()
    models.MonitoringApproach.objects.all().delete()
    models.EcosystemType.objects.all().delete()
    models.HatcheryName.objects.all().delete()
    models.ManagementArea.objects.all().delete()
    models.SalmonLifeStage.objects.all().delete()
    models.ProjectSubType.objects.all().delete()
    models.ProjectTheme.objects.all().delete()
    models.CoreComponent.objects.all().delete()
    models.SupportiveComponent.objects.all().delete()
    models.ProjectPurpose.objects.all().delete()
    models.FundingSources.objects.all().delete()
    models.ObjectiveCategory.objects.all().delete()
    models.CapacityBuilding.objects.all().delete()
    models.OutComeBarrier.objects.all().delete()
    models.LakeSystem.objects.all().delete()
    models.CUName.objects.all().delete()
    models.CUIndex.objects.all().delete()
    models.FirstNations.objects.all().delete()
    models.Watershed.objects.all().delete()
    models.Person.objects.all().delete()
    models.Organization.objects.all().delete()
    #models.StockManagementUnit.objects.all().delete()
    #models.SubDistrictArea.objects.all().delete()
    #models.DU.objects.all().delete()


def import_restart():
    import_rivers()
    import_project()
    project_river()
    import_costing()
    import_objective()
    import_report()
    import_data()
    import_method()
    import_reporting_outcome()
    import_sample_outcome()
    add_is_active_org()
    add_is_active()


def add_is_active():
    path = os.path.join('/Users/orpenr/Desktop/import', 'persons.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                person = models.Person.objects.get(first_name=row['First name'].strip(), last_name=row['Last name'].strip())
            except ObjectDoesNotExist:
                continue
            person.is_active = row['Is Active']
            person.save()


def add_is_active_org():
    path = os.path.join('/Users/orpenr/Desktop/import', 'organizations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                organization = models.Organization.objects.get(name=row['Organization Name'].strip())
            except ObjectDoesNotExist:
                continue

            organization.is_active=row['Is Active']
            organization.save()


def update_rivers():
    path = os.path.join('/Users/orpenr/Desktop/import', 'rivers_finals.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                river = models.River.objects.get(name=row['SYSTEM_SITE'].strip(),  )
            except ObjectDoesNotExist:
                continue

            river.is_active=row['Is Active']
            river.save()


def delete_data():
    models.River.objects.all().delete()


def load_river_data():
    path = os.path.join('/Users/orpenr/Desktop/import', 'rivers_finals.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            models.StockManagementUnit.objects.get_or_create(name=row['SMU'].strip())
            models.DU.objects.get_or_create(name=row['DU'].strip())
            models.SubDistrictArea.objects.get_or_create(name=row['AREA'].strip())


def delete_river_data():
    for z in models.Project.objects.all():
        z.river.all().delete()
    for x in models.Data.objects.all():
        x.river = None
    for y in models.Objective.objects.all():
        y.location = None
