from . import models
import csv
import os
from dm_apps import settings
from . import models
from django.core.exceptions import ObjectDoesNotExist


def import_watershed():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'watersheds.csv')
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
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'rivers.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if models.River.objects.filter(name__exact=row['River']) or row['River'] == "":
                continue
            else:
                created, _ = models.River.objects.get_or_create(
                    name=row['River'],
                    longitude=row['X_LONGT'],
                    latitude=row['Y_LAT'],
                )


def import_generic(file_name, model_name, row_name):
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', file_name)
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
    import_generic('CU_first_nations.csv', models.CUIndex, 'CU Index')
    import_generic('CU_first_nations.csv', models.CUName, 'CU Name')
    import_generic('CU_first_nations.csv', models.FirstNations, 'First Nations')
    import_generic('drop_down4.csv', models.Species, 'Species')
    import_generic('drop_down4.csv', models.SalmonLifeStage, 'Salmon Life Stage')
    import_generic('drop_down4.csv', models.ProjectSubType, 'Project Sub-Type')
    import_generic('drop_down4.csv', models.ProjectTheme, 'Project Theme')
    import_generic('drop_down4.csv', models.CoreComponent, 'Project Core Element')
    import_generic('drop_down4.csv', models.SupportiveComponent, 'Project Supportive Element')
    import_generic('drop_down4.csv', models.ProjectPurpose, 'Project Purpose')
    import_generic('drop_down4.csv', models.FundingSources, 'Funding Sources')
    import_generic('drop_down4.csv', models.CapacityBuilding, 'What capacity building did this project provide?')
    import_generic('drop_down4.csv', models.OutComeBarrier, 'Barrier to achieving outcomes?')
    import_generic('drop_down4.csv', models.PlanningMethodType, 'Planning Type')
    import_generic('drop_down4.csv', models.FieldWorkMethodType, 'Field Work Method')
    import_generic('drop_down4.csv', models.SampleProcessingMethodType, 'Sample Processing Type')
    import_generic('drop_down4.csv', models.SamplesCollected, 'Samples Collected')
    import_generic('drop_down4.csv', models.DatabaseChoice, 'Database')
    import_generic('drop_down4.csv', models.SampleBarrier, 'Barriers to Sample Collection')
    import_generic('drop_down4.csv', models.DataBarrier, 'Barriers to data checks/enter into database')
    import_generic('drop_down4.csv', models.SampleFormat, 'Data Format')
    import_generic('drop_down4.csv', models.DataProducts, 'Data Products')
    import_generic('drop_down4.csv', models.DataPrograms, 'Programs used in analysis')
    import_watershed()
    import_rivers()
    import_organization()
    import_person()
    import_project()
    import_costing()
    import_objective()
    import_report()
    import_data()
    import_method()
    import_reporting_outcome()
    import_sample_outcome()


