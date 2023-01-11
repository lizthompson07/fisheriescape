import datetime
import os
import uuid

import pandas as pd
from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import get_current_timezone, make_aware

from csas2.models import Process, ProcessNote, Document, CSASOffice, DocumentType, DocumentNote, Meeting, MeetingNote
from shared_models.models import FiscalYear

data_dir = os.path.join(settings.BASE_DIR, 'csas2', 'scripts', 'data')

files = ['csas_meetings.csv',
         'csas_publication_predates_schedule.csv',
         'csas_publications_with_multiple_meetings.csv',
         'csas_publications_with_one_meeting.csv'
         ]

csas_meetings: pd.DataFrame


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

    print("Import Publications that predate schedule")
    # the step below only required now . should make process null
    predates_process = get_or_create_predates_process(1977)
    publications = pd.read_csv(os.path.join(data_dir, 'csas_publication_predates_schedule.csv'))
    additional_notes = "This publication predates the DFO science advisory schedule. Cette publication précède le " \
                       "calendrier des conseils scientifiques du MPO. "

    for index, row in publications.iterrows():
        # replace nan values with None
        row = row.where(pd.notnull(row), None)
        row_dict = row.to_dict()
        create_document(row_dict, predates_process, additional_note=additional_notes)

    print("Import Publications with multiple meetings")
    # here we will create a process based off the first meeting id, then all other
    # meetings will be added to that process. This has to run before the single meeting
    # as the first meeting will be used to create the process
    publications = pd.read_csv(os.path.join(data_dir, 'csas_publications_with_multiple_meetings.csv'))

    for index, row in publications.iterrows():
        # replace nan values with None
        pub = row.where(pd.notnull(row), None)
        pub_dict = pub.to_dict()

        # get all meeting ids as int from the PeerReviewMtg1 column, separated by a semicolon
        meeting_ids = [int(x) for x in row['PeerReviewMtg1'].split(';')]
        # create a process based off the first meeting id
        process = get_or_create_process(meeting_ids[0], pub_dict)
        if process is None:
            print(f"Could not create process for {meeting_ids[0]}")
            continue
        # create all meetings
        meetings: [Meeting] = []
        for meeting_id in meeting_ids:
            # add the other meetings to the process
            meeting = get_or_create_meeting(process, meeting_id)
            if meeting is not None:
                meetings.append(meeting)
            else:
                print(f"Could not create meeting for id {meeting_id}")

        # create the document
        create_document(pub_dict, process, meetings=meetings)

    print("Import Publications with one meeting")
    publications = pd.read_csv(os.path.join(data_dir, 'csas_publications_with_one_meeting.csv'))
    for index, row in publications.iterrows():
        # replace nan values with None
        pub = row.where(pd.notnull(row), None)
        pub_dict = pub.to_dict()

        # get the meeting id as int from the PeerReviewMtg1 column
        meeting_id = int(row['PeerReviewMtg1'])
        # create a process based off the meeting id
        process = get_or_create_process(meeting_id, pub_dict)
        if process is None:
            print(f"Could not create process for {meeting_id}")
            continue
        # create the meeting
        meeting = get_or_create_meeting(process, meeting_id)
        if meeting is None:
            print(f"Could not create meeting for id {meeting_id}")
            continue

        # create the document
        create_document(pub_dict, process, meetings=[meeting])

    print("Done")


def check_import_files() -> bool:
    print("Checking import files exist")
    valid = True
    for file in files:
        if not os.path.exists(os.path.join(data_dir, file)):
            print(f"File {os.path.join(data_dir, file)} does not exist")
            valid = False
    return valid


def get_or_create_process(id_schedule: int, publication: dict) -> Process or None:
    """
    Get or create a process based on the schedule id
    """
    meeting = find_meeting_by_id(id_schedule)
    if meeting is None:
        print(f"Create Process: Could not find meeting with idSchedule {id_schedule}")
        return None

    # get the lead office
    lead_office = get_lead_region_office(publication['LeadRegion'])
    if lead_office is None:
        print(f"Create Process: Could not find lead office for {publication['LeadRegion']}")
        return None

    # get the fiscal year
    date = parse_datetime(meeting['Start Date'])
    fiscal_year = get_fiscal_year(date)
    if fiscal_year is None:
        print(f"Could not find fiscal year for {date}")
        return None

    process_args = {
        'status': 20,  # ON by default
        'lead_office_id': lead_office.id,
        'fiscal_year_id': fiscal_year.id,
        'has_peer_review_meeting': True,
        'has_planning_meeting': False,
        'scope': get_process_scope(meeting['Scope']),
        'type': get_process_type(meeting['Advisory']),
        'name': meeting['Subject Eng'],
        'nom': meeting['Subject Fra'],
        'advice_date': date,
        'created_by_id': get_default_created_by(),
    }

    # check if the process already exists
    try:
        process = Process.objects.get(name=process_args['name'], fiscal_year_id=process_args['fiscal_year_id'])
        return process
    except Process.DoesNotExist:
        # create the process
        process = Process(**process_args)
        process.save()

    # add the meeting contacts as a ProcessNote
    note = f"Process generated from legacy data import. Contacts: {meeting['Contact']}"
    ProcessNote.objects.create(
        process_id=process.id,
        note=note,
        type=1,  # general
        created_by_id=get_default_created_by(),
    )

    return process


