import csv
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")
DATASET = os.path.join(ROOTDIR, "csv", "Pacific_Region_Data_Inventory_main.csv")
DATA_MODEL = DataAsset

# Delete all objects stored in DataAsset table
def clear_inventory():
    to_delete = DATA_MODEL.objects.all()
    to_delete.delete()

# Goes through the csv row by row and maps the appropriate column to a variable
# Mapping with discrete column index will not work if structure of CSV is changed at all, try using pandas to search by field name
def run_csv_to_inventory():
    
    field_list = [
        "inventory_id",
        "approved_by",
        "data_asset_name",
        "data_asset_steward",
        "data_asset_sorting_category",
        "operational_or_analytical_data",
        "data_asset_acronym",
        "data_asset_description",
        "apm_id",
        "non_salmon_data",
        "data_asset_status",
        "data_asset_format",
        "data_type",
        "data_asset_location",
        "data_asset_trustee",
        "data_asset_custodian",
        "application_data_asset_is_associated_with",
        "application_description",
        "technical_documentation",
        "access_point",
        "policy_levers_data_asset_supports",
        "key_decisions",
        "impact_to_dfo_data_consumers",
        "decision_supporting_key_products",
        "impact_on_decision_making",
        "uniqueness",
        "cost",
        "data_asset_size",
        "update_frequency",
        "data_standards",
        "metadata_maturity",
        "data_quality_rating",
        "naming_conventions",
        "security_classification",
        "inbound_data_linkage",
        "outbound_data_linkage",
        "publication_status"
    ]

    # max_field_len = dict(zip(field_list, list([0]*len(field_list))))

    with open(os.path.join(ROOTDIR, DATASET), "r") as csvfile:
        reader = csv.reader(csvfile)
        #skip header row
        next(reader)
        for row in reader:
            # Remove whitespace and replace "" with None for cleaning
            row = [entry.strip() for entry in row]
            row = [entry if entry not in ["", "N/A", "n/a"] else None for entry in row]
            fields = dict(zip(field_list, row))

            # Clean data
            cleaning = [
                "data_asset_steward",
                "data_asset_custodian", 
            ]

            for field in cleaning:
                if fields[field] is not None:
                    fields[field] = fields[field].replace("\n", " ")
                    fields[field] = " ".join(fields[field].split())

            # Find max len of each field
            # for field in fields:
            #     if fields[field] is not None:
            #         max_len = 0
            #         if len(fields[field]) > max_len:
            #             max_len = len(fields[field])
            #         if max_len > max_field_len[field]:
            #             max_field_len[field] = max_len
           
            # Initializing a record for DataAsset -> DataAsset(parameter1=value1, parameter2=value2,...)
            # Initialize a DataAsset object using the variables and values assigned above
            model = DATA_MODEL(
                inventory_id                              = fields["inventory_id"],
                approved_by                               = fields["approved_by"],
                data_asset_name                           = fields["data_asset_name"],
                data_asset_steward                        = fields["data_asset_steward"],
                data_asset_sorting_category               = fields["data_asset_sorting_category"],
                operational_or_analytical_data            = fields["operational_or_analytical_data"],
                data_asset_acronym                        = fields["data_asset_acronym"],
                data_asset_description                    = fields["data_asset_description"],
                apm_id                                    = fields["apm_id"],
                non_salmon_data                           = fields["non_salmon_data"],
                data_asset_status                         = fields["data_asset_status"],
                data_asset_format                         = fields["data_asset_format"],
                data_type                                 = fields["data_type"],
                data_asset_location                       = fields["data_asset_location"],
                data_asset_trustee                        = fields["data_asset_trustee"],
                data_asset_custodian                      = fields["data_asset_custodian"],
                application_data_asset_is_associated_with = fields["application_data_asset_is_associated_with"],
                application_description                   = fields["application_description"],
                technical_documentation                   = fields["technical_documentation"],
                access_point                              = fields["access_point"],
                policy_levers_data_asset_supports         = fields["policy_levers_data_asset_supports"],
                key_decisions                             = fields["key_decisions"],
                impact_to_dfo_data_consumers              = fields["impact_to_dfo_data_consumers"],
                decision_supporting_key_products          = fields["decision_supporting_key_products"],
                impact_on_decision_making                 = fields["impact_on_decision_making"],
                uniqueness                                = fields["uniqueness"],
                cost                                      = fields["cost"],
                data_asset_size                           = fields["data_asset_size"],
                update_frequency                          = fields["update_frequency"],
                data_standards                            = fields["data_standards"],
                metadata_maturity                         = fields["metadata_maturity"],
                data_quality_rating                       = fields["data_quality_rating"],
                naming_conventions                        = fields["naming_conventions"],
                security_classification                   = fields["security_classification"],
                inbound_data_linkage                      = fields["inbound_data_linkage"],
                outbound_data_linkage                     = fields["outbound_data_linkage"],
                publication_status                        = fields["publication_status"]
            )
            model.save()

    # print(max_field_len)