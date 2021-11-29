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


def import_drop_downs():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'drop_down3.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            created_species = models.Species.objects.get_or_create(
                name=row['Species'],
            )
            created_salmon_life_stage = models.SalmonLifeStage.objects.get_or_create(
                name=row['Salmon Life Stage'],
            )
            created_project_sub_type = models.ProjectSubType.objects.get_or_create(
                name=row['Project Sub-Type'],
            )
            created_project_theme = models.ProjectTheme.objects.get_or_create(
                name=row['Project Theme'],
            )
            created_core_component = models.CoreComponent.objects.get_or_create(
                name=row['Project Core Element'],
            )
            created_supportive_component = models.SupportiveComponent.objects.get_or_create(
                name=row['Project Supportive Element'],
            )
            created_project_purpose = models.ProjectPurpose.objects.get_or_create(
                name=row['Project Purpose'],
            )
            created_funding_sources = models.FundingSources.objects.get_or_create(
                name=row['Funding Sources'],
            )
            created_capacity_building = models.CapacityBuilding.objects.get_or_create(
                name=row['What capacity building did this project provide?'],
            )
            created_outcome_barrier = models.OutComeBarrier.objects.get_or_create(
                name=row['Barrier to achieving outcomes?'],
            )
            created_planning = models.PlanningMethodType.objects.get_or_create(
                name=row['Planning Type'],
            )
            created_field_work = models.FieldWorkMethodType.objects.get_or_create(
                name=row['Field Work Method'],
            )
            created_sample_processing = models.SampleProcessingMethodType.objects.get_or_create(
                name=row['Sample Processing Type'],
            )
            created_sample_collected = models.SamplesCollected.objects.get_or_create(
                name=row['Samples Collected'],
            )
            created_database = models.DatabaseChoice.objects.get_or_create(
                name=row['Database'],
            )
            created_sample_barrier = models.SampleBarrier.objects.get_or_create(
                name=row['Barriers to Sample Collection'],
            )
            created_data_barrier = models.DataBarrier.objects.get_or_create(
                name=row['Barriers to data checks/enter into database'],
            )
            created_sample_format = models.SampleFormat.objects.get_or_create(
                name=row['Data Format'],
            )
            created_sample_format = models.SampleFormat.objects.get_or_create(
                name=row['Data Format'],
            )
            created_data_products = models.DataProducts.objects.get_or_create(
                name=row['Data Products'],
            )
            created_data_programs = models.DataPrograms.objects.get_or_create(
                name=row['Programs used in analysis'],
            )
            created_data_communication = models.DataCommunication.objects.get_or_create(
                name=row['data communication'],
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

            if row['Species'].__contains__(','):
                tmp_arr = row['Species'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.Species.objects.get_or_create(name=tmp)
                    created.species.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.Species.objects.get_or_create(name=row['Species'])
                created.species.add(int(tmp_obj.id))

            if row['Salmon Life Stage'].__contains__(','):
                tmp_arr = row['Salmon Life Stage'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.SalmonLifeStage.objects.get_or_create(name=tmp)
                    created.salmon_life_stage.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.SalmonLifeStage.objects.get_or_create(name=row['Salmon Life Stage'])
                created.salmon_life_stage.add(int(tmp_obj.id))

            if row['Project_Subtype'].__contains__(','):
                tmp_arr = row['Project_Subtype'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.ProjectSubType.objects.get_or_create(name=tmp)
                    created.project_sub_type.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.ProjectSubType.objects.get_or_create(name=row['Project_Subtype'])
                created.project_sub_type.add(int(tmp_obj.id))

            if row['Project_Theme'].__contains__(','):
                tmp_arr = row['Project_Theme'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.ProjectTheme.objects.get_or_create(name=tmp)
                    created.project_theme.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.ProjectTheme.objects.get_or_create(name=row['Project_Theme'])
                created.project_theme.add(int(tmp_obj.id))

            if row['Project_Core_Element'].__contains__(','):
                tmp_arr = row['Project_Core_Element'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.CoreComponent.objects.get_or_create(name=tmp)
                    created.core_component.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.CoreComponent.objects.get_or_create(name=row['Project_Core_Element'])
                created.core_component.add(int(tmp_obj.id))

            if row['Project_Supportive_Element'].__contains__(','):
                tmp_arr = row['Project_Supportive_Element'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.SupportiveComponent.objects.get_or_create(name=tmp)
                    created.supportive_component.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.SupportiveComponent.objects.get_or_create(name=row['Project_Supportive_Element'])
                created.supportive_component.add(int(tmp_obj.id))

            if row['Project Purpose'].__contains__(','):
                tmp_arr = row['Project Purpose'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.ProjectPurpose.objects.get_or_create(name=tmp)
                    created.project_purpose.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.ProjectPurpose.objects.get_or_create(name=row['Project Purpose'])
                created.project_purpose.add(int(tmp_obj.id))

            if row['Funding Sources'].__contains__(','):
                tmp_arr = row['Funding Sources'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.FundingSources.objects.get_or_create(name=tmp)
                    created.funding_sources.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.FundingSources.objects.get_or_create(name=row['Funding Sources'])
                created.funding_sources.add(int(tmp_obj.id))

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
        tmp_obj_id=0
        for row in reader:
            tmp_obj_id=tmp_obj_id+1
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
                sil_requirement=row['SIL_requirement'],
                expected_results=row['Expected Results'],
                dfo_report=row['Products/Reports to provide to DFO'],
                outcome_met=row['Was the Sampling Outcome Met?'],
                outcomes_contact_id=int(outcome_contact_tmp.id),
                outcomes_comment=row['Comment on outcomes'],
                key_lesson=row['Key Lessons learned'],
                missed_opportunities=row['Missed opportunities?'],
                objective_id=tmp_obj_id,
            )

            if row['River(s)'].__contains__(','):
                tmp_arr = row['River(s)'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.River.objects.get_or_create(name=tmp)
                    created.location.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.River.objects.get_or_create(name=row['River(s)'])
                created.location.add(int(tmp_obj.id))

            if row['Objective_Category'].__contains__(','):
                tmp_arr = row['Objective_Category'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.ObjectiveCategory.objects.get_or_create(name=tmp)
                    created.objective_category.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.ObjectiveCategory.objects.get_or_create(name=row['Objective_Category'])
                created.objective_category.add(int(tmp_obj.id))

            if row['Species'].__contains__(','):
                tmp_arr = row['Species'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.Species.objects.get_or_create(name=tmp)
                    created.species.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.Species.objects.get_or_create(name=row['Species'])
                created.species.add(int(tmp_obj.id))

            if row['Barrieres to Achieving outcomes?'].__contains__(','):
                tmp_arr = row['Barrieres to Achieving outcomes?'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.OutComeBarrier.objects.get_or_create(name=tmp)
                    created.outcome_barrier.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.OutComeBarrier.objects.get_or_create(name=row['Barrieres to Achieving outcomes?'])
                created.outcome_barrier.add(int(tmp_obj.id))

            if row['What capacity building did this project provide? (1-AH)'].__contains__(','):
                tmp_arr = row['What capacity building did this project provide? (1-AH)'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.CapacityBuilding.objects.get_or_create(name=tmp)
                    created.capacity_building.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.CapacityBuilding.objects.get_or_create(name=row['What capacity building did this project provide? (1-AH)'])
                created.capacity_building.add(int(tmp_obj.id))


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

            created, _ = models.Data.objects.get_or_create(
                project_id=int(project_tmp.id),
                samples_collected_comment=row['Samples Collected Comment'],
                sample_entered_database=row['Was sample collection data entered into database(s)?'],
                data_quality_check=row['Was sample data quality check complete?'],
                data_products_comment=row['Data Products Comment'],

            )

            if row['Samples Collected'].__contains__(','):
                tmp_arr = row['Samples Collected'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.SamplesCollected.objects.get_or_create(name=tmp)
                    created.samples_collected.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.SamplesCollected.objects.get_or_create(name=row['Samples Collected'])
                created.samples_collected.add(int(tmp_obj.id))

            if row['Samples Collected Database'].__contains__(','):
                tmp_arr = row['Samples Collected Database'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DatabaseChoice.objects.get_or_create(name=tmp)
                    created.samples_collected_database.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DatabaseChoice.objects.get_or_create(name=row['Samples Collected Database'])
                created.samples_collected_database.add(int(tmp_obj.id))

            if row['Species'].__contains__(','):
                tmp_arr = row['Species'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.Species.objects.get_or_create(name=tmp)
                    created.species.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.Species.objects.get_or_create(name=row['Species'])
                created.species.add(int(tmp_obj.id))

            if row['Barrier to sample collection?'].__contains__(','):
                tmp_arr = row['Barrier to sample collection?'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.SampleBarrier.objects.get_or_create(name=tmp)
                    created.sample_barrier.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.SampleBarrier.objects.get_or_create(name=row['Barrier to sample collection?'])
                created.sample_barrier.add(int(tmp_obj.id))

            if row['Barriers to data checks/enter into database'].__contains__(','):
                tmp_arr = row['Barriers to data checks/enter into database'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DataBarrier.objects.get_or_create(name=tmp)
                    created.barrier_data_check_entry.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DataBarrier.objects.get_or_create(name=row['Barriers to data checks/enter into database'])
                created.barrier_data_check_entry.add(int(tmp_obj.id))

            if row['Sample Collection Format(s)'].__contains__(','):
                tmp_arr = row['Sample Collection Format(s)'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.SampleFormat.objects.get_or_create(name=tmp)
                    created.sample_format.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.SampleFormat.objects.get_or_create(name=row['Sample Collection Format(s)'])
                created.sample_format.add(int(tmp_obj.id))

            if row['Data Products'].__contains__(','):
                tmp_arr = row['Data Products'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DataProducts.objects.get_or_create(name=tmp)
                    created.data_products.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DataProducts.objects.get_or_create(name=row['Data Products'])
                created.data_products.add(int(tmp_obj.id))

            if row['Data Products Database(s)'].__contains__(','):
                tmp_arr = row['Data Products Database(s)'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DatabaseChoice.objects.get_or_create(name=tmp)
                    created.data_products_database.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DatabaseChoice.objects.get_or_create(name=row['Data Products Database(s)'])
                created.data_products_database.add(int(tmp_obj.id))

            if row['Data Programs'].__contains__(','):
                tmp_arr = row['Data Programs'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DataPrograms.objects.get_or_create(name=tmp)
                    created.data_programs.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DataPrograms.objects.get_or_create(name=row['Data Programs'])
                created.data_programs.add(int(tmp_obj.id))

            if row['How was the data communicated to recipient?'].__contains__(','):
                tmp_arr = row['How was the data communicated to recipient?'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.DataCommunication.objects.get_or_create(name=tmp)
                    created.data_communication.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.DataCommunication.objects.get_or_create(name=row['How was the data communicated to recipient?'])
                created.data_communication.add(int(tmp_obj.id))


def import_method():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects2.csv')
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_tmp, _ = models.Project.objects.get_or_create(agreement_number=row['Agreement Number'])

            created, _ = models.Method.objects.get_or_create(
                project_id=int(project_tmp.id),
                scale_processing_location=row['Location/Organization responsible for Scale Processing'],
                otolith_processing_location=row['Location/Organization responsible for Otolith Processing'],
                DNA_processing_location=row['Location/Organization responsible for DNA Processing'],
                heads_processing_location=row['Location/Organization responsible for Heads Processing'],
                instrument_data_processing_location=row['Location/Organization responsible for Instrument Data Processing'],
                knowledge_consideration=row['Traditional Ecological Knowledge Considered?'],
            )

            if row['Method Type'].__contains__(','):
                tmp_arr = row['Method Type'].split(',')
                for tmp in tmp_arr:
                    tmp_obj, _ = models.FieldWorkMethodType.objects.get_or_create(name=tmp)
                    created.field_work_method_type.add(int(tmp_obj.id))
            else:
                tmp_obj, _ = models.FieldWorkMethodType.objects.get_or_create(name=row['Method Type'])
                created.field_work_method_type.add(int(tmp_obj.id))
