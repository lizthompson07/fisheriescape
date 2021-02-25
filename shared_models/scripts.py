import csv
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core import serializers
from django.core.files import File

from lib.templatetags.custom_filters import nz
from . import models


def resave_sections():
    for s in models.Section.objects.all():
        s.save()


def save_and_add_uuid():
    model_list = [models.Region, models.Branch, models.Division, models.Section, models.Province]

    for model in model_list:
        for obj in model.objects.all():
            if not obj.uuid:
                obj.uuid = uuid.uuid4()
                obj.save()


def pad_codes():
    for port in models.Port.objects.all():
        if len(port.district_code) == 1:
            port.district_code = "0{}".format(port.district_code)
            port.save()
        if len(port.port_code) == 1:
            port.port_code = "0{}".format(port.port_code)
            port.save()


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.FiscalYear,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


#
# #
# #
# def get_file(request, file):
#     my_file = models.File.objects.get(pk=file)
#     blob_name = my_file.file
#
#     if settings.AZURE_STORAGE_ACCOUNT_NAME:
#         AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
#         token_credential = MSIAuthentication(resource=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net')
#         blobService = BlockBlobService(account_name=AZURE_STORAGE_ACCOUNT_NAME, token_credential=token_credential)
#         blobService.create_blob_from_path()
#         blob_file = blobService.get_blob_to_bytes("media", blob_name)
#         response = HttpResponse(blob_file.content, content_type='application/zip')
#         response['Content-Disposition'] = f'attachment; filename="{blob_name}"'
#     else:
#         response = HttpResponse(my_file.file.read(), content_type='application/zip')
#         response['Content-Disposition'] = f'attachment; filename="{blob_name}"'
#
#     return response


# def upload_mediafiles_to_blob():
#     block_blob_service = BlockBlobService(account_name='dmappsdev', account_key='')
#     container_name ='media'
#
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'travel')
#
#     for files in os.listdir(MEDIA_DIR):
#         block_blob_service.create_blob_from_path(container_name,files,os.path.join(local_path,files))


def __db_user_to_spreadsheet(obj, target_email, user_type, blank_spots_are_literal=False, commit=False):
    db_user = getattr(obj, user_type)  # e.g. region.head
    # if there is no email and we are meant to take this literally, we should clear the user in db table, if any
    if not target_email:  # doing this in two steps do create a deadend
        if blank_spots_are_literal and db_user:
            print(f"clearing user {db_user} from db.")
            setattr(obj, user_type, None)
        else:
            print(f"no email for {obj} listed on spreadsheet, but not taking action since blank spots are not to be taken literally. {db_user} is spared.")

    # there is an email from spreadsheet
    else:
        qs = User.objects.filter(email__iexact=target_email)
        # the user's email DOES NOT exists in the db
        if not qs.exists():
            first_name = target_email.split("@")[0].split(".")[0].title()
            last_name = target_email.split("@")[0].split(".")[1].title()
            target_user = User.objects.create(first_name=first_name, last_name=last_name, email=target_email, username=target_email, is_active=True)
        else:
            target_user = qs.first()

        # now that we have a user, we can make our final assessment in one go:
        if target_user != db_user:
            print(f"{target_user} is replacing {db_user} in {obj}.")
            setattr(obj, user_type, target_user)
        else:
            print(f"{target_user} is already in place for {obj} :)")

        if commit:
            obj.save()


def __get_create_object_from_uuid(my_model, uuid, name, nom, create=False, update=False):
    qs = my_model.objects.filter(uuid=uuid)

    if qs.exists():
        print(f'{my_model._meta.verbose_name} with uuid {uuid} found: {qs.first().name}')
        obj = qs.first()
    else:
        print(f'{my_model._meta.verbose_name} with uuid {uuid} NOT found: {qs.first().name}')
        if create:
            my_model.objects.create(uuid=uuid)



def import_users_from_org_sheet(blank_spots_are_literal=False, commit=False):
    import unidecode

    my_target_data_file = os.path.join(settings.BASE_DIR, 'shared_models', 'script_data', 'org_list_import_2021_02_24.csv')

    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # region
            region, created = models.Region.objects.get_or_create(uuid=row["region uuid"])
            # update the names
            region.name = row["region name"]
            region.nom = row["region nom"]
            region.save()

            # get the head and admin user from sheet
            ## head:
            email = nz(row["region head email"])  # old email, old user? ||  new email, old user? || new email, new user?

            if row["region admin"]:
                last_name = row["region admin"].split(" ")[-1]
                first_name = row["region admin"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not region.admin:
                    if qs.exists():
                        region.admin = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        region.admin = new_user
                    region.save()

            # branch
            qs = models.Branch.objects.filter(uuid=row["branch uuid"])
            if qs.exists():
                branch = qs.first()
            else:
                branch = models.Branch.objects.create(uuid=row["branch uuid"], region=region)

            # update the names
            branch.name = row["branch name"]
            branch.nom = row["branch nom"]
            branch.save()
            # get the head and admin user from sheet
            ## head:
            if row["branch head"]:
                last_name = row["branch head"].split(" ")[-1]
                first_name = row["branch head"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not branch.head:
                    if qs.exists():
                        branch.head = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        branch.head = new_user
                    branch.save()

            if row["branch admin"]:
                last_name = row["branch admin"].split(" ")[-1]
                first_name = row["branch admin"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not branch.admin:
                    if qs.exists():
                        branch.admin = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        branch.admin = new_user
                    branch.save()

            # division
            qs = models.Division.objects.filter(uuid=row["division uuid"])
            if qs.exists():
                division = qs.first()
            else:
                division = models.Division.objects.create(uuid=row["division uuid"], branch=branch)
            # update the names
            division.name = row["division name"]
            division.nom = row["division nom"]
            division.save()
            # get the head and admin user from sheet

            ## head:
            if row["division head"]:
                last_name = row["division head"].split(" ")[-1]
                first_name = row["division head"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not division.head:
                    if qs.exists():
                        division.head = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        division.head = new_user
                    division.save()

            if row["division admin"]:
                last_name = row["division admin"].split(" ")[-1]
                first_name = row["division admin"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not division.admin:
                    if qs.exists():
                        division.admin = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        division.admin = new_user
                    division.save()

            # section
            qs = models.Section.objects.filter(uuid=row["section uuid"])
            if qs.exists():
                section = qs.first()
            else:
                section = models.Section.objects.create(uuid=row["section uuid"], division=division)
            # update the names
            section.name = row["section name"]
            section.nom = row["section nom"]
            section.save()
            # get the head and admin user from sheet
            ## head:
            if row["section head"]:
                last_name = row["section head"].split(" ")[-1]
                first_name = row["section head"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not section.head:
                    if qs.exists():
                        section.head = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        section.head = new_user
                    section.save()

            if row["section admin"]:
                last_name = row["section admin"].split(" ")[-1]
                first_name = row["section admin"].replace(last_name, "").strip()
                # this will be used to determine if the user is already in the system
                qs = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
                # if the spreadsheet has no user assigned...
                if not section.admin:
                    if qs.exists():
                        section.admin = qs.first()
                    else:
                        email = f'{unidecode.unidecode(first_name)}.{unidecode.unidecode(last_name)}@dfo-mpo.gc.ca'
                        print("creating user:", first_name, last_name, email)
                        new_user = User.objects.create(first_name=first_name, last_name=last_name,
                                                       email=email, username=email,
                                                       is_active=True)
                        section.admin = new_user
                    section.save()
