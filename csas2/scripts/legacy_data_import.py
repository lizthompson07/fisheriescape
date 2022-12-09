import os
import datetime
import pandas as pd
import numpy as np

from django.conf import settings
from django.utils.timezone import get_current_timezone, make_aware

from shared_models.models import FiscalYear, Region
from csas2.models import CSASRequest, CSASRequestReview, Process, Document, CSASOffice, DocumentType, DocumentNote


data_dir = os.path.join(settings.BASE_DIR, 'csas2', 'scripts', 'data')

files = ['csas_meetings.csv',
         'csas_publication_predates_schedule.csv',
         'csas_publications_with_multiple_meetings.csv',
         'csas_publications_with_one_meeting.csv'
         ]

def run():
    print("Importing legacy data")

    if check_import_files():
        print("All files exist")
    else:
        print("Missing files - stopping")
        return

    print("Import Publications that predate schedule")
    predates_process = get_or_create_predates_process()

    publications = pd.read_csv(os.path.join(data_dir, 'csas_publication_predates_schedule.csv'))
    for index, row in publications.iterrows():
        create_document(row, predates_process)

    print("Done")


def check_import_files() -> bool:
    print("Checking import files exist")
    valid = True
    for file in files:
        if not os.path.exists(os.path.join(data_dir, file)):
            print(f"File {os.path.join(data_dir, file)} does not exist")
            valid = False
    return valid


def create_document(publication: dict, process: Process = None) -> Document:


    # create the document
    document_args = {
        "translation_status": 3,
        "document_type_id": get_document_type(publication['Series']).id or 1,
        "process_id": process.id,
        "is_confirmed": True,
        "status": 12,
        "title_en": publication['Title_English'],
        "title_fr": publication['Titre_français'],
        "old_id": publication['Hidden ID Publication'],
    }

    document = Document.objects.create(**document_args)

    return document



def get_or_create_predates_process() -> Process:
    """
    Create the predates process
    """
    print("Creating predates process")

    process_args = {
        "name": "Process for publications that predate schedule",
        "nom": "Processus pour les publications qui précèdent le calendrier",
        "status": 100,
        "scope": 3,
        "type": 1,
        "advice_date": parseDatetime("2019-04-01"), # this will also set FY through model's save method
        "lead_office_id": 2,
    }

    try:
        process = Process.objects.get(name__iexact=process_args['name'])
    except Process.DoesNotExist:
        process = Process.objects.create(**process_args)

    return process


def get_fiscal_year(date: datetime) -> FiscalYear or None:
    year = date.year
    if date.month >= 4:
        fy = '{0}-{1}'.format(year, year + 1)
    else:
        fy = '{0}-{1}'.format(year - 1, year)
    try:
        return FiscalYear.objects.get(full=fy)
    except FiscalYear.DoesNotExist:
        return None


def get_document_type(name: str) -> DocumentType:
    try:
        return DocumentType.objects.get(name__iexact=name)
    except DocumentType.DoesNotExist:
        return None


def parseDatetime(date: str) -> datetime or None:
    """
    Parse a date string into a datetime object
    Expected format: YYYY-MM-DD
    """
    try:
        return make_aware(datetime.datetime.strptime(f"{date} 12:00", '%Y-%m-%d %H:%M'), get_current_timezone())
    except ValueError:
        return None


# Nothing to do with import - just for testing


def create_csas_offices():

    # check we're not in production
    if not settings.DEBUG:
        return

    """
    Create the CSAS offices - only to be run when the database is empty.
    For testing purposes.
    """
    print("Creating CSAS Offices")
    offices = [
        'Gulf',
        'Maritimes',
        'National',
        'Pacific',
        'Quebec',
        'Newfoundland and Labrador',
        'Ontario and Prairie'
    ]


    region_args = {
       "abbrev": 'abbrv',
    }

    # create Regions from the list of offices
    for office in offices:
        region = Region.objects.get_or_create(name=office, **region_args)[0]
        region.save()

    office_args = {
        'generic_email': 'genericEmail@test.com',
        'coordinator_id': 1,
    }

    for office in offices:
        region = Region.objects.get(name__iexact=office)
        try:
            CSASOffice.objects.get(region_id = region.id)
        except CSASOffice.DoesNotExist:
            CSASOffice.objects.create(region_id=region.id, **office_args)


def create_document_types():
    """
    Create the document types - only to be run when the database is empty.
    For testing purposes.
    """

    # check we're not in production
    if not settings.DEBUG:
        return

    print("Creating Document Types")
    types = [
        'RES',
        'SSR',
        'SAR-AS',
        'ESR',
        'HSR',
        'PRO',
        'SRR-RS',
        'PSARCwp',
    ]

    for type in types:
        try:
            DocumentType.objects.get(name__iexact=type)
        except DocumentType.DoesNotExist:
            DocumentType.objects.create(name=type)