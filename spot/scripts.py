from . import models
import csv
import os
from dm_apps import settings
from . import models


def import_watershed_m9d2y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'List of BC Watersheds.csv')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader,None)
        for row in reader:
            created = models.Watershed.objects.get_or_create(
                group_code=row[0],
                name=row[1],
            )


def import_lakesystem_m9d2y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'Lake Systems of BC.csv')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader,None)
        for row in reader:
            created = models.LakeSystem.objects.get_or_create(
                name=row[0],
            )


def import_organization_m9d2y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'spot organizations.csv')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            created = models.Organization.objects.get_or_create(
                name=row[0],
                organization_type=row[1],
                section=row[2],
                address=row[3],
                city=row[4],
                province=row[5],
                country=row[6],
                phone=row[7],
                email=row[8],
                website=row[9]
            )


def import_rivers_m9d2y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'rivers.csv')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if models.River.objects.filter(name__contains=row[2]):
                continue
            created = models.River.objects.get_or_create(
                name=row[2],
                longitude=row[1],
                latitude=row[0]
            )


def import_person_m9d2y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'spot persons.csv')
    orgs = models.Organization.objects.all()
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            created, _ = models.Person.objects.get_or_create(
                last_name=row[0],
                first_name=row[1],
                phone=row[2],
                email=row[3],
                city=row[4],
                province=row[5],
                section=row[8],
                role=row[9],
                other_membership=row[10],
            )
            org_str = row[7]
            try:
                org_tmp, _ = models.Organization.objects.get(name=org_str)
            except:
                org_tmp = None
            if org_tmp is not None:
                created.organizations.add(org_tmp)


def import_project_m9d14y2021():
    path = os.path.join(settings.BASE_DIR, 'spot', 'import', 'projects.csv')
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            primary_river_str = row[19]
            primary_river_tmp, _ = models.River.objects.get_or_create(
                name=primary_river_str
            )
            """
            # DFO PROJECT AUTHORITY #
            if row[46].__contains__(','):
                DFO_project_authority_full = row[46].split(',')
            else:
                DFO_project_authority_full = row[46]

            for person in DFO_project_authority_full:
                DFO_project_authority_first = person.split(' ')[0]
                DFO_project_authority_last = person.split(' ')[1]
                try:
                    DFO_project_authority_tmp, _ = models.Person.objects.get(
                        first_name=DFO_project_authority_first, last_name=DFO_project_authority_last
                    )
                except:
                    DFO_project_authority_tmp = None
     
            # DFO AREA CHIEF #
            DFO_area_chief_first = row[48].split()[0]
            DFO_area_chief_last = row[48].split()[1]
            try:
                DFO_area_chief_tmp, _ = models.Person.objects.get(
                    first_name=DFO_area_chief_first, last_name=DFO_area_chief_last
                )
            except:
                DFO_area_chief_tmp = None

            ### DFO AAA ###
            DFO_aboriginal_AAA_first = row[47].split()[0]
            DFO_aboriginal_AAA_last = row[47].split()[1]
            try:
                DFO_aboriginal_AAA_tmp, _ = models.Person.objects.get(
                    first_name=DFO_aboriginal_AAA_first, last_name=DFO_aboriginal_AAA_last
                )
            except:
                DFO_aboriginal_AAA_tmp = None

            # DFO RESOURCE MANAGER #


            DFO_resource_manager_first = row[49].split()[0]
            DFO_resource_manager_last = row[49].split()[1]
            try:
                DFO_resource_manager_tmp, _ = models.Person.objects.get(
                    first_name=DFO_resource_manager_first, last_name=DFO_resource_manager_last
                )
            except:
                DFO_resource_manager_tmp = None

            # TRIBAL COUNCIL #
            tribal_council_str = row[50]
            tribal_council_tmp, _ = models.Organization.objects.get_or_create(
                name=tribal_council_str
            )

            # PRIMARY FIRST NATIONS CONTACT #
            primary_first_nations_contact_str = row[51]
            primary_first_nations_contact_tmp, _ = models.Person.objects.get_or_create(
                first_name=primary_first_nations_contact_str
            )
            DFO_technicians_str = row[55]
            DFO_technicians_tmp, _ = models.Person.objects.get_or_create(
                first_name=DFO_technicians_str
            )
            primary_river=primary_river_tmp,
                DFO_project_authority=DFO_project_authority_tmp,
                DFO_area_chief=DFO_area_chief_tmp,
                DFO_aboriginal_AAA=DFO_aboriginal_AAA_tmp,
                DFO_resource_manager=DFO_resource_manager_tmp,
                tribal_council=tribal_council_tmp,
                primary_first_nations_contact=primary_first_nations_contact_tmp,
            """
            created, _ = models.Project.objects.get_or_create(

                agreement_number=row[1],
                name=row[13],
                project_description=row[14],
                region=row[17],
                stock_management_unit=row[26],
                cu_index=row[27],
                cu_name=row[28],
                species=row[29],
                salmon_life_stage=row[31],
                project_type=row[33],
                project_sub_type=row[34],
                project_theme=row[36],
                project_stage=row[32],
                monitoring_approach=row[35],
                core_component=row[37],
                supportive_component=row[38],
                project_purpose=row[39],
                category_comments=row[40],
                DFO_link=row[41],
                DFO_program_reference=row[42],
                government_organization=row[43],
                first_nations_contact_role=row[52],
                contractor=row[59],
                contractor_contact=row[60],
                agreement_database=row[2],
                agreement_comment=row[4],
                funding_sources=row[6],
                agreement_type=row[7],
                project_lead_organization=row[10]
            )

            secondary_river_str = row[20]
            lake_system_str = row[21]
            watershed_str = row[22]
            partner_str = row[57]
            primary_contact_partner_str = row[58]

            secondary_river_tmp, _ = models.River.objects.get_or_create(
                name=secondary_river_str
            )
            lake_system_tmp, _ = models.LakeSystem.objects.get_or_create(
                name=lake_system_str
            )
            watershed_tmp, _ = models.Watershed.objects.get_or_create(
                name=watershed_str
            )

            partner_tmp, _ = models.Organization.objects.get_or_create(
                name=partner_str
            )
            primary_contact_partner_tmp, _ = models.Person.objects.get_or_create(
                first_name=primary_contact_partner_str
            )

            created.secondary_river.add(secondary_river_tmp)
            created.lake_system.add(lake_system_tmp)
            created.watershed.add(watershed_tmp)
            created.partner.add(partner_tmp)
            created.partner_contact.add(primary_contact_partner_tmp)
