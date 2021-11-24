from . import models
import csv
import os
from dm_apps import settings
from . import models


def import_watershed():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'watersheds.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.Watershed.objects.get_or_create(
                group_code=row['group_code'],
                name=row['name'],
            )


def import_lakesystem():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'lake_systems.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.LakeSystem.objects.get_or_create(
                name=row['lake_systems'],
            )


def import_CUIndex():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'CU_first_nations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.CUIndex.objects.get_or_create(
                name=row['CU Index'],
            )


def import_CUName():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'CU_first_nations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.CUName.objects.get_or_create(
                name=row['CU Name'],
            )


def import_first_nations():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'CU_first_nations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.FirstNations.objects.get_or_create(
                name=row['First Nations'],
            )


def import_rivers():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'rivers.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if models.River.objects.filter(name__contains=row['River']):
                continue
            created = models.River.objects.get_or_create(
                name=row['River'],
                longitude=row['X_LONGT'],
                latitude=row['Y_LAT'],
            )


def import_organization():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'organizations.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = models.Organization.objects.get_or_create(
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
        next(reader, None)
        for row in reader:
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
            org_tmp, _ = models.Organization.objects.get_or_create(name=row['Primary Organization'])
            created.organizations.add(org_tmp)


def import_project():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects2.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row['Species'].__contains__(','):
                species_tmp = row['Species'].split(',')
            else:
                species_tmp = row['Species'],

            if row['Salmon Life Stage'].__contains__(','):
                salmon_life_stage_tmp = row['Salmon Life Stage'].split(',')
            else:
                salmon_life_stage_tmp = row['Salmon Life Stage'],

            if row['Project_Subtype'].__contains__(','):
                project_sub_type_tmp = row['Project_Subtype'].split(',')
            else:
                project_sub_type_tmp = row['Project_Subtype'],

            if row['Project_Theme'].__contains__(','):
                project_theme_tmp = row['Project_Theme'].split(',')
            else:
                project_theme_tmp = row['Project_Theme'],

            if row['Project_Core_Element'].__contains__(','):
                core_component_tmp = row['Project_Core_Element'].split(',')
            else:
                core_component_tmp = row['Project_Core_Element'],

            if row['Project_Supportive_Element'].__contains__(','):
                supportive_component_tmp = row['Project_Supportive_Element'].split(',')
            else:
                supportive_component_tmp = row['Project_Supportive_Element'],

            if row['Project Purpose'].__contains__(','):
                project_purpose_tmp = row['Project Purpose'].split(',')
            else:
                project_purpose_tmp = row['Project Purpose'],

            if row['Funding Sources'].__contains__(','):
                funding_sources_tmp = row['Funding Sources'].split(',')
            else:
                funding_sources_tmp = row['Funding Sources'],

            if row['DFO Management Area'].isnumeric():
                management_area_tmp = row['DFO Management Area']
            else:
                management_area_tmp = 999

            if row['Project Start Date'] == 'NA':
                start_date_tmp = '2100-01-01'
            else:
                start_date_tmp = row['Project Start Date']

            if row['Project End Date'] == 'NA':
                end_date_tmp = '2100-01-01'
            else:
                end_date_tmp = row['Project End Date']


            primary_river_tmp, _ = models.River.objects.get_or_create(name=row['Primary_River'])
            first_nations_tmp, _ = models.FirstNations.objects.get_or_create(name=row['First Nations'])
            cu_index_tmp, _ = models.CUIndex.objects.get_or_create(name=row['CUIndex'])
            cu_name_tmp, _ = models.CUName.objects.get_or_create(name=row['CUName'])

            if row['First Nations Contact'].__contains__(' '):
                tmp_whole_name = row['First Nations Contact'].split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                first_nations_contact_tmp, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
            else:
                first_nations_contact_tmp, _ = models.Person.objects.get_or_create(first_name=row['First Nations Contact'])

            created, _ = models.Project.objects.get_or_create(
                project_number=row['Project Number'],
                agreement_number=row['Agreement Number'],
                name=row['Project Name'],
                project_description=row['Project Description'],
                start_date=start_date_tmp,
                end_date=end_date_tmp,
                primary_river_id=int(primary_river_tmp.id),
                ecosystem_type=row['Ecosystem Type'],
                management_area=management_area_tmp,
                region=row['Region'],
                stock_management_unit=row['Stock Management Unit'],
                cu_index_id=int(cu_index_tmp.id),
                cu_name_id=int(cu_name_tmp.id),
                species=species_tmp,
                salmon_life_stage=salmon_life_stage_tmp,
                project_type=row['Project_Type'],
                project_sub_type=project_sub_type_tmp,
                project_theme=project_theme_tmp,
                project_stage=row['Project Stage'],
                monitoring_approach=row['Monitoring_Approach'],
                core_component=core_component_tmp,
                supportive_component=supportive_component_tmp,
                project_purpose=project_purpose_tmp,
                category_comments=row['Category Comments'],
                DFO_link=row['Links to other DFO Programs'],
                DFO_program_reference=['Linked DFO Program Project Reference'],
                government_organization=row['Links to other Government Departments'],
                policy_program_connection=row['Policy and Program Connections'],
                first_nation_id=int(first_nations_tmp.id),
                first_nations_contact_id=int(first_nations_contact_tmp.id),
                first_nations_contact_role=row['First Nations Contact Role'],
                contractor=row['Contractors'],
                contractor_contact=row['Contractors Primary Contact'],
                agreement_database=row['Agreement Database'],
                agreement_comment=row['Agreement Comment'],
                funding_sources=funding_sources_tmp,
                other_funding_sources=row['Other Funding Sources'],
                agreement_type=['Agreement Type'],
                lead_organization=['Lead Organization'],
            )

            if row['Secondary River'].__contains__(','):
                tmp_arr = row['Secondary River'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.River.objects.get_or_create(name=tmp)
                    created.secondary_river.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.River.objects.get_or_create(name=row['Secondary River'])
                created.secondary_river.add(int(tmp_obj.id))

            if row['Lake System'].__contains__(','):
                tmp_arr = row['Lake System'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.LakeSystem.objects.get_or_create(name=tmp)
                    created.lake_system.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.LakeSystem.objects.get_or_create(name=row['Lake System'])
                created.lake_system.add(int(tmp_obj.id))

            if row['Watershed Name'].__contains__(','):
                tmp_arr = row['Watershed Name'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.Watershed.objects.get_or_create(name=tmp)
                    created.watershed.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.Watershed.objects.get_or_create(name=row['Watershed Name'])
                created.watershed.add(int(tmp_obj.id))

            if row['Partners'].__contains__(','):
                tmp_arr = row['Partners'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.Organization.objects.get_or_create(name=tmp)
                    created.partner.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.Organization.objects.get_or_create(name=row['Partners'])
                created.partner.add(int(tmp_obj.id))

            if row['DFO Project Authority'].__contains__(','):
                tmp_str = row['DFO Project Authority'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.DFO_project_authority.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.DFO_project_authority.add(int(tmp_person.id))
            elif row['DFO Project Authority'].__contains__(' '):
                tmp = row['DFO Project Authority']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.DFO_project_authority.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['DFO Project Authority'])
                created.DFO_project_authority.add(int(tmp_person.id))

            if row['Area Chief'].__contains__(','):
                tmp_str = row['Area Chief'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.DFO_area_chief.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.DFO_area_chief.add(int(tmp_person.id))
            elif row['Area Chief'].__contains__(' '):
                tmp = row['Area Chief']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.DFO_area_chief.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['Area Chief'])
                created.DFO_area_chief.add(int(tmp_person.id))

            if row['DFO Aboriginal Affairs Advisor'].__contains__(','):
                tmp_str = row['DFO Aboriginal Affairs Advisor'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.DFO_aboriginal_AAA.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.DFO_aboriginal_AAA.add(int(tmp_person.id))
            elif row['DFO Aboriginal Affairs Advisor'].__contains__(' '):
                tmp = row['DFO Aboriginal Affairs Advisor']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.DFO_aboriginal_AAA.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['DFO Aboriginal Affairs Advisor'])
                created.DFO_aboriginal_AAA.add(int(tmp_person.id))

            if row['DFO Resource manager'].__contains__(','):
                tmp_str = row['DFO Resource manager'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.DFO_resource_manager.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.DFO_resource_manager.add(int(tmp_person.id))
            elif row['DFO Resource manager'].__contains__(' '):
                tmp = row['DFO Resource manager']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.DFO_resource_manager.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['DFO Resource manager'])
                created.DFO_resource_manager.add(int(tmp_person.id))

            if row['DFO Biologists or Technicians'].__contains__(','):
                tmp_str = row['DFO Biologists or Technicians'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.DFO_technicians.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.DFO_technicians.add(int(tmp_person.id))
            elif row['DFO Biologists or Technicians'].__contains__(' '):
                tmp = row['DFO Biologists or Technicians']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.DFO_technicians.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['DFO Biologists or Technicians'])
                created.DFO_technicians.add(int(tmp_person.id))

            if row['Partners Primary Contact'].__contains__(','):
                tmp_str = row['Partners Primary Contact'].split(',')
                for tmp in tmp_str:
                    if tmp.__contains__(' '):
                        tmp_whole_name = tmp.split(' ')
                        tmp_first_name = tmp_whole_name[0]
                        tmp_last_name = tmp_whole_name[1]
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                        created.partner_contact.add(int(tmp_person.id))
                    else:
                        tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp)
                        created.partner_contact.add(int(tmp_person.id))
            elif row['Partners Primary Contact'].__contains__(' '):
                tmp = row['Partners Primary Contact']
                tmp_whole_name = tmp.split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                tmp_person, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
                created.partner_contact.add(int(tmp_person.id))
            else:
                tmp_person, _ = models.Person.objects.get_or_create(first_name=row['Partners Primary Contact'])
                created.partner_contact.add(int(tmp_person.id))


def import_objective():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'objective.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row['Objective_Category'].__contains__(','):
                objective_category_tmp = row['Objective_Category'].split(',')
            else:
                objective_category_tmp = row['Objective_Category'],

            if row['Species'].__contains__(','):
                species_tmp = row['Species'].split(',')
            else:
                species_tmp = row['Species'],

            if row['Barrieres to Achieving outcomes?'].__contains__(','):
                barriers_tmp = row['Barrieres to Achieving outcomes?'].split(',')
            else:
                barriers_tmp = row['Barrieres to Achieving outcomes?'],

            if row['What capacity building did this project provide? (1-AH)'].__contains__(','):
                capacity_tmp = row['What capacity building did this project provide? (1-AH)'].split(',')
            else:
                capacity_tmp = row['What capacity building did this project provide? (1-AH)'],

            if row['Outcome contact'].__contains__(' '):
                tmp_whole_name = row['Outcome contact'].split(' ')
                tmp_first_name = tmp_whole_name[0]
                tmp_last_name = tmp_whole_name[1]
                outcome_contact_tmp, _ = models.Person.objects.get_or_create(first_name=tmp_first_name, last_name=tmp_last_name)
            else:
                outcome_contact_tmp, _ = models.Person.objects.get_or_create(first_name=row['Outcome contact'])

            project_tmp, _ = models.Project.objects.get_or_create(agreement_number=row['Agreement_Number'])

            created, _ = models.Objective.objects.get_or_create(
                project_id=int(project_tmp.id),
                task_description=row['Task Description'],
                element_title=row['Element Title'],
                activity_title=row['Activity Title'],
                pst_requirement=row['PST requirement indentified'],
                objective_category=objective_category_tmp,
                species=species_tmp,
                sil_requirement=row['SIL_requirement'],
                expected_results=row['Expected Results'],
                dfo_report=row['Products/Reports to provide to DFO'],
                outcome_met=row['Was the Sampling Outcome Met?'],
                outcomes_contact_id=int(outcome_contact_tmp.id),
                outcomes_comment=row['Comment on outcomes'],
                outcome_barrier=barriers_tmp,
                capacity_building=capacity_tmp,
                key_lesson=row['Key Lessons learned'],
                missed_opportunities=row['Missed opportunities?'],
            )

            if row['River(s)'].__contains__(','):
                tmp_arr = row['River(s)'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.River.objects.get_or_create(name=tmp)
                    created.location.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.River.objects.get_or_create(name=row['River(s)'])
                created.location.add(int(tmp_obj.id))


def import_report():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects2.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_tmp, _ = models.Project.objects.get_or_create(agreement_number=row['Agreement Number'])

            created, _ = models.Reports.objects.get_or_create(
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
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects2.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_tmp, _ = models.Project.objects.get_or_create(agreement_number=row['Agreement Number'])

            if row['Samples Collected'].__contains__(','):
                samples_collected_tmp = row['Samples Collected'].split(',')
            else:
                samples_collected_tmp = row['Samples Collected'],

            if row['Species'].__contains__(','):
                species_tmp = row['Species'].split(',')
            else:
                species_tmp = row['Species'],

            if row['Samples Collected Database'].__contains__(','):
                samples_database_tmp = row['Samples Collected Database'].split(',')
            else:
                samples_database_tmp = row['Samples Collected Database'],

            if row['Barrier to sample collection?'].__contains__(','):
                sample_barrier_tmp = row['Barrier to sample collection?'].split(',')
            else:
                sample_barrier_tmp = row['Barrier to sample collection?'],

            if row['Barriers to data checks/enter into database'].__contains__(','):
                sample_barrier_check_tmp = row['Barriers to data checks/enter into database'].split(',')
            else:
                sample_barrier_check_tmp = row['Barriers to data checks/enter into database'],

            if row['Barriers to data checks/enter into database'].__contains__(','):
                sample_barrier_check_tmp = row['Barriers to data checks/enter into database'].split(',')
            else:
                sample_barrier_check_tmp = row['Barriers to data checks/enter into database'],

            if row['Sample Collection Format(s)'].__contains__(','):
                sample_format_tmp = row['Sample Collection Format(s)'].split(',')
            else:
                sample_format_tmp = row['Sample Collection Format(s)'],

            if row['Data Products'].__contains__(','):
                data_products_tmp = row['Data Products'].split(',')
            else:
                data_products_tmp = row['Data Products'],

            if row['Data Products Database(s)'].__contains__(','):
                data_products_database_tmp = row['Data Products Database(s)'].split(',')
            else:
                data_products_database_tmp = row['Data Products Database(s)'],

            if row['Data Programs'].__contains__(','):
                data_programs_tmp = row['Data Programs'].split(',')
            else:
                data_programs_tmp = row['Data Programs'],

            created, _ = models.Data.objects.get_or_create(
                project_id=int(project_tmp.id),
                species=species_tmp,
                samples_collected=samples_collected_tmp,
                samples_collected_comment=row['Samples Collected Comment'],
                samples_collected_database=samples_database_tmp,
                sample_barrier=sample_barrier_tmp,
                sample_entered_database=row['Was sample collection data entered into database(s)?'],
                data_quality_check=row['Was sample data quality check complete?'],
                barrier_data_check_entry=sample_barrier_check_tmp,
                sample_format=sample_format_tmp,
                data_products=data_products_tmp,
                data_products_database=data_products_database_tmp,
                data_products_comment=row['Data Products Comment'],
                data_programs=data_programs_tmp,
                data_communication=row['How was the data communicated to recipient?'],
            )


def import_method():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects2.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_tmp, _ = models.Project.objects.get_or_create(agreement_number=row['Agreement Number'])

            if row['Method Type'].__contains__(','):
                method_tmp = row['Method Type'].split(',')
            else:
                method_tmp = row['Method Type'],

            created, _ = models.Method.objects.get_or_create(
                project_id=int(project_tmp.id),
                field_work_method_type=method_tmp,
                scale_processing_location=row['Location/Organization responsible for Scale Processing'],
                otolith_processing_location=row['Location/Organization responsible for Otolith Processing'],
                DNA_processing_location=row['Location/Organization responsible for DNA Processing'],
                heads_processing_location=row['Location/Organization responsible for Heads Processing'],
                instrument_data_processing_location=row['Location/Organization responsible for Instrument Data Processing'],
                knowledge_consideration=row['Traditional Ecological Knowledge Considered?'],
            )