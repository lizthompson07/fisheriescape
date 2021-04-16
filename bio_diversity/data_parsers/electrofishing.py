from datetime import  datetime

import pytz
from django.core.exceptions import ValidationError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils


def coldbrook_electrofishing_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0

    # load data:
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl',
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # set up before iterating over rows:
    try:
        temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
        river_dict = {}
        for river_name in data["River"].unique():
            river_dict[river_name] = models.RiverCode.objects.filter(name__iexact=river_name).get()

    except Exception as err:
        log_data += "\n Error in preparing data: {}".format(err.__str__())
        return log_data, False

    # iterate over rows:
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_datetime = datetime.strptime(row["Year"] + row["Month"] + row["Day"],
                                             "%Y%b%d").replace(tzinfo=pytz.UTC)
            relc_id = None
            rive_id = river_dict[row["River"]]
            if utils.nan_to_none(row["site"]):
                relc_qs = models.ReleaseSiteCode.objects.filter(name__iexact=row["Site"])
                if len(relc_qs) == 1:
                    relc_id = relc_qs.get()
            loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                  locc_id=models.LocCode.objects.filter(name__icontains="Electrofishing site").get(),
                                  rive_id=rive_id,
                                  relc_id=relc_id,
                                  loc_lat=utils.round_no_nan(row["Lat"], 5),
                                  loc_lon=utils.round_no_nan(row["Long"], 5),
                                  end_lat=utils.round_no_nan(row["End Lat"], 5),
                                  end_lon=utils.round_no_nan(row["End Long"], 5),
                                  loc_date=row_datetime,
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

            if utils.enter_env(row["temp"], row_datetime, cleaned_data, temp_envc_id, loc_id=loc, ):
                row_entered = True

            cnt_caught = utils.enter_cnt(cleaned_data, cnt_value=row["# of salmon collected"], loc_pk=loc.pk,
                                         cnt_code="Fish Caught")
            cnt_obs = utils.enter_cnt(cleaned_data, cnt_value=row["# of salmon observed"], loc_pk=loc.pk,
                                      cnt_code="Fish Observed")

            if cnt_caught:
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["Settings"], "Electrofishing Settings"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["fishing seconds"], "Electrofishing Seconds"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["Voltage"], "Voltage"):
                    row_entered = True
            if cnt_obs:
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["Settings"], "Electrofishing Settings"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["fishing seconds"], "Electrofishing Seconds"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["Voltage"], "Voltage"):
                    row_entered = True

        except Exception as err:
            log_data += "Error parsing row: \n"
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

    # do general actions on data
    try:
        for key in river_dict:
            stok_id = models.StockCode.objects.filter(name__icontains=key).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)
            if anix_grp_qs.count() == 0:
                grp = models.Group(spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                   stok_id=stok_id,
                                   coll_id=models.Collection.objects.filter(name__icontains=data["Collection"]).get(),
                                   grp_year=data["Year"][0],
                                   grp_valid=True,
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
                try:
                    grp.clean()
                    grp.save()
                except ValidationError:
                    grp = models.Group.objects.filter(spec_id=grp.spec_id, stok_id=grp.stok_id,
                                                      grp_year=grp.grp_year, coll_id=grp.coll_id).get()

                anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
            elif anix_grp_qs.count() == 1:
                anix_grp = anix_grp_qs.get()
                grp = anix_grp.grp_id

            contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, grp.pk, True)

            utils.enter_cnt(cleaned_data, data[data["River"] == key]["# of salmon collected"].sum(), contx_pk=contx.pk,
                            cnt_code="Fish in Container", )

    except Exception as err:
        log_data += "Error parsing common data (entering group, placing it in a location and recording the count): \n"
        log_data += "\n Error: {}".format(err.__str__())
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def mactaquac_electrofishing_parser(cleaned_data):
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
        river_dict = {}
        for river_name in data["River"].unique():
            river_dict[river_name] = models.RiverCode.objects.filter(name__iexact=river_name).get()

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
            rive_id = river_dict[row["River"]]
            if utils.nan_to_none(row["Location Name"]):
                relc_qs = models.ReleaseSiteCode.objects.filter(name__icontains=row["Location Name"],
                                                                rive_id=rive_id)
                if len(relc_qs) == 1:
                    relc_id = relc_qs.get()
            loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                  locc_id=models.LocCode.objects.first(),
                                  rive_id=rive_id,
                                  relc_id=relc_id,
                                  loc_lat=utils.round_no_nan(row["Lat"], 5),
                                  loc_lon=utils.round_no_nan(row["Long"], 5),
                                  end_lat=utils.round_no_nan(row["Lat.1"], 5),
                                  end_lon=utils.round_no_nan(row["Long.1"], 5),
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

            if utils.enter_env(row["Temperature"], row_date, cleaned_data, temp_envc_id, loc_id=loc, ):
                row_entered = True

            cnt_caught = utils.enter_cnt(cleaned_data, cnt_value=row["# Fish Collected"], loc_pk=loc.pk,
                                         cnt_code="Fish Caught")
            cnt_obs = utils.enter_cnt(cleaned_data, cnt_value=row["# Fish Observed"], loc_pk=loc.pk,
                                      cnt_code="Fish Observed")

            if cnt_caught:
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["Fishing Settings"], "Electrofishing Settings"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["Fishing seconds"], "Electrofishing Seconds"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_caught, row["Voltage"], "Voltage"):
                    row_entered = True
            if cnt_obs:
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["Fishing seconds"], "Electrofishing Seconds"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["Fishing seconds"], "Electrofishing Seconds"):
                    row_entered = True
                if utils.enter_cnt_det(cleaned_data, cnt_obs, row["Voltage"], "Voltage"):
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
        for key in river_dict:
            stok_id = models.StockCode.objects.filter(name__icontains=key).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)

            if anix_grp_qs.count() == 0:
                grp = models.Group(spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                   stok_id=stok_id,
                                   coll_id=models.Collection.objects.filter(name__icontains=row["Collection"]).get(),
                                   grp_year=data["Year"][0],
                                   grp_valid=True,
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
                try:
                    grp.clean()
                    grp.save()
                except ValidationError:
                    grp = models.Group.objects.filter(spec_id=grp.spec_id, stok_id=grp.stok_id,
                                                      grp_year=grp.grp_year, coll_id=grp.coll_id).get()
                anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
            elif anix_grp_qs.count() == 1:
                anix_grp = anix_grp_qs.get()
                grp = anix_grp.grp_id

            contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, grp.pk, True)

            utils.enter_cnt(cleaned_data, data[data["River"] == key]["# Fish Collected"].sum(), contx_pk=contx.pk,
                            cnt_code="Fish in Container", )

    except Exception as err:
        log_data += "Error parsing common data: \n"
        log_data += "\n Error: {}".format(err.__str__())
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
