from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils


def coldbrook_tagging_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'To Tank': str, 'From Tank': str, 'Year': str,
                                         'Month': str, 'Day': str})
        data = data.mask(data == 'None', None).mask(data == '', None).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prepare data:
    grp_id = False
    try:
        if len(data["Group"].unique()) > 1 or len(data["Stock"].unique()) > 1:
            log_data += "\n WARNING: Form only designed for use with single group. Check \"Group\" column and split" \
                        " sheet if needed. \n"

        year, coll = utils.year_coll_splitter(data["Group"][0])
        grp_qs = models.Group.objects.filter(stok_id__name=data_dict[0]["Stock"],
                                             coll_id__name__icontains=coll,
                                             grp_year=year)
        if len(grp_qs) == 1:
            grp_id = grp_qs.get().pk
        elif len(grp_qs) > 1:
            for grp in grp_qs:
                tank_list = grp.current_tank()
                if str(data["From Tank"][0]) in [tank.name for tank in tank_list]:
                    grp_id = grp.pk

        if grp_id:
            anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp_id)

        salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        stok_id = models.StockCode.objects.filter(name=data["Stock"][0]).get()
        coll_id = models.Collection.objects.filter(name__icontains=coll).get()
        tagger_code = models.RoleCode.objects.filter(name__iexact="Tagger").get()

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error finding origin group (check first row): \n"
        log_data += "Error: {}\n\n".format(err_msg)
        return log_data, False

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            year, coll = utils.year_coll_splitter(row["Group"])
            row_datetime = utils.get_row_date(row)
            row_date = row_datetime.date()
            indv_ufid = utils.nan_to_none(row["Universal Fish ID"])
            indv = models.Individual(grp_id_id=grp_id,
                                     spec_id=salmon_id,
                                     stok_id=stok_id,
                                     coll_id=coll_id,
                                     indv_year=year,
                                     pit_tag=row["PIT tag"],
                                     ufid=indv_ufid,
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

            if not row["From Tank"] == "nan" and not row["To Tank"] == "nan":
                in_tank = models.Tank.objects.filter(name=row["From Tank"]).get()
                out_tank = models.Tank.objects.filter(name=row["To Tank"]).get()
                if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                              indv_pk=indv.pk):
                    row_entered = True

            anix_indv = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Vial"], "Vial", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Box"], "Box", None):
                row_entered = True

            if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, row["Location"], "Box Location", None):
                row_entered = True

            if utils.nan_to_none(row["Tagger"]):
                perc_list, inits_not_found = utils.team_list_splitter(row["Tagger"])
                for perc_id in perc_list:
                    team_id = utils.add_team_member(perc_id, cleaned_data["evnt_id"], role_id=tagger_code,
                                                    return_team=True)
                    if team_id:
                        row_entered = True
                        utils.enter_anix(cleaned_data, indv_pk=indv.pk, team_pk=team_id.pk)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) for row with pit tag {}\n".format(inits,
                                                                                                         row["PIT tag"])

            if utils.nan_to_none(row["Comments"]):
                comments_parsed = utils.comment_parser(row["Comments"], anix_indv, det_date=row_datetime.date())
                if not comments_parsed:
                    log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row["PIT tag"],
                                                                                            row["Comments"])

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False

        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    # handle general data:
    try:
        from_tanks = data["From Tank"].value_counts()
        for tank_name in from_tanks.keys():
            fish_tagged_from_tank = int(from_tanks[tank_name])
            contx = utils.enter_tank_contx(tank_name, cleaned_data, None, grp_pk=grp_id, return_contx=True)
            if contx:
                utils.enter_cnt(cleaned_data, fish_tagged_from_tank, contx.pk, cnt_code="Pit Tagged")

    except Exception as err:
        err_msg = utils.common_err_parser(err)
        log_data += "Error parsing common data (recording counts on tank movements)\n "
        log_data += "\n Error: {}".format(err_msg)
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def mactaquac_tagging_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'Origin Pond': str, "PIT": str, 'Year': str, 'Month': str, 'Day': str})
        data = data.mask(data == 'None', None).mask(data == '', None).dropna(how="all")
        data["Comments"] = data["Comments"].fillna('')
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # Prepare data:
    grp_id = False
    try:
        if len(data["Collection"].unique()) > 1 or len(data["Stock"].unique()) > 1:
            log_data += "\n WARNING: Form only designed for use with single group. Check \"Collection\"" \
                        " column and split sheet if needed. \n"

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

        if grp_id:
            anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp_id)

        salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        stok_id = models.StockCode.objects.filter(name=data["Stock"][0]).get()
        coll_id = models.Collection.objects.filter(name__icontains=coll).get()
        tagger_code = models.RoleCode.objects.filter(name__iexact="Tagger").get()

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error finding origin group (check first row): \n"
        log_data += "Error: {}\n\n".format(err_msg)
        return log_data, False

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            year, coll = utils.year_coll_splitter(row["Collection"])
            row_datetime = utils.get_row_date(row)
            indv = models.Individual(grp_id_id=grp_id,
                                     spec_id=salmon_id,
                                     stok_id=stok_id,
                                     coll_id=coll_id,
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
                in_tank = models.Tank.objects.filter(name=row["Origin Pond"]).get()
                out_tank = models.Tank.objects.filter(name=row["Destination Pond"]).get()
                if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                              indv_pk=indv.pk):
                    row_entered = True

            anix_indv = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

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

            if utils.nan_to_none(row["Crew"]):
                perc_list, inits_not_found = utils.team_list_splitter(row["Crew"])
                for perc_id in perc_list:
                    team_id = utils.add_team_member(perc_id, cleaned_data["evnt_id"], role_id=tagger_code,
                                                    return_team=True)
                    if team_id:
                        row_entered = True
                        utils.enter_anix(cleaned_data, indv_pk=indv.pk, team_pk=team_id.pk)
                for inits in inits_not_found:
                    log_data += "No valid personnel with initials ({}) from row with pit tag {}\n".format(inits, row[
                        "PIT"])

            if utils.nan_to_none(row["Comments"]):
                comments_parsed = utils.comment_parser(row["Comments"], anix_indv, det_date=row_datetime.date())
                if not comments_parsed:
                    log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row["PIT"],
                                                                                            row["Comments"])

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    # handle general data:
    try:
        from_tanks = data["Origin Pond"].value_counts()
        for tank_name in from_tanks.keys():
            fish_tagged_from_tank = int(from_tanks[tank_name])
            contx = utils.enter_tank_contx(tank_name, cleaned_data, None, grp_pk=grp_id, return_contx=True)
            if contx:
                utils.enter_cnt(cleaned_data, fish_tagged_from_tank, contx.pk, cnt_code="Pit Tagged")

    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error parsing common data (recording counts on tank movements)\n "
        log_data += "\n Error: {}".format(err_msg)
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False
    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