def import_organization():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'organizations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if models.Organization.objects.filter(name__iexact=row['Organization Name']) or row['Organization Name'] == "":
                continue
            else:
                created, _ = models.Organization.objects.get_or_create(
                    name=row['Organization Name'],
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
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'persons.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or models.Person.objects.filter(first_name__iexact=row['First name'], last_name__iexact=row['Last name']):
                continue
            else:
                created, _ = models.Person.objects.get_or_create(
                    last_name=row['Last name'],
                    first_name=row['First name'],
                    phone=row['Work phone'],
                    email=row['Work email'],
                    city=row['Office location - city'],
                    province_state=row['state/province'],
                    country=row['Country'],
                    section=row['Section'],
                    role=row['Role'],
                    other_membership=row['Other membership'],
                )
                if row['Primary Organization'] != "":
                    org_tmp, _ = models.Organization.objects.get_or_create(name=row['Primary Organization'].strip())
                    created.organizations.add(org_tmp)
                else:
                    continue


def import_project():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects6.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue

            if row['Project Start Date'] == "":
                tmp_start = None
            else:
                tmp_start = row['Project Start Date']

            if row['Project End Date'] == "":
                tmp_end = None
            else:
                tmp_end = row['Project End Date']

            primary_river_tmp, _ = models.River.objects.get_or_create(name=row['Primary_River'].strip())
            first_nations_tmp, _ = models.FirstNations.objects.get_or_create(name=row['First Nations'].strip())
            cu_name_tmp, _ = models.CUName.objects.get_or_create(name=row['CUName'].strip())

            tmp_whole_name = row['First Nations Contact'].split(' ')
            tmp_first_name = tmp_whole_name[0].strip()
            if len(tmp_whole_name) > 1:
                tmp_last_name = tmp_whole_name[1].strip()
            else:
                tmp_last_name = None
            first_nations_contact_tmp, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)

            created, _ = models.Project.objects.get_or_create(
                project_number=row['Project Number'],
                agreement_number=row['Agreement Number'],
                name=row['Project Name'],
                project_description=row['Project Description'],
                start_date=tmp_start,
                end_date=tmp_end,
                primary_river_id=int(primary_river_tmp.id),
                ecosystem_type=row['Ecosystem Type'],
                management_area=row['DFO Management Area'],
                region=row['Region'],
                stock_management_unit=row['Stock Management Unit'],
                cu_name_id=int(cu_name_tmp.id),
                project_type=row['Project_Type'],
                project_stage=row['Project Stage'],
                monitoring_approach=row['Monitoring_Approach'],
                category_comments=row['Category Comments'],
                DFO_link=row['Links to other DFO Programs'],
                DFO_program_reference=row['Linked DFO Program Project Reference'],
                government_organization=row['Links to other Government Departments'],
                policy_program_connection=row['Policy and Program Connections'],
                first_nation_id=int(first_nations_tmp.id),
                first_nations_contact_id=int(first_nations_contact_tmp.id),
                first_nations_contact_role=row['First Nations Contact Role'],
                contractor=row['Contractors'],
                contractor_contact=row['Contractors Primary Contact'],
                agreement_database=row['Agreement Database'],
                agreement_comment=row['Agreement Comment'],
                other_funding_sources=row['Other Funding Sources'],
                agreement_type=row['Agreement Type'],
                lead_organization=row['Lead Organization'],
            )

            many_var(row['Species'], created.species, models.Species)
            many_var(row['CUIndex'], created.cu_index, models.CUIndex)
            many_var(row['Salmon Life Stage'], created.salmon_life_stage, models.SalmonLifeStage)
            many_var(row['Project_Subtype'], created.project_sub_type, models.ProjectSubType)
            many_var(row['Project_Theme'], created.project_theme, models.ProjectTheme)
            many_var(row['Project_Core_Element'], created.core_component, models.CoreComponent)
            many_var(row['Project_Supportive_Element'], created.supportive_component, models.SupportiveComponent)
            many_var(row['Project Purpose'], created.project_purpose, models.ProjectPurpose)
            many_var(row['Funding Sources'], created.funding_sources, models.FundingSources)
            many_var(row['Secondary River'], created.secondary_river, models.River)
            many_var(row['Lake System'], created.lake_system, models.LakeSystem)
            many_var(row['Watershed Name'], created.watershed, models.Watershed)
            many_var(row['Partners'], created.partner, models.Organization)

            first_last(row['DFO Project Authority'], created.DFO_project_authority)
            first_last(row['Area Chief'], created.DFO_area_chief)
            first_last(row['DFO Aboriginal Affairs Advisor'], created.DFO_aboriginal_AAA)
            first_last(row['DFO Resource manager'], created.DFO_resource_manager)
            first_last(row['DFO Biologists or Technicians'], created.DFO_technicians)
            first_last(row['Partners Primary Contact'], created.partner_contact)


def import_objective():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'objects4.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue

            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement_Number'].strip())
            except ObjectDoesNotExist:
                continue
            tmp_whole_name = row['Outcome contact'].split(' ')
            tmp_first_name = tmp_whole_name[0].strip()
            if len(tmp_whole_name) > 1:
                tmp_last_name = tmp_whole_name[1].strip()
            else:
                tmp_last_name = None
            outcome_contact_tmp, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
            species_tmp, _ = models.Species.objects.get_or_create(name=row['Species'].strip())
            location_tmp, _ = models.River.objects.get_or_create(name=row['River(s)'].strip())

            created = models.Objective.objects.create(
                project_id=int(project_tmp.id),
                species_id=int(species_tmp.id),
                location_id=int(location_tmp.id),
                unique_objective=row['Unique Objective'],
                task_description=row['Task Description'],
                element_title=row['Element Title'],
                activity_title=row['Activity Title'],
                pst_requirement=row['PST requirement indentified'],
                sil_requirement=row['SIL_requirement'],
                expected_results=row['Expected Results'],
                dfo_report=row['Products/Reports to provide to DFO'],
                outcome_met=row['Was the Sampling Outcome Met?'],
                outcomes_contact_id=int(outcome_contact_tmp.id),
                outcomes_comment=row['Comment on outcomes'],
                key_lesson=row['Key Lessons learned'],
                missed_opportunities=row['Missed opportunities?'],
            )
            many_var(row['Barrieres to Achieving outcomes?'], created.outcome_barrier, models.OutComeBarrier)
            many_var(row['Objective_Category'], created.objective_category, models.ObjectiveCategory)
            many_var(row['What capacity building did this project provide? (1-AH)'], created.capacity_building, models.CapacityBuilding)


def import_report():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects6.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement Number'].strip())
            except ObjectDoesNotExist:
                continue

            created = models.Reports.objects.create(
                project_id=int(project_tmp.id),
                report_timeline=row['Report Timeline'],
                report_type=row['Report Types'],
                report_concerns=row['Report Limitations and concerns'],
                document_name=row['Document Name'],
                document_author=row['Document Owner/Author'],
                document_reference_information=row['Document Reference Information'],
                document_link=row['Document Link'],
                published=row['Is this report published?'],
            )


