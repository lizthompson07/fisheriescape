import math
import os
import datetime
import pandas as pd
import random

from django.db import IntegrityError
from django.conf import settings
from django.utils.timezone import get_current_timezone, make_aware

from shared_models.models import FiscalYear
from csas2.models import Process, Document, CSASOffice, DocumentType, DocumentNote, Meeting


data_dir = os.path.join(settings.BASE_DIR, 'csas2', 'scripts', 'data')

files = ['csas_meetings.csv',
         'csas_publication_predates_schedule.csv',
         'csas_publications_with_multiple_meetings.csv',
         'csas_publications_with_one_meeting.csv'
         ]

csas_meetings: pd.DataFrame = None
def run():
    print("Importing legacy data")

    if check_import_files():
        print("All files exist")
    else:
        print("Missing files - stopping")
        return

    print("Load meeting data file")
    global csas_meetings
    csas_meetings = pd.read_csv(os.path.join(data_dir, 'csas_meetings.csv'))

    # print("Import Publications that predate schedule")
    # # the step below only required now .. should make process null
    # predates_process = get_or_create_predates_process(1977)
    # publications = pd.read_csv(os.path.join(data_dir, 'csas_publication_predates_schedule.csv'))
    # additional_notes = "This publication predates the DFO science advisory schedule. Cette publication précède le calendrier des conseils scientifiques du MPO."
    # for index, row in publications.iterrows():
    #     # replace nan values with None
    #     row = row.where(pd.notnull(row), None)
    #     row_dict = row.to_dict()
    #     create_document(row_dict, predates_process, additional_note=additional_notes)


    print("Import Publications with multiple meetings")
    # here we will create a process based off the first meeting id, then all other
    # meetings will be added to that process
    publications = pd.read_csv(os.path.join(data_dir, 'csas_publications_with_multiple_meetings.csv'))
    for index, row in publications.iterrows():
        # replace nan values with None
        pub = row.where(pd.notnull(row), None)
        pub_dict = pub.to_dict()

        # get all meeting ids as int from the PeerReviewMtg1 column, separated by a semicolon
        meeting_ids = [int(x) for x in row['PeerReviewMtg1'].split(';')]
        # create a process based off the first meeting id
        process = get_or_create_process(meeting_ids[0], pub_dict)
        return


    print("Done")


def check_import_files() -> bool:
    print("Checking import files exist")
    valid = True
    for file in files:
        if not os.path.exists(os.path.join(data_dir, file)):
            print(f"File {os.path.join(data_dir, file)} does not exist")
            valid = False
    return valid


def get_or_create_process(idSchedule: int, publication: dict) -> Process or None:
    """
    Get or create a process based on the schedule id
    """
    global csas_meetings

    meeting = csas_meetings[csas_meetings['ID_Schedule'] == idSchedule]
    if len(meeting) == 0:
        print(f"Could not find meeting with idSchedule {idSchedule}")
        return None
    else:
        meeting = meeting.iloc[0]
        # replace nan values with None
        meeting = meeting.where(pd.notnull(meeting), None)

    # get the lead office
    lead_office = get_lead_region_office(publication['LeadRegion'])
    if lead_office is None:
        print(f"Could not find lead office for {publication['LeadRegion']}")
        return None

    # get the fiscal year
    date = parseDatetime(meeting['Start Date'])
    fiscal_year = get_fiscal_year(date)
    if fiscal_year is None:
        print(f"Could not find fiscal year for {date}")
        return None


    process_args = {
        'status': 20, # ON by default
        'lead_office_id': lead_office.id,
        'fiscal_year_id': fiscal_year.id,
        'has_peer_review_meeting': True,
        'has_planning_meeting': False,
    }


    print(f"Creating process for {date}")
    print(f"FY: {fiscal_year}")
    print(f"Lead Office: {lead_office}")

    print(meeting)


def create_document(publication: dict, process: Process = None, additional_note: str = None) -> Document:


    # safety check - if the pubcalition alreay exists, via old_id, then skip
    if Document.objects.filter(old_id=publication['Hidden ID Publication']).exists():
        print(f"Publication {publication['Hidden ID Publication']} already exists - skipping")
        return None

    # get the document type
    document_type = get_or_create_document_type(publication['Series'])
    if(document_type is None):
        print(f"Could not find document type for {publication['Series']}")
        try:
            document_type = DocumentType.objects.get(name__iexact="Working Paper")
        except DocumentType.DoesNotExist:
            print("Could not find default document type")
            return None

    # get the lead office
    lead_office = get_lead_region_office(publication['LeadRegion'])
    if(lead_office is None):
        print(f"Could not find lead office for {publication['LeadRegion']}")
        try:
            lead_office = CSASOffice.objects.get(region__name="National")
        except CSASOffice.DoesNotExist:
            print("Could not find default lead office")
            return None

    # publication number
    publication_number = f"{publication['Series']} {int(publication['ID_Year'])}/{publication['ID_Code']}"

    # create the document
    document_args = {
        "translation_status": 3, # Translated, reviewed
        "document_type_id": document_type.id, # default to "Working Paper"
        "process_id": process.id,
        "is_confirmed": True,
        "status": 12, # Posted
        "title_en": publication['Title_English'],
        "title_fr": publication['Titre_français'],
        "old_id": publication['Hidden ID Publication'],
        "pages_en": publication['Pagination'],
        "pages_fr": publication['Pagination_F'],
        "pdf_size_kb_en": publication['Pdf_Size'],
        "pdf_size_kb_fr": publication['Pdf_Size_F'],
        "url_en": publication['Link_Pdf_English'],
        "url_fr": publication['Link_Pdf_français'],
        "ekme_gcdocs_en": publication['EKME._E'],
        "ekme_gcdocs_fr": publication['EKME._F'],
        "created_by_id": getDefaultCreatedBy(),
        "lead_office_id": lead_office.id, # default to CSAS office - NCR
        "pub_number": publication_number,
    }

    try:
        document = Document.objects.create(**document_args)
    except IntegrityError as e:
        print(f"Document {publication_number} already exists - adding suffix")
        #random two char suffix
        suffix = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(2))
        document_args['pub_number'] = f"{publication_number}-{suffix}"
        document = Document.objects.create(**document_args)



    # add the author list to a DocumentNote
    if publication['Authors'] is not None:
        note = f"Authors: {publication['Authors']}"
        DocumentNote.objects.create(
            document_id=document.id,
            note=note,
            type=2, # to do type
            created_by_id=getDefaultCreatedBy(),
        )

    # add the additional note to a DocumentNote
    if additional_note is not None:
        DocumentNote.objects.create(
            document_id=document.id,
            note=additional_note,
            type=1, # general information type
            created_by_id=getDefaultCreatedBy(),
        )

    return document



