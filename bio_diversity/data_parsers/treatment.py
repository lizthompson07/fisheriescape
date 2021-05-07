
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd
from decimal import Decimal

from bio_diversity import models
from bio_diversity import utils


def mactaquac_treatment_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        tank_data = pd.read_excel(cleaned_data["data_csv"], header=2, engine='openpyxl', sheet_name="Ponds",
                                  converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = tank_data.to_dict('records')
        eggroom_data = pd.read_excel(cleaned_data["data_csv"], header=2, engine='openpyxl', sheet_name="Eggrooms",
                                     converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        eggroom_data_dict = eggroom_data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # data prep:
    try:
        water_envc_id = models.EnvCode.objects.filter(name="Water Level").get()
    except Exception as err:
        log_data += "Error finding code for Water Level in database: \n"
        log_data += "{}\n\n".format(err)
        return log_data, False

    for row in data_dict:
        row_entered = False
        try:
            row_datetime = utils.get_row_date(row)
            row_date = row_datetime.date()
            contx, data_entered = utils.enter_tank_contx(row["Tank"], cleaned_data, None, return_contx=True)
            row_entered += data_entered
            val, unit_str = utils.val_unit_splitter(row["Amount"])
            duration = row["Duration (hours)"]
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
                row_entered = True
            except (ValidationError, IntegrityError):
                pass

            water_level, height_unit = utils.val_unit_splitter(row["Pond Level During Treatment"])
            row_entered += utils.enter_env(water_level, row_date, cleaned_data, water_envc_id, contx=contx)

            if utils.nan_to_none(row["Initials"]):
                perc_list, inits_not_found = utils.team_list_splitter(row["Initials"])
                for perc_id in perc_list:
                    row_entered += utils.add_team_member(perc_id, cleaned_data["evnt_id"])
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) on row: \n{}\n".format(inits, row)

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False

        rows_parsed += 1
        if row_entered:
            rows_entered += 1

    rows_parsed = 0
    rows_entered = 0
    for row in eggroom_data_dict:
        row_entered = False
        try:
            row_datetime = utils.get_row_date(row)
            row_date = row_datetime.date()
            contx, data_entered = utils.enter_trof_contx(str(row["Trough"]), cleaned_data, None, return_contx=True)
            row_entered += data_entered
            val, unit_str = utils.val_unit_splitter(row["Amount"])
            duration = row["Duration (mins)"]
            row_concentration = utils.parse_concentration(row["Concentration"])
            envt = models.EnvTreatment(contx_id=contx,
                                       envtc_id=models.EnvTreatCode.objects.filter(
                                           name__icontains=row["Treatment Type"]).get(),
                                       lot_num=None,
                                       amt=val,
                                       unit_id=models.UnitCode.objects.filter(name__icontains=unit_str).get(),
                                       duration=duration,
                                       concentration=row_concentration.quantize(Decimal("0.000001")),
                                       created_by=cleaned_data["created_by"],
                                       created_date=cleaned_data["created_date"],
                                       )

            try:
                envt.clean()
                envt.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                pass

            water_level, height_unit = utils.val_unit_splitter(row["Pond Level During Treatment"])
            row_entered += utils.enter_env(water_level, row_date, cleaned_data, water_envc_id, contx=contx)

            if utils.nan_to_none(row["Initials"]):
                perc_list, inits_not_found = utils.team_list_splitter(row["Initials"])
                for perc_id in perc_list:
                    row_entered += utils.add_team_member(perc_id, cleaned_data["evnt_id"])
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) on row: \n{}\n".format(inits, row)

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing eggroom data row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(eggroom_data_dict), rows_entered, len(eggroom_data_dict))
            return log_data, False

        rows_parsed += 1
        if row_entered:
            rows_entered += 1

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(eggroom_data_dict), rows_entered, len(eggroom_data_dict))
    return log_data, True
