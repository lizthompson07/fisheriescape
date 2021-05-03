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
            river_dict[river_name] = models.RiverCode.objects.filter(name__icontains=river_name).get()

        leader_code = models.RoleCode.objects.filter(name__iexact="Crew Lead").get()
        if cleaned_data["evntc_id"].__str__() == "Electrofishing":
            locc_id = models.LocCode.objects.filter(name__icontains="Electrofishing site").get()
        elif cleaned_data["evntc_id"].__str__() == "Smolt Wheel Collection":
            locc_id = models.LocCode.objects.filter(name__icontains="Smolt Wheel site").get()
        elif cleaned_data["evntc_id"].__str__() == "Bypass Collection":
            locc_id = models.LocCode.objects.filter(name__icontains="Bypass site").get()

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "\n Error in preparing data: {}".format(err_msg)
        return log_data, False

    # iterate over rows:
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_datetime = utils.get_row_date(row)
            relc_id = None
            rive_id = river_dict[row["River"]]
            if utils.nan_to_none(row["site"]):
                relc_qs = models.ReleaseSiteCode.objects.filter(name__iexact=row["Site"])
                if len(relc_qs) == 1:
                    relc_id = relc_qs.get()
            loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                  locc_id=locc_id,
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

            if utils.nan_to_none(row["Crew"]):
                row_percs, inits_not_found = utils.team_list_splitter(row["Crew"])
                for perc in row_percs:
                    utils.add_team_member(perc, cleaned_data["evnt_id"], loc_id=loc)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                              row)

            if utils.nan_to_none(row["crew lead"]):
                row_percs, inits_not_found = utils.team_list_splitter(row["crew lead"])
                for perc in row_percs:
                    utils.add_team_member(perc, cleaned_data["evnt_id"], loc_id=loc, role_id=leader_code)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                              row)

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
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n \n Error: {}".format(err_msg)
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
        river_group_data = data.groupby(["River", "Group", "Collection"], dropna=False).size().reset_index()
        for row in river_group_data:
            stok_id = models.StockCode.objects.filter(name__icontains=row["River"]).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)

            grp_found = False
            grp = None
            for anix in anix_grp_qs:
                anix_prog_grp_names = [adsc.name for adsc in anix.grp_id.prog_group()]
                if utils.nan_to_none(row["Group"]) and row["Group"] in anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
                elif not utils.nan_to_none(row["Group"]) and not anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
            if not grp_found:
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
                if utils.nan_to_none(row["Group"]):
                    utils.enter_grpd(anix_grp.pk, cleaned_data, cleaned_data["evnt_id"].start_date, None,
                                     "Program Group", row["Group"])

            contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, grp.pk, True)

            if utils.nan_to_none(row["Group"]):
                utils.enter_cnt(cleaned_data, data[(data["River"] == row["River"]) & (data["Group"] == row["Group"])][
                    "# of salmon collected"].sum(), contx_pk=contx.pk, cnt_code="Fish in Container", )
            else:
                utils.enter_cnt(cleaned_data, data[(data["River"] == row["River"]) & (data["Group"].isnull())][
                    "# of salmon collected"].sum(), contx_pk=contx.pk,
                                cnt_code="Fish in Container", )

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error parsing common data (entering group, placing it in a location and recording the count): \n"
        log_data += "\n Error: {}".format(err_msg)
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
        if cleaned_data["evntc_id"].__str__() == "Electrofishing":
            locc_id = models.LocCode.objects.filter(name__icontains="Electrofishing site").get()
        elif cleaned_data["evntc_id"].__str__() == "Smolt Wheel Collection":
            locc_id = models.LocCode.objects.filter(name__icontains="Smolt Wheel site").get()
        elif cleaned_data["evntc_id"].__str__() == "Bypass Collection":
            locc_id = models.LocCode.objects.filter(name__icontains="Bypass site").get()

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "\n Error preparing data: {}".format(err_msg)
        return log_data, False

    # iterate over rows
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_date = utils.get_row_date(row)

            relc_id = None
            rive_id = river_dict[row["River"]]
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

            if utils.nan_to_none(row["Crew"]):
                row_percs, inits_not_found = utils.team_list_splitter(row["Crew"])
                for perc in row_percs:
                    utils.add_team_member(perc, cleaned_data["evnt_id"], loc_id=loc)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                              row)

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
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row {}: \n".format(rows_parsed + 1)
            log_data += str(row)
            log_data += "\n \n Error: {}".format(err_msg)
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
        river_group_data = data.groupby(["River", "Group", "Collection"], dropna=False).size().reset_index()
        for row in river_group_data.to_dict("records"):
            stok_id = models.StockCode.objects.filter(name__icontains=row["River"]).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)

            grp_found = False
            grp = None
            for anix in anix_grp_qs:
                anix_prog_grp_names = [adsc.name for adsc in anix.grp_id.prog_group()]
                if utils.nan_to_none(row["Group"]) and row["Group"] in anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
                elif not utils.nan_to_none(row["Group"]) and not anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
            if not grp_found:
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
                    # no way to get the groups here, should only be here if there are no groups already
                    pass
                anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
                if utils.nan_to_none(row["Group"]):
                    utils.enter_grpd(anix_grp.pk, cleaned_data, cleaned_data["evnt_id"].start_date, None, "Program Group",
                                     row["Group"])

            contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, grp.pk, True)

            if utils.nan_to_none(row["Group"]):
                utils.enter_cnt(cleaned_data, data[(data["River"] == row["River"]) & (data["Group"] == row["Group"])][
                    "# Fish Collected"].sum(), contx_pk=contx.pk, cnt_code="Fish in Container", )
            else:
                utils.enter_cnt(cleaned_data, data[(data["River"] == row["River"]) & (data["Group"].isnull())][
                    "# Fish Collected"].sum(), contx_pk=contx.pk,
                                cnt_code="Fish in Container", )

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error parsing common data: \n"
        log_data += "\n Error: {}".format(err_msg)
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
