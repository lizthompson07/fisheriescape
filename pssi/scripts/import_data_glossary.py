import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import DataGlossary
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")
# DATASET = os.path.join(ROOTDIR, "csv", "filename.csv")
DATA_MODEL = DataGlossary

def clear():
    to_delete = DATA_MODEL.objects.all()
    to_delete.delete()

# Similar to the functions in importCSV.py - use discrete column indices to map glossary values to the right field
def run():

    pass