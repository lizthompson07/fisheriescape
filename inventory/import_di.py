import csv
import os
import xml.etree.ElementTree as ET

from django.contrib.auth.models import User
from django.utils import timezone

from inventory import models
from django.conf import settings

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from . import xml_export

def get_create_user(email):
    try:
        my_user = User.objects.get(email__iexact=email)
    except User.MultipleObjectsReturned:
        print(email)
    except User.DoesNotExist:
        # if it is a DFO email, then it should be easy..
        email = email.lower()
        names = email.split("@")[0].split(".")
        first_name = names[0]
        last_name = names[-1]
        # print(email, first_name, last_name, names)

        # if this is a dfo email, and there is a first and last name, they can be set as an active user
        if "dfo" in email and len(names) > 1:
            is_active = True
        else:
            is_active = False

        my_user = User.objects.create(
            username=email,
            first_name=first_name.title(),
            last_name=last_name.title(),
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
            is_active=is_active,
            email=email,
        )
        print("new user created:", my_user.first_name, my_user.last_name, my_user.email, "is_active=", is_active)
    finally:
        return my_user


def restart():
    models.Resource.objects.filter(section_id=61).delete()


def check_uuids():
    target_dir = os.path.join(settings.BASE_DIR, 'inventory', 'temp')
    # with open(os.path.join(target_dir, "QuiderE_v2b.xml"), 'r', encoding="utf8") as xml_file:
    # with open(os.path.join(target_dir, "JacobsK_v2b.xml"), 'r') as xml_file:
    # with open(os.path.join(target_dir, "PED_Records_Output_v3.xml"), 'r') as xml_file:
    with open(os.path.join(target_dir, "BondSRecords_Output.xml"), 'r') as xml_file:

        tree = ET.parse(xml_file)
        recordset = tree.getroot()
        my_dict = {}
        for record in recordset:
            uuid = record.find("record_uuid").text
            if not my_dict.get(uuid):
                my_dict[uuid] = 0
            my_dict[uuid] += 1

        for uuid in my_dict:
            if my_dict[uuid] > 1:
                print(uuid, my_dict[uuid])


target_dir = os.path.join(settings.BASE_DIR, 'inventory', 'temp')


