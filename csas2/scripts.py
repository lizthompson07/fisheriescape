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
from lib.templatetags.custom_filters import nz
from shared_models.models import Section


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
        for row in my_csv:
            now = timezone.now()

            # title
            title = nz(row["Title"], None)
            if title:
                # coord
                coord = User.objects.get(email__iexact="laura.ferris@dfo-mpo.gc.ca")

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
                        password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
                        is_active=True,
                        email=email,
                    )

                # section
                section_text = row["section"].strip()
                section_uuid = row["section_uuid"].strip()

                qs = Section.objects.filter(uuid=section_uuid)
                if not qs.exists():
                    print("PROBLEM!! We are missing the section with the following uuid: ", section_uuid)
                else:
                    section = qs.first()

                    zonal = True if row['Zonal'].lower() == "yes" else False
                    zonal_text = row['ZonalText']
                    issue = row['TheQuestion']
                    assistance = True if row['Assistance'].lower() == "yes" else False
                    assistance_text = row['AssistanceText']
                    rationale = row['RationaleOrContextText']
                    risk_text = row['ConsequenceIfAdviceNotProvidedText']
                    timeline_text = row['RationaleForDeadlineText']
                    funds = True if row['Funds'] and row['Funds'].lower() == "yes" else False
                    funds_text = row['FundsText']
                    date = datetime.datetime.strptime(row['date'] + " 12:00", "%m/%d/%Y %H:%M")
                    date = make_aware(date, utc)

                    # first determine if a request exists with the same title
                    qs = models.CSASRequest.objects.filter(title=title, advice_needed_by=date)
                    if not qs.exists():
                        r = models.CSASRequest.objects.create(
                            title=title,
                            coordinator=coord,
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
                            submission_date=now,
                        )
                    else:
                        r = qs.first()
                        r.coordinator = coord
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
                        r.submission_date = now
                        r.save()
                    #
                    # # create a review
                    # review, created = models.CSASRequestReview.objects.get_or_create(
                    #     csas_request=r
                    # )
                    # on_off_text = row['OnOff'].lower()
                    # if on_off_text == "on":
                    #     decision = 1
                    # elif on_off_text == "off":
                    #     decision = 2
                    # elif on_off_text == "withdrawn":
                    #     decision = 3
                    # elif on_off_text == "deferred":
                    #     decision = 4
                    # else:
                    #     decision = None
                    #
                    # review.decision = decision
                    # review.decision_date = now
                    # if not review.notes:
                    #     review.notes = f"Imported from tracking spreadsheet on {now.strftime('%Y-%m-%d')}"
                    #
                    # review.save()