def import_data():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects6.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue

            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement Number'].strip())
            except ObjectDoesNotExist:
                continue

            created = models.Data.objects.create(
                project_id=int(project_tmp.id),
                samples_collected_comment=row['Samples Collected Comment'],
                sample_entered_database=row['Was sample collection data entered into database(s)?'],
                data_quality_check=row['Was sample data quality check complete?'],
                data_products_comment=row['Data Products Comment'],

            )

            many_var(row['Samples Collected'], created.samples_collected, models.SamplesCollected)
            many_var(row['Samples Collected Database'], created.samples_collected_database, models.DatabaseChoice)
            many_var(row['Species'], created.species, models.Species)
            many_var(row['Barrier to sample collection?'], created.sample_barrier, models.SampleBarrier)
            many_var(row['Barriers to data checks/enter into database'], created.barrier_data_check_entry, models.DataBarrier)
            many_var(row['Sample Collection Format(s)'], created.sample_format, models.SampleFormat)
            many_var(row['Data Products'], created.data_products, models.DataProducts)
            many_var(row['Data Products Database(s)'], created.data_products_database, models.DatabaseChoice)
            many_var(row['Data Programs'], created.data_programs, models.DataPrograms)
            many_var(row['How was the data communicated to recipient?'], created.data_communication, models.DataCommunication)


def import_method():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects6.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['Agreement Number'].strip())
            except ObjectDoesNotExist:
                continue

            created = models.Method.objects.create(
                project_id=int(project_tmp.id),
                scale_processing_location=row['Location/Organization responsible for Scale Processing'],
                otolith_processing_location=row['Location/Organization responsible for Otolith Processing'],
                DNA_processing_location=row['Location/Organization responsible for DNA Processing'],
                heads_processing_location=row['Location/Organization responsible for Heads Processing'],
                instrument_data_processing_location=row['Location/Organization responsible for Instrument Data Processing'],
                knowledge_consideration=row['Traditional Ecological Knowledge Considered?'],
            )

            many_var(row['Field Work Methods Type'], created.field_work_method_type, models.FieldWorkMethodType)
            many_var(row['Planning Method Type'], created.planning_method_type, models.PlanningMethodType)
            many_var(row['Sample Processing Method Type'], created.sample_processing_method_type, models.SampleProcessingMethodType)


def import_costing():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'costing.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            try:
                project_tmp = models.Project.objects.get(agreement_number=row['agreement_number'].strip())
            except ObjectDoesNotExist:
                continue
            created = models.FundingYears.objects.create(
                project_id=int(project_tmp.id),
                funding_year=row['year'],
                agreement_cost=row['annual_agreement_cost'],
                project_cost=row['annual_project_cost'],
            )


def import_sample_outcome():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'sample_outcome.csv')
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
                object_tmp, _ = models.Objective.objects.get_or_create(project=project_tmp, unique_objective=row['Unique Objective'])
            except ObjectDoesNotExist:
                continue

            created = models.SampleOutcome.objects.create(
                objective_id=int(object_tmp.id),
                sampling_outcome=row['Sampling_Outcome'],
                outcome_delivered=row['Was the Sampling Outcome Met?'],
                unique_objective_number=row['Unique Objective'],
                outcome_report_delivered=row['Was Reporting Outcome Deliverable Met?'],
                outcome_quality=row['Outcome Quality']
            )


def import_reporting_outcome():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'reporting_outcome2.csv')
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
                object_tmp, _ = models.Objective.objects.get_or_create(project=project_tmp, unique_objective=row['Unique Objective'])
            except ObjectDoesNotExist:
                continue
            if row['Reporting Link'] != "" or row['Reporting Link'] is not None:
                report_tmp, _ = models.Reports.objects.get_or_create(document_link=row['Reporting Link'])
            else:
                report_tmp = None
            created = models.ReportOutcome.objects.create(
                objective_id=int(object_tmp.id),
                reporting_outcome=row['Reporting_Outcome'],
                unique_objective_number=row['Unique Objective'],
                outcome_delivered=row['Reporting Met'],
                report_link_id=int(report_tmp.id),
            )


def first_last(row_name, instance_name):
    if row_name != "" or row_name is not None:
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
    if row_name != "" or row_name is not None:
        tmp_arr = row_name.split(',')
        for tmp in tmp_arr:
            tmp_obj, _ = model_name.objects.get_or_create(name=tmp.strip())
            instance_name.add(int(tmp_obj.id))
        return
    else:
        return


def output_select():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'drop_down4.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.values() == "" or row.values() is None:
                continue
            print("('" + row['Report Type'] + "','" + row['Report Type'] + "')," )
