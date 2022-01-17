import csv
import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import make_aware
from pytz import utc

from csas2 import models
from csas2.models import CSASRequest, CSASRequestReview, Process
from shared_models.models import Section, Region


def resave_requests():
    for r in CSASRequest.objects.all():
        r.save()


def resave_processes():
    for p in Process.objects.all():
        p.save()


def clean_up_reviews():
    for review in CSASRequestReview.objects.filter(decision__in=[2, 3, 4]):
        if review.decision == 3:
            review.decision = 2
        elif review.decision == 2:
            if review.notes:
                review.notes += "; Review was originally set to 'off'"
            else:
                review.notes = "Review was originally set to 'off'"
        elif review.decision == 4:
            review.decision = None
            if review.notes:
                review.notes += "; Review was originally set to 'deferred'"
            else:
                review.notes = "Review was originally set to 'deferred'"
        review.save()


def digest_csv():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'csas2', 'csas_import.csv')
    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        i = 1
        for row in my_csv:
            print(i)
            for key in row:
                row[key] = row[key].strip()
                if row[key].strip() == "":
                    row[key] = None

            # first thing is to check whether there is a matching reference ID in the system...
            ref = row["ID"]
            qs = models.CSASRequestReview.objects.filter(ref_number=ref)

            r = None
            if ref:
                if qs.exists() and qs.count() == 1:
                    r = qs.first().csas_request
                elif qs.exists():
                    print(f"warning ref number {ref} has multiple matches")

            now = timezone.now()
            title = row["Title"]
            if title:
                # coord
                office_region = Region.objects.get(name__iexact=row["CsasOffice"])
                office_qs = models.CSASOffice.objects.filter(region=office_region)
                if office_qs.exists():
                    office = office_qs.first()
                else:
                    laura = User.objects.get(email__iexact="laura.ferris@dfo-mpo.gc.ca")
                    office = models.CSASOffice.objects.create(region=office_region, coordinator=laura)

                # client
                email = row["Email"].lower().strip()
                try:
                    client = User.objects.get(email__iexact=email)
                except:
                    first_name = email.split("@")[0].split(".")[0].title()
                    last_name = email.split("@")[0].split(".")[1].title()
                    client = User.objects.create(
                        username=email,
                        first_name=first_name,
                        last_name=last_name,
                        password="",
                        is_active=True,
                        email=email,
                    )

                # section
                section = Section.objects.get(uuid=row["section_uuid"])
                zonal = True if row['Zonal'] and row['Zonal'].lower() == "yes" else False
                zonal_text = row['ZonalText']
                issue = row['TheQuestion']
                assistance_text = row['AssistanceText']
                rationale = row['RationaleForContextText']
                risk_text = row['ConsequenceText']
                timeline_text = row['RationaleForDeadlineText']
                funds = True if row['Funds'] and row['Funds'].lower() == "yes" else False
                funds_text = row['FundsText']
                date = datetime.datetime.strptime(row['AdviceDate'] + " 12:00", "%m/%d/%Y %H:%M")
                date = make_aware(date, utc)

                submission_date = None
                if row['SubmissionDate']:
                    submission_date = datetime.datetime.strptime(row['SubmissionDate'] + " 12:00", "%m/%d/%Y %H:%M")
                    submission_date = make_aware(submission_date, utc)

                # first determine if a request exists with the same title
                created = False
                if not r:
                    qs = models.CSASRequest.objects.filter(title=title, advice_needed_by=date)
                    if not qs.exists():
                        created = True
                        r = models.CSASRequest.objects.create(
                            title=title,
                            office=office,
                            client=client,
                            section=section,
                            is_multiregional=zonal,
                            multiregional_text=zonal_text,
                            issue=issue,
                            assistance_text=assistance_text,
                            rationale=rationale,
                            risk_text=risk_text,
                            rationale_for_timeline=timeline_text,
                            has_funding=funds,
                            funding_text=funds_text,
                            advice_needed_by=date,
                            old_id=9999,
                            submission_date=submission_date,
                        )
                    else:
                        r = qs.first()

                if not created:
                    r.office = office
                    r.client = client
                    r.section = section
                    r.is_multiregional = zonal
                    r.multiregional_text = zonal_text
                    r.issue = issue
                    r.assistance_text = assistance_text
                    r.rationale = rationale
                    r.risk_text = risk_text
                    r.rationale_for_timeline = timeline_text
                    r.has_funding = funds
                    r.funding_text = funds_text
                    r.submission_date = submission_date
                    r.save()

                #if there is a reference ID, we will create a review
                if ref:
                    review, created = models.CSASRequestReview.objects.get_or_create(ref_number=ref, csas_request=r)
                    if created:
                        print(f"creating a review for {r} with ref id: {ref}")
            i += 1


def check_tor():
    for p in Process.objects.all():
        p.save()
        tor = p.tor
        requests = p.csas_requests.all()
        if requests.exists():
            r = requests.first()
            if r.language == 2:
                if not tor.context_fr:
                    tor.context_fr = r.issue
                if not tor.objectives_fr:
                    tor.objectives_fr = r.rationale
            else:
                if not tor.context_en:
                    tor.context_en = r.issue
                if not tor.objectives_en:
                    tor.objectives_en = r.rationale
            tor.save()
