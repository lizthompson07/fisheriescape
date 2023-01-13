import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import Acronym
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")
DATASET = os.path.join(ROOTDIR, "csv", "Pacific_Salmon_Acronyms.csv")
DATA_MODEL = Acronym

def clear():
    to_delete = DATA_MODEL.objects.all()
    to_delete.delete()

# Similar to the functions in importCSV.py - use discrete column indices to map acronym values to the right field
# Also should be converted into pandas or another library that will allow for accessing specific fields
def run():

    field_list = [
        "acronym_letters",
        "acronym_full_name",
        "acronym_topic",
        "acronym_url"
    ]

    with open(DATASET, "r") as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        i = 0
        for row in reader:
            row = [entry.strip() for entry in row]
            row = [entry if entry != "" else None for entry in row]

            # Auto Increment ID
            acronym_id = i
            i += 1

            # value list
            value_list = [
                row[0],
                row[1],
                row[4],
                row[7]
            ]

            fields = dict(zip(field_list, value_list))

            # left side: parameters, right side: argument
            model = DATA_MODEL(
                acronym_id = acronym_id,
                acronym_letters = fields["acronym_letters"],
                acronym_full_name = fields["acronym_full_name"],
                acronym_topic = fields["acronym_topic"],
                acronym_url = fields["acronym_url"]
            )
            model.save()
            