def import_paas():
    with open(os.path.join(target_dir, "paa.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            shared_models.PAAItem.objects.get_or_create(
                code=row["code"],
                name=row["english"],
                nom=row["french"],
            )


"""﻿
ID --> this will be a new field
ODIP --> redundant
On OGP --> redundant with url
Dataset title English: --> good.
Dataset title French: --> good
Dataset description English: --> good
Dataset description French: --> good
Your name: --> nix
Your title/role: --> nix
Data owner's name: --> owner
Data owner's email: --> owner email
Data owner's sector: --> this will be tricky. Maybe we can create a generic section from each region based on this set. 
Data owner's Directorate/Branch/Division: --> 
Data owner's region: --> 
IT custodian's name:  --> messy.
Date: --> what is this date?
Source/location of dataset:  --> sometimes a url, othertimes a location on a drive or in a building
Is the dataset publicly available? --> 
Location (if yes): --> These can be concatinated to open data notes
Location (French): --> 
Corresponding Pub/Bib Record --> This can be appended to notes section but should be prefaced by: "needs to be properly added as a citation in the record"
Do you have a data quality process in place? --> appended to notes
Is/can the dataset be machine readable and platform independent? --> appended to notes
What is the current format of the source dataset? --> needs to be parse by data_distribution_formats.py
What is the estimated volume of the dataset (in GB)? --> notes
What is the geographic coverage of the dataset? --> geo_descr_eng
Other, please describe: --> we can do a search here for bounding box. Otherwise can be appended to notes
Is the data for this dataset derived from more than one source? --> notes
How often does the source data change? --> maintenance frequency…problem is split between two cols. If we concatenate then search for FK. If not found, append as note.
If "Other", please indicate time frame: --> 
What is the date range of the dataset? --> needs to be digested. Very problematic though because of the use of hyphen
How does the dataset link to DFO's Program Alignment Architecture (PAA)? --> need to create a new FK
NOTES --> append to notes; may contain an FGP url…
Canada.ca pages where dataset is used --> append to open data  notes
ODIP - Date Pub --> unsure
Spatial/Non-Spatial --> new field needed
Review Dec 2018 --> append to notes
Openess Rating --> append to notes
"""


def import_file():
    with open(os.path.join(target_dir, "annette_open_data.csv"), 'r', encoding="utf8") as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        i = 0
        existing_records = 0
        for row in my_csv:
            # only start on row #2
            if i >= 1:


                # most important thing is to establish a uuid. I have verified that the On OGP field is a reliable way to get the uuid
                # i also verified that the best field to get the url / uuid would be row["Location (if yes):"]


                uuid_found = "https://open.canada.ca" in row["Location (if yes):"]

                if uuid_found:
                    uuid = row["Location (if yes):"].split("/")[-1]
                    # we will use the uuid as the basis for grabbing / creating a record
                    if models.Resource.objects.filter(uuid=uuid).count() > 1:
                        r, created = models.Resource.objects.get_or_create(uuid=uuid, notes="WARNING: Duplicate uuid in system.")
                    else:
                        r, created = models.Resource.objects.get_or_create(uuid=uuid)
                    if not created:
                        print("found matching uuid")
                        existing_records += 1

                # otherwise, using the odi_id is not a bad idea.
                else:

                    if models.Resource.objects.filter(title_eng__iexact=row["Dataset title English:"]).count() > 1:
                        r = models.Resource.objects.filter(title_eng__iexact=row["Dataset title English:"]).first()
                    else:
                        r, created = models.Resource.objects.get_or_create(title_eng__iexact=row["Dataset title English:"])
                    if not created:
                        print("found matching title")
                        existing_records += 1

                r.odi_id = row["\ufeffID"]

                # ok, now we have our full dataset nucleated in the db
                # let's tackle each row.

                # Dataset title English: --> good.
                # Dataset title French: --> good
                # Dataset description English: --> good
                # Dataset description French: --> good
                if created:
                    r.title_eng = row["Dataset title English:"]
                    r.title_fre = row["Dataset title French:"]
                    r.descr_eng = row["Dataset description English:"]
                    r.descr_fre = row["Dataset description French:"]

                # add the data owner
                # Data owner's name: --> owner
                # Data owner's email: --> owner email

                # if the email address is missing, means there is no custodian. Let's add annette for interim
                if "@" not in row["Data owner's email:"]:
                    my_user = get_create_user("Annette.Anthony@dfo-mpo.gc.ca")
                    my_role = models.PersonRole.objects.get(id=1)  # steward
                    print("there was no email, so adding annette instead.")
                else:
                    raw = row["Data owner's email:"].replace(" ", "").replace("\n", "")
                    # we will have to clean up the email address(es)
                    if "," in raw or ";" in raw:
                        if "," in raw:
                            emails = raw.split(",")
                        else:
                            emails = raw.split(";")
                    else:
                        emails = [raw, ]

                    # let's cycle through the emails
                    for email in emails:
                        if "@" in email:
                            my_user = get_create_user(email)
                            my_role = models.PersonRole.objects.get(id=1)  # owner
                            models.Person.objects.get_or_create(user=my_user)
                            models.ResourcePerson.objects.get_or_create(
                                resource=r,
                                person_id=my_user.id,
                                role=my_role
                            )

                if r.notes:
                    r.notes += "\n\n"
                else:
                    r.notes = ""  # to prime the field

                if r.open_data_notes:
                    r.open_data_notes += "\n\n"
                else:
                    r.open_data_notes = ""  # to prime the field

                if not "This record has been automatically imported" in r.notes:
                    r.notes += f'{timezone.now().strftime("%B %d, %Y")}: This record has been automatically imported into DM Apps from the Open Data Inventory. These notes will have to be cleaned up.'
                    r.notes += '-------------------------------------------------------------'

                # What is the date range of the dataset? --> needs to be digested. Very problematic though because of the use of hyphen
                field = "What is the date range of the dataset?"
                if not field in r.notes:
                    r.notes += "\n{} {}".format(field, row[field])

                # since the governance will not line up, let's just add this to notes
                # Data owner's region: -->
                # Data owner's sector: --> this will be tricky. Maybe we can create a generic section from each region based on this set.
                # Data owner's Directorate/Branch/Division: -->
                if not "Data owner's region" in r.notes:
                    r.notes += "\nData owner's region: {}".format(row["Data owner's region:"])
                    r.notes += "\nData owner's sector: {}".format(row["Data owner's sector:"])
                    r.notes += "\nData owner's Directorate/Branch/Division: {}".format(row["Data owner's Directorate/Branch/Division:"])

                # IT custodian's name:  --> messy.
                field = "IT custodian's name: "
                r.notes += "\n{} {}".format(field, row[field])

                # Date: --> what is this date?

                # Source/location of dataset:  --> need to parse this out and extract the uuid.
                if uuid_found and not r.public_url:
                    r.public_url = row["Source/location of dataset: "]
                else:
                    field = "Source/location of dataset: "
                    if not field in r.open_data_notes:
                        r.open_data_notes += "\n{} {}".format(field, row[field])

                # Location (if yes): --> These can be concatinated to open data notes
                field = "Location (if yes):"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # Location (French): -->
                field = "Location (French):"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # Corresponding Pub/Bib Record --> This can be appended to notes section but should be prefaced by: "needs to be properly added as a citation in the record"
                field = "Corresponding Pub/Bib Record"
                if not field in r.open_data_notes:
                    r.notes += "\n{}: {}".format(field, row[field])

                # Do you have a data quality process in place? --> appended to notes
                if not r.qc_process_descr_eng:
                    r.qc_process_descr_eng = "Do you have a data quality process in place? {}".format(
                        row["Do you have a data quality process in place?"])

                # Is/can the dataset be machine readable and platform independent? --> appended to notes
                field = "Is/can the dataset be machine readable and platform independent?"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # What is the current format of the source dataset? --> needs to be parse by data_distribution_formats.py
                field = "What is the current format of the source dataset?"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # What is the estimated volume of the dataset (in GB)? --> notes
                field = "What is the estimated volume of the dataset (in GB)?"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # What is the geographic coverage of the dataset? --> geo_descr_eng
                # Other, please describe: --> we can do a search here for bounding box. Otherwise can be appended to notes
                field = "What is the geographic coverage of the dataset?"
                field1 = "Other, please describe:"
                if not r.geo_descr_eng:
                    r.geo_descr_eng = "\n{} {}; {}".format(field, row[field], row[field1])

                # Is the data for this dataset derived from more than one source? --> notes
                field = "Is the data for this dataset derived from more than one source?"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # How often does the source data change? --> maintenance frequency…problem is split between two cols. If we concatenate then search for FK. If not found, append as note.
                # If "Other", please indicate time frame: -->
                field = "How often does the source data change?"
                field1 = 'If "Other", please indicate time frame:'
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}; {}".format(field, row[field], row[field1])

                # NOTES --> append to notes; may contain an FGP url…
                field = "NOTES"
                if not field in r.notes:
                    r.notes += "\n{} {}".format(field, row[field])

                # Canada.ca pages where dataset is used --> append to open data  notes
                field = "Canada.ca pages where dataset is used"
                if not field in r.notes:
                    r.notes += "\n{} {}".format(field, row[field])

                # ODIP - Date Pub --> unsure
                field = "ODIP - Date Pub"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # Spatial/Non-Spatial --> new field needed
                field = "Spatial/Non-Spatial"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{} {}".format(field, row[field])

                # Review Dec 2018 --> append to notes
                field = "Review Dec 2018"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{}: {}".format(field, row[field])

                # Openess Rating --> append to notes
                field = "Openess Rating"
                if not field in r.open_data_notes:
                    r.open_data_notes += "\n{}: {}".format(field, row[field])


                r.save()
                xml_export.verify(r)
                # How does the dataset link to DFO's Program Alignment Architecture (PAA)? --> need to create a new FK
                field = "How does the dataset link to DFO's Program Alignment Architecture (PAA)?"
                list1 = row[field].replace(";", ",").split(",")
                paa_code_list = [paa.code for paa in shared_models.PAAItem.objects.all()]
                for paa in list1:
                    my_code = paa.lstrip().split(" ")[0]
                    if my_code in paa_code_list:
                        r.paa_items.add(shared_models.PAAItem.objects.get(code=my_code))

            i += 1

    print(f"there were {existing_records} records already in the system")
    print(f"there were a total of {i} records processed")