def get_or_create_meeting(process: Process, id_schedule: int) -> Meeting or None:
    """
    Get or create a meeting based on the schedule id
    """
    import_meeting = find_meeting_by_id(id_schedule)
    if import_meeting is None:
        print(f"Create meeting: Could not find meeting with idSchedule {id_schedule}")
        return None

    # get the fiscal year
    start_date = parse_datetime(import_meeting['Start Date'])
    fiscal_year = get_fiscal_year(start_date)
    if fiscal_year is None:
        print(f"Create meeting: Could not find fiscal year for {start_date}")
        return None

    # is virtual meeting?
    is_virtual = False
    if import_meeting['Location Eng'] == 'Virtual Meeting':
        is_virtual = True

    meeting_args = {
        'process_id': process.id,
        'name': import_meeting['Subject Eng'],
        'nom': import_meeting['Subject Fra'],
        'start_date': start_date,
        'end_date': parse_datetime(import_meeting['End Date']),
        'location': import_meeting['Location Eng'],
        'is_virtual': is_virtual,
        'is_planning': False,
        'is_estimate': False,
        'is_posted': True,
        'has_media_attention': import_meeting['MediaLines'],
        'is_somp_submitted': True,
        'fiscal_year_id': fiscal_year.id,
        'chair_comments': import_meeting['ChairComment'],
        'created_by_id': get_default_created_by(),
    }

    # check if the meeting already exists
    try:
        meeting = Meeting.objects.get(name=meeting_args['name'], fiscal_year_id=meeting_args['fiscal_year_id'])
        return meeting
    except Meeting.DoesNotExist:
        # create the meeting
        meeting = Meeting(**meeting_args)
        meeting.save()

    # add the meeting contacts as a MeetingNote
    note = f"Meeting generated from legacy data import. Contacts: {import_meeting['Contact']}"
    MeetingNote.objects.create(
        meeting_id=meeting.id,
        note=note,
        type=1,  # general
        created_by_id=get_default_created_by(),
    )

    return meeting


def create_document(publication: dict, process: Process = None, additional_note: str = None,
                    meetings: [Meeting] = None) -> Document:
    # safety check - if the publication already exists, via old_id, then skip
    if Document.objects.filter(old_id=publication['Hidden ID Publication']).exists():
        print(f"Publication {publication['Hidden ID Publication']} already exists - skipping")
        return None

    # get the document type
    document_type = get_or_create_document_type(publication['Series'])
    if document_type is None:
        print(f"Create Document: Could not find document type for {publication['Series']}")
        try:
            document_type = DocumentType.objects.get(name__iexact="Working Paper")
        except DocumentType.DoesNotExist:
            print("Could not find default document type")
            return None

    # get the lead office
    lead_office = get_lead_region_office(publication['LeadRegion'])
    if lead_office is None:
        print(f"Create Document: Could not find lead office for {publication['LeadRegion']}")
        try:
            lead_office = CSASOffice.objects.get(region__name="National")
        except CSASOffice.DoesNotExist:
            print("Could not find default lead office")
            return None

    # publication number
    publication_number = f"{publication['Series']} {int(publication['ID_Year'] or 0)}/{publication['ID_Code']}"

    # create the document
    document_args = {
        "translation_status": 3,  # Translated, reviewed
        "document_type_id": document_type.id,  # default to "Working Paper"
        "process_id": process.id,
        "is_confirmed": True,
        "status": get_document_status(publication['DOCUMENT STATUS']),  # defaults to "Confirmed"
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
        "created_by_id": get_default_created_by(),
        "lead_office_id": lead_office.id,  # default to CSAS office - NCR
        "pub_number": publication_number,
    }

    try:
        document = Document.objects.create(**document_args)
    except IntegrityError:
        # generate a uuid and try again
        document_args['pub_number'] = f"{publication_number} {uuid.uuid4()}"
        document = Document.objects.create(**document_args)

    # add the author list to a DocumentNote
    if publication['Authors'] is not None:
        note = f"Authors: {publication['Authors']}"
        DocumentNote.objects.create(
            document_id=document.id,
            note=note,
            type=2,  # to do type
            created_by_id=get_default_created_by(),
        )

    # add the additional note to a DocumentNote
    if additional_note is not None:
        DocumentNote.objects.create(
            document_id=document.id,
            note=additional_note,
            type=1,  # general information type
            created_by_id=get_default_created_by(),
        )

    if meetings is not None:
        # attach meeting to the documents many to many field
        document.meetings.add(*meetings)

    return document


