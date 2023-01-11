import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

# ROOTDIR = dm_apps/pssi
ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")

# Delete all objects stored in DataAsset table
def clear_inventory():
    to_delete = DataAsset.objects.all()
    to_delete.delete()

# Goes through the csv row by row and maps the appropriate column to a variable
# Mapping with discrete column index will not work if structure of CSV is changed at all, try using pandas to search by field name
def run_csv_to_inventory():

    with open(os.path.join(ROOTDIR, "./csv/Pacific_Region_Data_Inventory_main.csv"), "r") as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        for row in reader:
            # Remove whitespace and replace "" with None for cleaning
            row = [entry.strip() for entry in row]
            row = [entry if entry not in ["", "N/A", "n/a"] else None for entry in row]

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
                inventory_id                              = Inventory_ID,
                approved_by                               = Approved_By,
                data_asset_name                           = Data_Asset_Name,
                data_asset_steward                        = Data_Asset_Steward,
                data_asset_sorting_category               = Data_Asset_Sorting_Category,
                operational_or_analytical_data            = Operational_Or_Analytical_Data,
                data_asset_acronym                        = Data_Asset_Acronym,
                data_asset_description                    = Data_Asset_Description,
                apm_id                                    = APM_ID,
                non_salmon_data                           = Non_Salmon_Data,
                data_asset_status                         = Data_Asset_Status,
                data_asset_format                         = Data_Asset_Format,
                data_type                                 = Data_Type,
                data_asset_location                       = Data_Asset_Location,
                data_asset_trustee                        = Data_Asset_Trustee,
                data_asset_custodian                      = Data_Asset_Custodian,
                application_data_asset_is_associated_with = Application_Data_Asset_is_Associated_With,
                application_description                   = Application_Description,
                technical_documentation                   = Technical_Documentation,
                access_point                              = Access_Point,
                policy_levers_data_asset_supports         = Policy_Levers_Data_Asset_Supports,
                key_decisions                             = Key_Decisions,
                impact_to_dfo_data_consumers              = Impact_to_DFO_Data_Consumers,
                decision_supporting_key_products          = Decision_Supporting_Key_Products,
                impact_on_decision_making                 = Impact_on_Decision_Making,
                uniqueness                                = Uniqueness,
                cost                                      = Cost,
                data_asset_size                           = Data_Asset_Size,
                update_frequency                          = Update_Frequency,
                data_standards                            = Data_Standards,
                metadata_maturity                         = Metadata_Maturity,
                data_quality_rating                       = Data_Quality_Rating,
                naming_conventions                        = Naming_Conventions,
                security_classification                   = Security_Classification,
                inbound_data_linkage                      = Inbound_Data_Linkage,
                outbound_data_linkage                     = Outbound_Data_Linkage,
                publication_status                        = Publication_Status
            )
            model.save()
