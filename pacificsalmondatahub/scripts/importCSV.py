import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pacificsalmondatahub.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

# rootdir = dm_apps/pacificsalmondatahub
rootdir = os.path.join(settings.BASE_DIR, 'pacificsalmondatahub')

# Delete all objects stored in DataAsset table
def clearInventory():
    toDelete = DataAsset.objects.all()
    toDelete.delete()

# Goes through the csv row by row and maps the appropriate column to a variable
# Mapping with discrete column index will not work if structure of CSV is changed at all, try using pandas to search by field name
def run_csvToInventory():

    with open(os.path.join(rootdir, 'CSV/Pacific_Region_Data_Inventory_main.csv'), 'r') as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        for row in reader:
            # Remove whitespace and replace '' with None for cleaning
            row = [entry.strip() for entry in row]
            row = [entry if entry not in ['', 'N/A', 'n/a'] else None for entry in row]

            
            Inventory_ID                              = row[0]
            Approved_By                               = row[1]
            Data_Asset_Name                           = row[2]
            Data_Asset_Steward                        = row[3]
            Data_Asset_Sorting_Category               = row[4]
            Operational_Or_Analytical_Data            = row[5]
            Data_Asset_Acronym                        = row[6]
            Data_Asset_Description                    = row[7]
            APM_ID                                    = row[8]
            Non_Salmon_Data                           = row[9]
            Data_Asset_Status                         = row[10]
            Data_Asset_Format                         = row[11]
            Data_Type                                 = row[12]
            Data_Asset_Location                       = row[13]
            Data_Asset_Trustee                        = row[14]
            Data_Asset_Custodian                      = row[15]
            Application_Data_Asset_is_Associated_With = row[16]
            Application_Description                   = row[17]
            Technical_Documentation                   = row[18]
            Access_Point                              = row[19]
            Policy_Levers_Data_Asset_Supports         = row[20]
            Key_Decisions                             = row[21]
            Impact_to_DFO_Data_Consumers              = row[22]
            Decision_Supporting_Key_Products          = row[23]
            Impact_on_Decision_Making                 = row[24]
            Uniqueness                                = row[25]
            Cost                                      = row[26]
            Data_Asset_Size                           = row[27]
            Update_Frequency                          = row[28]
            Data_Standards                            = row[29]
            Metadata_Maturity                         = row[30]
            Data_Quality_Rating                       = row[31]
            Naming_Conventions                        = row[32]
            Security_Classification                   = row[33]
            Inbound_Data_Linkage                      = row[34]
            Outbound_Data_Linkage                     = row[35]
            Publication_Status                        = row[36]

            # Initializing a record for DataAsset -> DataAsset(parameter1=value1, parameter2=value2,...)
            # Initialize a DataAsset object using the variables and values assigned above
            model = DataAsset(
                Inventory_ID                              = Inventory_ID,
                Approved_By                               = Approved_By,
                Data_Asset_Name                           = Data_Asset_Name,
                Data_Asset_Steward                        = Data_Asset_Steward,
                Data_Asset_Sorting_Category               = Data_Asset_Sorting_Category,
                Operational_Or_Analytical_Data            = Operational_Or_Analytical_Data,
                Data_Asset_Acronym                        = Data_Asset_Acronym,
                Data_Asset_Description                    = Data_Asset_Description,
                APM_ID                                    = APM_ID,
                Non_Salmon_Data                           = Non_Salmon_Data,
                Data_Asset_Status                         = Data_Asset_Status,
                Data_Asset_Format                         = Data_Asset_Format,
                Data_Type                                 = Data_Type,
                Data_Asset_Location                       = Data_Asset_Location,
                Data_Asset_Trustee                        = Data_Asset_Trustee,
                Data_Asset_Custodian                      = Data_Asset_Custodian,
                Application_Data_Asset_is_Associated_With = Application_Data_Asset_is_Associated_With,
                Application_Description                   = Application_Description,
                Technical_Documentation                   = Technical_Documentation,
                Access_Point                              = Access_Point,
                Policy_Levers_Data_Asset_Supports         = Policy_Levers_Data_Asset_Supports,
                Key_Decisions                             = Key_Decisions,
                Impact_to_DFO_Data_Consumers              = Impact_to_DFO_Data_Consumers,
                Decision_Supporting_Key_Products          = Decision_Supporting_Key_Products,
                Impact_on_Decision_Making                 = Impact_on_Decision_Making,
                Uniqueness                                = Uniqueness,
                Cost                                      = Cost,
                Data_Asset_Size                           = Data_Asset_Size,
                Update_Frequency                          = Update_Frequency,
                Data_Standards                            = Data_Standards,
                Metadata_Maturity                         = Metadata_Maturity,
                Data_Quality_Rating                       = Data_Quality_Rating,
                Naming_Conventions                        = Naming_Conventions,
                Security_Classification                   = Security_Classification,
                Inbound_Data_Linkage                      = Inbound_Data_Linkage,
                Outbound_Data_Linkage                     = Outbound_Data_Linkage,
                Publication_Status                        = Publication_Status
            )
            model.save()