def get_or_create_predates_process(fiscalYearId: int) -> Process:
    """
    Create the predates process - this is the process
    that will be used for all documents that predate the schedule
    """

    # parse date
    date = parseDatetime(f"{fiscalYearId}-01-01")
    print(f"Creating predates process for {date}")

    process_args = {
        "name": "Process for publications that predate schedule",
        "nom": "Processus pour les publications qui précèdent le calendrier",
        "status": 100,
        "scope": 3,
        "type": 1,
        "advice_date": date, # this will also set FY through model's save method
        "lead_office_id": 2,
    }

    try:
        process = Process.objects.get(name=process_args['name'], fiscal_year_id=fiscalYearId)
    except Process.DoesNotExist:
        print(f"Creating predates process: {fiscalYearId}")
        process = Process.objects.create(**process_args)

    return process


def get_process_scope_choie(scope: str) -> int:
    """
    Get the process scope choice based on the string
    """
    if scope == "National":
        return 3
    elif scope == "Zonal":
        return 2
    elif scope == "Regional":
        return 1
    else:
        return 1


def get_process_type_choie(type: str) -> int:
    """
    Get the process type choice based on the string
    """
    if type == "Advisory Meeting":
        return 1
    else:
        return 2


def get_or_create_document_type(abbrev: str) -> DocumentType or None:

    map = [
        {'import': 'RES', 'name': 'Research Document', 'nom': 'Document de recherche'},
        {'import': 'PRO', 'name': 'Proceedings', 'nom': 'Comptes rendus'},
        {'import': 'SSR', 'name': 'Stock Status Report', 'nom': 'Rapport sur l’état des stocks'},
        {'import': 'ESR', 'name': 'Ecosystem Status Report', 'nom': 'Rapport sur l’état des écosystèmes'},
        {'import': 'HSR', 'name': 'Habitat Status Report', 'nom': 'Rapport sur l’état des habitats'},
        {'import': 'SSR-RS', 'name': 'Science Response', 'nom': 'Réponse des Sciences'},
        {'import': 'SAR-AS', 'name': 'Science Advisory Report', 'nom': 'Avis scientifique'},
    ]

    # lookup if given name exits in map "import" field
    for item in map:
        if abbrev == item['import']:
            try:
                return DocumentType.objects.get(name__iexact=item['name'])
            except DocumentType.DoesNotExist:
                return DocumentType.objects.create(
                    name=item['name'],
                    nom=item['nom'],
                    hide_from_list=True)

    # if not found, return None
    return None

def get_lead_region_office(abbrev: str) -> CSASOffice or None:
    """
    Get the lead office for the given region
    """
    map = [
        {'import': 'QC', 'name': 'Quebec'},
        {'import': 'O&P', 'name': 'Ontario and Prairie'},
        {'import': 'PAC', 'name': 'Pacific'},
        {'import': 'MAR', 'name': 'Maritimes'},
        {'import': 'GLF', 'name': 'Gulf'},
        {'import': 'NCR', 'name': 'National'},
        {'import': 'C&A', 'name': 'Ontario and Prairie'}, #todo: send to O&P for now; laura would like to add "Central and Arctic" to the list of regions
        {'import': 'NL', 'name': 'Newfoundland & Labrador'},
    ]

    for item in map:
        if abbrev == item['import']:
            try:
                return CSASOffice.objects.get(region__name=item['name'])
            except CSASOffice.DoesNotExist:
                return None

    return None

def getDefaultCreatedBy() -> int:
    return 1142 # Laura Ferris uid is 1142

def parseDatetime(date: str) -> datetime or None:
    """
    Parse a date string into a datetime object
    Expected format: YYYY-MM-DD
    """
    try:
        return make_aware(datetime.datetime.strptime(f"{date} 12:00", '%Y-%m-%d %H:%M'), get_current_timezone())
    except ValueError:
        return None


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
