import inspect
import math
import os
from datetime import date, datetime, timedelta

import pytz
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.forms import modelformset_factory
from django.utils.translation import gettext
import pandas as pd
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
import numpy as np

from bio_diversity import models
from bio_diversity import utils


def mactaquac_water_quality_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'Pond': str, 'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    parsed = True
    temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
    oxlvl_envc_id = models.EnvCode.objects.filter(name="Oxygen Level").get()
    ph_envc_id = models.EnvCode.objects.filter(name="pH").get()
    disn_envc_id = models.EnvCode.objects.filter(name="Dissolved Nitrogen").get()

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            contx = utils.enter_tank_contx(row["Pond"], cleaned_data, None, return_contx=True)
            row_date = datetime.strptime(row["Year"] + row["Month"] + row["Day"],
                                         "%Y%b%d").replace(tzinfo=pytz.UTC).date()
            if not math.isnan(row["Time (24HR)"]):
                row_time = row["Time (24HR)"].replace(tzinfo=pytz.UTC)
            else:
                row_time = None

            if utils.enter_env(row["Temp °C"], row_date, cleaned_data, temp_envc_id, contx=contx, env_start=row_time):
                row_entered = True
            if utils.enter_env(row["DO%"], row_date, cleaned_data, oxlvl_envc_id, contx=contx, env_start=row_time):
                row_entered = True
            if utils.enter_env(row["pH"], row_date, cleaned_data, ph_envc_id, contx=contx, env_start=row_time):
                row_entered = True
            if utils.enter_env(row["Dissolved Nitrogen %"], row_date, cleaned_data, disn_envc_id, contx=contx,
                               env_start=row_time):
                row_entered = True

        except Exception as err:
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err.__str__())
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1
    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
