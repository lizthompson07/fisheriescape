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
    #     )
    #     model.save()

