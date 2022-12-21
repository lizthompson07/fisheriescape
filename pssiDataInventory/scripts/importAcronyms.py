import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssiDataInventory.models import Acronym
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

rootdir = os.path.join(settings.BASE_DIR, 'pssiDataInventory')

def clear():
    toDelete = Acronym.objects.all()
    toDelete.delete()


def run():
    #fieldsList = [Inventory_ID, Approved_By, Data_Asset_Name, Data_Asset_Steward, Data_Asset_Sorting_Category, Operational_Or_Analytical_Data, Data_Asset_Acronym, Data_Asset_Description, APM_ID, Non_Salmon_Data, Data_Asset_Status, Data_Asset_Format, Data_Type, Data_Asset_Location, Data_Asset_Trustee, Data_Asset_Custodian, Application_Data_Asset_is_Associated_With, Application_Description, Technical_Documentation, Access_Point, Policy_Levers_Data_Asset_Supports, Key_Decisions, Impact_to_DFO_Data_Consumers, Decision_Supporting_Key_Products, Impact_on_Decision_Making, Uniqueness, Cost, Data_Asset_Size, Update_Frequency, Data_Standards, Metadata_Maturity, Data_Quality_Rating, Naming_Conventions, Security_Classification, Inbound_Data_Linkage, Outbound_Data_Linkage, Publication_Status] 
    #indexList = range(len(fieldsList))
    #Pacific_Region_Data_Inventory_2022.csv
    with open(os.path.join(rootdir, 'PacificSalmonAcronyms.csv'), 'r') as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        i = 0
        for row in reader:
            row = [entry.strip() for entry in row]
            row = [entry if entry != '' else None for entry in row]
            
            acronym_ID = row[0]
            acronym_Full_Name = row[1]
            acronym_URL = row[2]
            acronym_Topic = row[3]

            # left side: parameters, right side: argument
            model = Acronym(
                acronym_ID = acronym_ID,
                acronym_Full_Name = acronym_Full_Name,
                acronym_Topic = acronym_Topic,
                acronym_URL = acronym_URL,
            )
            model.save()