def get_or_create_predates_process(fiscal_year_id: int) -> Process:
    """
    Create the predates process - this is the process
    that will be used for all documents that predate the schedule
    """

    # parse date
    date = parse_datetime(f"{fiscal_year_id}-01-01")

    process_args = {
        "name": "Process for publications that predate schedule",
        "nom": "Processus pour les publications qui précèdent le calendrier",
        "status": 100,
        "scope": 3,
        "type": 1,
        "advice_date": date,  # this will also set FY through model's save method
        "lead_office_id": 2,
    }

    try:
        process = Process.objects.get(name=process_args['name'], fiscal_year_id=fiscal_year_id)
    except Process.DoesNotExist:
        process = Process.objects.create(**process_args)

    return process


def get_process_scope(scope: str) -> int:
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


def get_process_type(process_type: str) -> int:
    """
    Get the process type choice based on the string
    TODO - Laura wants to add more types here.
    Existing types in import data are, only two (*) of them mapped:
        Peer Review
        (*) Advisory Meeting -> Science Advisory Meeting
        Internal Workshop
        Bi-Lateral Peer Review
        Workshop
        Review of Past Advice
        Open Workshop
        Ad Hoc Review
        Science Special Response Process (SSRP)
        (*) Science Response Process (SRP) -> Science Response Process
    """
    if process_type == "Advisory Meeting":
        return 1
    else:
        return 2


def get_or_create_document_type(abbrev: str) -> DocumentType or None:
    import_map = [
        {'import': 'RES', 'name': 'Research Document', 'nom': 'Document de recherche'},
        {'import': 'PRO', 'name': 'Proceedings', 'nom': 'Comptes rendus'},
        {'import': 'SSR', 'name': 'Stock Status Report', 'nom': 'Rapport sur l’état des stocks'},
        {'import': 'ESR', 'name': 'Ecosystem Status Report', 'nom': 'Rapport sur l’état des écosystèmes'},
        {'import': 'HSR', 'name': 'Habitat Status Report', 'nom': 'Rapport sur l’état des habitats'},
        {'import': 'SRR-RS', 'name': 'Science Response', 'nom': 'Réponse des Sciences'},
        {'import': 'SAR-AS', 'name': 'Science Advisory Report', 'nom': 'Avis scientifique'},
    ]

    # lookup if given name exits in map "import" field
    for item in import_map:
        if abbrev == item['import']:
            try:
                return DocumentType.objects.get(name__iexact=item['name'])
            except DocumentType.DoesNotExist:
                return DocumentType.objects.create(
                    name=item['name'],
                    nom=item['nom'],
                    hide_from_list=False)

    # if not found, return None
    return None


def get_document_status(status: str) -> int:
    """
    Get the document status choice based on the string, defaults to 1 (Confirmed)
    if not found.
    """
    if status == "PUBLISHED":
        return 12 # Posted
    elif status == "WITHDRAWN":
        return 1 # Confirmed : todo - should be withdrawn but option does not exist
    elif status == "Not yet submitted":
        return 1 # Confirmed
    elif status == "Submitted: in progress":
        return 9 # Submitted to CSAS office
    elif status == "Ready for Posting":
        return 11 # Proof approved by author
    else:
        print(f"Unknown status: {status}")
        return 1 # Confirmed


def get_lead_region_office(abbrev: str) -> CSASOffice or None:
    """
    Get the lead office for the given region
    """
    import_map = [
        {'import': 'QC', 'name': 'Quebec'},
        {'import': 'O&P', 'name': 'Ontario and Prairie'},
        {'import': 'PAC', 'name': 'Pacific'},
        {'import': 'MAR', 'name': 'Maritimes'},
        {'import': 'GLF', 'name': 'Gulf'},
        {'import': 'NCR', 'name': 'National'},
        {'import': 'C&A', 'name': 'Ontario and Prairie'},
        # todo: send to O&P for now; laura would like to add "Central and Arctic" to the list of regions
        {'import': 'NL', 'name': 'Newfoundland & Labrador'},
    ]

    for item in import_map:
        if abbrev == item['import']:
            try:
                return CSASOffice.objects.get(region__name=item['name'])
            except CSASOffice.DoesNotExist:
                return None

    return None


def find_meeting_by_id(id_schedule: int) -> pd.Series or None:
    """
    Find a meeting by its ID
    """
    global csas_meetings

    meeting = csas_meetings[csas_meetings['ID_Schedule'] == id_schedule]
    if len(meeting) == 0:
        print(f"Could not find meeting with idSchedule {id_schedule}")
        return None
    else:
        meeting = meeting.iloc[0]
        # replace nan values with None
        meeting = meeting.where(pd.notnull(meeting), None)
        return meeting


def get_default_created_by() -> int:
    return 1142  # Laura Ferris uid is 1142


def parse_datetime(date: str) -> datetime or None:
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
