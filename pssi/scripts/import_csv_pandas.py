import pandas as pd
import os
import datetime

from django.db import models
from django.conf import settings
from pssi.models import DataAsset
from django.db.models import QuerySet
# @pylance.typecheck(QuerySet)

ROOTDIR = os.path.join(settings.BASE_DIR, "pssi")
dataset_file = os.path.join(ROOTDIR, "csv", "Pacific_Region_Data_Inventory_main.csv")
dataset_model = DataAsset

def clear():
    to_delete = dataset_model.objects.all()
    to_delete.delete()

# Use Pandas read_csv() to ingest data into a dataframe, then create DataAsset instances using the values of each row in the dataframe
def run():
    df = pd.read_csv(open(dataset_file), skiprows=[0])
    print(df)