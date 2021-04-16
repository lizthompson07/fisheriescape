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


def mactaquac_treatment_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=0, engine='openpyxl', sheet_name="Ponds").dropna(
            how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    water_envc_id = models.EnvCode.objects.filter(name="Water Level").get()

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_date = row["Date"].date()

            contx = utils.enter_tank_contx(row["Pond / Trough"], cleaned_data, None, return_contx=True)
            val, unit_str = utils.val_unit_splitter(row["Amount"])
            duration, time_unit = utils.val_unit_splitter(row["Duration"])
            row_concentration = utils.parse_concentration(row["Concentration"])
            envt = models.EnvTreatment(contx_id=contx,
                                       envtc_id=models.EnvTreatCode.objects.filter(
                                           name__icontains=row["Treatment Type"]).get(),
                                       lot_num=None,
                                       amt=val,
                                       unit_id=models.UnitCode.objects.filter(name__icontains=unit_str).get(),
                                       duration=60 * duration,
                                       concentration=row_concentration.quantize(Decimal("0.000001")),
                                       created_by=cleaned_data["created_by"],
                                       created_date=cleaned_data["created_date"],
                                       )

            try:
                envt.clean()
                envt.save()
            except (ValidationError, IntegrityError):
                pass

            water_level, height_unit = utils.val_unit_splitter(row["Pond Level During Treatment"])
            utils.enter_env(water_level, row_date, cleaned_data, water_envc_id, contx=contx)

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