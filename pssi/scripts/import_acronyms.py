import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import Acronym
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")

def clear():
    to_delete = Acronym.objects.all()
    to_delete.delete()

# Similar to the functions in importCSV.py - use discrete column indices to map acronym values to the right field
# Also should be converted into pandas or another library that will allow for accessing specific fields
def run():

    with open(os.path.join(ROOTDIR, "./csv/Pacific_Salmon_Acronyms.csv"), "r") as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        i = 0
        for row in reader:
            row = [entry.strip() for entry in row]
            row = [entry if entry != "" else None for entry in row]
            
            acronym_id = i
            i+= 1
            acronym_letters = row[0]
            acronym_full_name = row[1]
            acronym_url = row[7]
            acronym_topic = row[4]

            # left side: parameters, right side: argument
            model = Acronym(
                acronym_id = acronym_id,
                acronym_letters = acronym_letters,
                acronym_full_name = acronym_full_name,
                acronym_topic = acronym_topic,
                acronym_url = acronym_url,
            )
            model.save()
