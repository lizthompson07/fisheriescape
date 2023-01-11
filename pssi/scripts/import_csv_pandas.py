import pandas as pd
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")

def clear_inventory():
    to_delete = DataAsset.objects.all()
    to_delete.delete()

# Use Pandas read_csv() to ingest data into a dataframe, then create DataAsset instances using the values of each row in the dataframe
def run_csv_to_inventory():
    df = pd.read_csv(open(os.path.join(ROOTDIR, "./csv/Pacific_Region_Data_Inventory_main.csv"))).dropna()
    print(df)
    # for idx, row in df.iterrows():
    #     model = DataAsset(
    #         inventory_id                              = row["Inventory_ID"],
    #         approved_by                               = row["Approved_By"],
    #         data_asset_name                           = row["Data_Asset_Name"],
    #         data_asset_steward                        = row["Data_Asset_Steward"],
    #         data_asset_sorting_category               = row["Data_Asset_Sorting_Category"],
    #         operational_or_analytical_data            = row["Operational_Or_Analytical_Data"],
    #         data_asset_acronym                        = row["Data_Asset_Acronym"],
    #         data_asset_description                    = row["Data_Asset_Description"],
    #         apm_id                                    = row["APM_ID"],
    #         non_salmon_data                           = row["Non_Salmon_Data"],
    #         data_asset_status                         = row["Data_Asset_Status"],
    #         data_asset_format                         = row["Data_Asset_Format"],
    #         data_type                                 = row["Data_Type"],
    #         data_asset_location                       = row["Data_Asset_Location"],
    #         data_asset_trustee                        = row["Data_Asset_Trustee"],
    #         data_asset_custodian                      = row["Data_Asset_Custodian"],
    #         application_data_asset_is_associated_with = row["Application_Data_Asset_Is_Associated_With"],
    #         application_description                   = row["Application_Description"],
    #         technical_documentation                   = row["Technical_Documentation"],
    #         access_point                              = row["Access_Point"],
    #         policy_levers_data_asset_supports         = row["Policy_Levers_Data_Asset_Supports"],
    #         key_decisions                             = row["Key_Decisions"],
    #         impact_to_dfo_data_consumers              = row["Impact_to_DFO_Data_Consumers"],
    #         decision_supporting_key_products          = row["Decision_Supporting_Key_Products"],
    #         impact_on_decision_making                 = row["Impact_on_Decision_Making"],
    #         uniqueness                                = row["Uniqueness"],
    #         cost                                      = row["Cost"],
    #         data_asset_size                           = row["Data_Asset_Size"],
    #         update_frequency                          = row["Update_Frequency"],
    #         data_standards                            = row["Data_Standards"],
    #         metadata_maturity                         = row["Metadata_Maturity"],
    #         data_quality_rating                       = row["Data_Quality_Rating"],
    #         naming_conventions                        = row["Naming_Conventions"],
    #         security_classification                   = row["Security_Classification"],
    #         inbound_data_linkage                      = row["Inbound_Data_Linkage"],
    #         outbound_data_linkage                     = row["Outbound_Data_Linkage"],
    #         publication_status                        = row["Publication_Status"],
    #     )
    #     model.save()

