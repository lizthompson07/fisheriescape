import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pacificsalmondatahub.models import BusinessGlossary
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, 'pacificsalmondatahub')

def clear():
    to_delete = BusinessGlossary.objects.all()
    to_delete.delete()

# Similar to the functions in importCSV.py - use discrete column indices to map glossary values to the right field
def run():

    pass

    # with open(os.path.join(ROOTDIR, './csv/PacificSalmonBusinessGlossary.csv'), 'r') as csvfile:
    #     reader = csv.reader(csvfile)
    #     #skip header row
    #     next(reader)
    #     i = 0
    #     for row in reader:
    #         row = [entry.strip() for entry in row]
    #         row = [entry if entry != '' else None for entry in row]
            
    #         acronym_ID = i
    #         i+= 1
    #         acronym_Letters = row[0]
    #         acronym_Full_Name = row[1]
    #         acronym_URL = row[7]
    #         acronym_Topic = row[4]

    #         # left side: parameters, right side: argument
    #         model = BusinessGlossary(
    #             acronym_ID = acronym_ID,
    #             acronym_Letters = acronym_Letters,
    #             acronym_Full_Name = acronym_Full_Name,
    #             acronym_Topic = acronym_Topic,
    #             acronym_URL = acronym_URL,
    #         )
    #         model.save()
