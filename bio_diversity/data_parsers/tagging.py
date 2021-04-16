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


def coldbrook_tagging_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'to tank': str, 'from tank': str, 'Year': str, 'Month': str, 'Day': str}).dropna(
            how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    grp_id = False
    try:
        year, coll = utils.year_coll_splitter(data["Group"][0])
        grp_qs = models.Group.objects.filter(stok_id__name=data_dict[0]["Stock"],
                                             coll_id__name__icontains=coll,
                                             grp_year=year)
        if len(grp_qs) == 1:
            grp_id = grp_qs.get().pk
        elif len(grp_qs) > 1:
            for grp in grp_qs:
                tank_list = grp.current_tank()
                if str(data["from Tank"][0]) in [tank.name for tank in tank_list]:
                    grp_id = grp.pk

    except Exception as err:
        log_data += "Error finding origin group (check first row): \n"
        log_data += "Error: {}\n\n".format(err.__str__())
        return log_data, False

    if grp_id:
        anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp_id)

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            year, coll = utils.year_coll_splitter(row["Group"])
            row_datetime = datetime.strptime(row["Year"] + row["Month"] + row["Day"],
                                             "%Y%b%d").replace(tzinfo=pytz.UTC)
            row_date = row_datetime.date()
            if type(row["Universal Fish ID"]) == float:
                indv_ufid = None
            else:
                indv_ufid = row["Universal Fish ID"]
            indv = models.Individual(grp_id_id=grp_id,
                                     spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                     stok_id=models.StockCode.objects.filter(name=row["Stock"]).get(),
                                     coll_id=models.Collection.objects.filter(name__icontains=coll).get(),
                                     indv_year=year,
                                     pit_tag=row["PIT tag"],
                                     ufid=indv_ufid,
                                     indv_valid=True,
                                     comments=row["comments"],
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
            try:
                indv.clean()
                indv.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                indv = models.Individual.objects.filter(pit_tag=indv.pit_tag).get()

            if not row["from Tank"] == "nan" and not row["to tank"] == "nan":
                in_tank = models.Tank.objects.filter(name=row["from Tank"]).get()
                out_tank = models.Tank.objects.filter(name=row["to tank"]).get()
                if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                              indv_pk=indv.pk):
                    row_entered = True

            anix_indv = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

            utils.enter_anix(cleaned_data, indv_pk=indv.pk, grp_pk=grp_id)

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Vial"], "Vial", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Box"], "Box", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["location"], "Box Location", None):
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

    from_tanks = data["from Tank"].value_counts()
    for tank_name in from_tanks.keys():
        fish_tagged_from_tank = int(from_tanks[tank_name])
        contx = utils.enter_tank_contx(tank_name, cleaned_data, None, grp_pk=grp_id, return_contx=True)
        if contx:
            utils.enter_cnt(cleaned_data, fish_tagged_from_tank, contx.pk, cnt_code="Pit Tagged")

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def mactaquac_tagging_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'to tank': str, "PIT": str, 'Year': str, 'Month': str, 'Day': str}).dropna(
            how="all")
        data["Comments"] = data["Comments"].fillna('')
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    parsed = True
    grp_id = False
    try:

        year, coll = utils.year_coll_splitter(data["Collection"][0])
        grp_qs = models.Group.objects.filter(stok_id__name=data_dict[0]["Stock"],
                                             coll_id__name__icontains=coll,
                                             grp_year=year)
        if len(grp_qs) == 1:
            grp_id = grp_qs.get().pk
        elif len(grp_qs) > 1:
            for grp in grp_qs:
                tank_list = grp.current_tank()
                if data["Origin Pond"][0] in [tank.name for tank in tank_list]:
                    grp_id = grp.pk

    except Exception as err:
        log_data += "Error finding origin group (check first row): \n"
        log_data += "Error: {}\n\n".format(err.__str__())
        return log_data, False
    if grp_id:
        anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp_id)

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            year, coll = utils.year_coll_splitter(row["Collection"])
            row_datetime = datetime.strptime(row["Year"] + row["Month"] + row["Day"],
                                             "%Y%b%d").replace(tzinfo=pytz.UTC)
            indv = models.Individual(grp_id_id=grp_id,
                                     spec_id=models.SpeciesCode.objects.filter(name__icontains="Salmon").get(),
                                     stok_id=models.StockCode.objects.filter(name=row["Stock"]).get(),
                                     coll_id=models.Collection.objects.filter(name__icontains=coll).get(),
                                     indv_year=year,
                                     pit_tag=row["PIT"],
                                     indv_valid=True,
                                     comments=row["Comments"],
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
            try:
                indv.clean()
                indv.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                indv = models.Individual.objects.filter(pit_tag=indv.pit_tag).get()

            if not row["Origin Pond"] == "nan" and not row["Destination Pond"] == "nan":
                in_tank = models.Tank.objects.filter(name=row["ORIGIN POND"]).get()
                out_tank = models.Tank.objects.filter(name=row["DESTINATION POND"]).get()
                if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                              indv_pk=indv.pk):
                    row_entered = True

            anix_indv = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

            anix_grp = utils.enter_anix(cleaned_data, indv_pk=indv.pk, grp_pk=grp_id)

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_datetime.date(), row["Length (cm)"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_datetime.date(), row["Weight (g)"], "Weight", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_datetime.date(), row["Vial Number"], "Vial", None):
                row_entered = True

            if row["Precocity (Y/N)"].upper() == "Y":
                if utils.enter_indvd(anix_indv.pk, cleaned_data, row_datetime.date(), None, "Animal Health",
                                     "Precocity"):
                    row_entered = True

            if row["Comments"]:
                utils.comment_parser(row["Comments"], anix_indv, det_date=row_datetime.date())
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

    from_tanks = data["Origin Pond"].value_counts()
    for tank_name in from_tanks.keys():
        fish_tagged_from_tank = int(from_tanks[tank_name])
        contx = utils.enter_tank_contx(tank_name, cleaned_data, None, grp_pk=grp_id, return_contx=True)
        if contx:
            utils.enter_cnt(cleaned_data, fish_tagged_from_tank, contx.pk, cnt_code="Pit Tagged")

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
