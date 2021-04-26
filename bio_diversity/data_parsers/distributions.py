from datetime import datetime

import pytz
from django.core.exceptions import ValidationError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils


def coldbrook_distribution_parser(cleaned_data):
    log_data, sucess = mactaquac_distribution_parser(cleaned_data)
    return log_data, sucess


def mactaquac_distribution_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0

    # loading data catch:
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=1, engine='openpyxl',
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prepare rows before iterating:
    try:
        temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()

        locc_id = models.LocCode.objects.filter(name__icontains="Distribution site").get()

    except Exception as err:
        log_data += "\n Error preparing data: {}".format(err.__str__())
        return log_data, False

    # iterate over rows
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_date = datetime.strptime(str(row["Year"]) + str(row["Month"]) + str(row["Day"]), "%Y%b%d").replace(
                tzinfo=pytz.UTC)

            relc_id = None
            rive_id = models.RiverCode.objects.filter(name__icontains=row["Stock"]).get()
            if utils.nan_to_none(row["Location Name"]):
                relc_qs = models.ReleaseSiteCode.objects.filter(name__icontains=row["Location Name"],
                                                                rive_id=rive_id)
                if len(relc_qs) == 1:
                    relc_id = relc_qs.get()
            loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                  locc_id=locc_id,
                                  rive_id=rive_id,
                                  relc_id=relc_id,
                                  loc_lat=utils.round_no_nan(row["Lat"], 5),
                                  loc_lon=utils.round_no_nan(row["Long"], 5),
                                  loc_date=row_date,
                                  comments=row["Comments"],
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
            try:
                loc.set_relc_latlng()
                loc.clean()
                loc.save()
                row_entered = True
            except ValidationError:
                loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                     rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                     relc_id=loc.relc_id, loc_lat=loc.loc_lat,
                                                     loc_lon=loc.loc_lon, loc_date=loc.loc_date).get()

            if utils.nan_to_none(row["Crew"]):
                row_percs, inits_not_found = utils.team_list_splitter(row["Crew"])
                for perc in row_percs:
                    utils.add_team_member(perc, cleaned_data["evnt_id"], loc_id=loc)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                              row)
            if utils.nan_to_none(row["Driver"]):
                if utils.add_team_member(row["Driver"], cleaned_data["evnt_id"], loc_id=loc):
                    row_entered = True
                else:
                    log_data += "No valid personnel with initials ({}) for driver in this " \
                                "row: \n {}".format(row["Driver"], row)

            if utils.enter_env(row["Temperature"], row_date, cleaned_data, temp_envc_id, loc_id=loc, ):
                row_entered = True

            cnt = utils.enter_cnt(cleaned_data, cnt_value=row["NFish"], loc_pk=loc.pk, cnt_code="Fish Distributed")

            if utils.enter_cnt_det(cleaned_data, cnt, row["Temp???"], "Electrofishing Settings"):
                row_entered = True

        except Exception as err:
            log_data += "Error parsing row {}: \n".format(rows_parsed + 1)
            log_data += str(row)
            log_data += "\n Error: {}".format(err.__str__())
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                        " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    # enter general data once all rows are entered:

    try:
        contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, None, True)

    except Exception as err:
        log_data += "Error parsing common data: \n"
        log_data += "\n Error: {}".format(err.__str__())
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
