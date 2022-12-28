import pandas as pd
import os
import datetime

from django.db import models
from django.conf import settings
from pacificsalmondatahub.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

rootdir = os.path.join(settings.BASE_DIR, 'pacificsalmondatahub')

def clearInventory():
    toDelete = DataAsset.objects.all()
    toDelete.delete()

# Use Pandas read_csv() to ingest data into a dataframe, then create DataAsset instances using the values of each row in the dataframe
def run_csvToInventory():
    csvDF = pd.read_csv(open(os.path.join(rootdir, 'PacificDataInventory121422.csv'))).dropna()
    print(csvDF)
    # for index, row in csvDF.iterrows():
    #     model = DataAsset(
    #         Inventory_ID                              = row['Inventory_ID'],
    #         Approved_By                               = row['Approved_By'],
    #         Data_Asset_Name                           = row['Data_Asset_Name'],
    #         Data_Asset_Steward                        = row['Data_Asset_Steward'],
    #         Data_Asset_Sorting_Category               = row['Data_Asset_Sorting_Category'],
    #         Operational_Or_Analytical_Data            = row['Operational_Or_Analytical_Data'],
    #         Data_Asset_Acronym                        = row['Data_Asset_Acronym'],
    #         Data_Asset_Description                    = row['Data_Asset_Description'],
    #         APM_ID                                    = row['APM_ID'],
    #         Non_Salmon_Data                           = row['Non_Salmon_Data'],
    #         Data_Asset_Status                         = row['Data_Asset_Status'],
    #         Data_Asset_Format                         = row['Data_Asset_Format'],
    #         Data_Type                                 = row['Data_Type'],
    #         Data_Asset_Location                       = row['Data_Asset_Location'],
    #         Data_Asset_Trustee                        = row['Data_Asset_Trustee'],
    #         Data_Asset_Custodian                      = row['Data_Asset_Custodian'],
    #         Application_Data_Asset_is_Associated_With = row['Application_Data_Asset_Is_Associated_With'],
    #         Application_Description                   = row['Application_Description'],
    #         Technical_Documentation                   = row['Technical_Documentation'],
    #         Access_Point                              = row['Access_Point'],
    #         Policy_Levers_Data_Asset_Supports         = row['Policy_Levers_Data_Asset_Supports'],
    #         Key_Decisions                             = row['Key_Decisions'],
    #         Impact_to_DFO_Data_Consumers              = row['Impact_to_DFO_Data_Consumers'],
    #         Decision_Supporting_Key_Products          = row['Decision_Supporting_Key_Products'],
    #         Impact_on_Decision_Making                 = row['Impact_on_Decision_Making'],
    #         Uniqueness                                = row['Uniqueness'],
    #         Cost                                      = row['Cost'],
    #         Data_Asset_Size                           = row['Data_Asset_Size'],
    #         Update_Frequency                          = row['Update_Frequency'],
    #         Data_Standards                            = row['Data_Standards'],
    #         Metadata_Maturity                         = row['Metadata_Maturity'],
    #         Data_Quality_Rating                       = row['Data_Quality_Rating'],
    #         Naming_Conventions                        = row['Naming_Conventions'],
    #         Security_Classification                   = row['Security_Classification'],
    #         Inbound_Data_Linkage                      = row['Inbound_Data_Linkage'],
    #         Outbound_Data_Linkage                     = row['Outbound_Data_Linkage'],
    #         Publication_Status                        = row['Publication_Status'],
    #     )
    #     model.save()

