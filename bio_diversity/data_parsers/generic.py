import copy
import pandas as pd

from bio_diversity import models
from bio_diversity import utils


def parser_template(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0

    # loading data:
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=1, engine='openpyxl',
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prepare rows before iterating:
    try:
        pass
    except Exception as err:
        log_data += "\n Error preparing data: {}".format(err.__str__())
        return log_data, False

    # iterate over rows
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            pass
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

    # enter general data once all rows are entered:
    try:
        pass
    except Exception as err:
        log_data += "Error parsing common data: \n"
        log_data += "\n Error: {}".format(err.__str__())
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def generic_indv_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'PIT': str, 'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # data prep:
    sex_dict = {"M": "Male",
                "F": "Female",
                "I": "Immature"}
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            indv_qs = models.Individual.objects.filter(pit_tag=row["PIT"])
            if len(indv_qs) == 1:
                indv = indv_qs.get()
            else:
                row_entered = False
                row_parsed = False
                indv = False
                log_data += "Error parsing row: \n"
                log_data += str(row)
                log_data += "\nFish with PIT {} not found in db\n".format(row["PIT"])

            if indv:
                anix = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

                row_datetime = utils.get_row_date(row)
                row_date = row_datetime.date()
                if utils.nan_to_none(row["Sex"]):
                    if utils.enter_indvd(anix.pk, cleaned_data, row_date, sex_dict[row["Sex"]], "Gender", None, None):
                        row_entered = True
                if utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None):
                    row_entered = True
                if utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None):
                    row_entered = True
                if utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Vial"], "Vial", None):
                    row_entered = True
                if utils.nan_to_none(row["Precocity (Y/N)"]):
                    if row["Precocity (Y/N)"].upper() == "Y":
                        if utils.enter_indvd(anix.pk, cleaned_data, row_date, None, "Animal Health",
                                             "Tissue Sample"):
                            row_entered = True
                if utils.nan_to_none(row["Mortality (Y/N)"]):
                    if row["Mortality (Y/N)"].upper() == "Y":
                        mort_evnt, mort_anix = utils.enter_mortality(indv, cleaned_data, row_date)
                if utils.nan_to_none(row["Tissue Sample (Y/N)"]):
                    if row["Tissue Sample (Y/N)"].upper() == "Y":
                        if utils.enter_indvd(anix.pk, cleaned_data, row_date, None, "Animal Health",
                                             "Tissue Sample"):
                            row_entered = True

                if utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Scale Envelope"], "Scale Envelope", None):
                    row_entered = True

                if not row["Origin Pond"] == "nan" and not row["Destination Pond"] == "nan":
                    in_tank = models.Tank.objects.filter(name=row["Origin Pond"]).get()
                    out_tank = models.Tank.objects.filter(name=row["Destination Pond"]).get()
                    if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                                  indv_pk=indv.pk):
                        row_entered = True

                if utils.nan_to_none(row["COMMENTS"]):
                    utils.comment_parser(row["COMMENTS"], anix, row_date)
            else:
                break

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


def generic_grp_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prep data:
    sex_dict = {"M": "Male",
                "F": "Female",
                "I": "Immature"}

    data["datetime"] = data.apply(lambda row: utils.get_row_date(row), axis=1)
    data["grp_year"] = data.apply(lambda row: utils.year_coll_splitter(row["Year Class"])[0], axis=1)
    data["grp_coll"] = data.apply(lambda row: utils.year_coll_splitter(row["Year Class"])[1], axis=1)

    tank_qs = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"])
    tank_dict = {tank.name: tank for tank in tank_qs}
    data["start_tank_id"] = data.apply(lambda row: tank_dict[row["Origin Pond"]], axis=1)
    data["end_tank_id"] = data.apply(lambda row: tank_dict[row["Destination Pond"]], axis=1)

    data["grp_key"] = data["River"] + data["Year Class"] + data["Origin Pond"] + data["Group"].astype(str) + \
                      data["datetime"].astype(str)
    data["end_grp_key"] = data["River"] + data["Year Class"] + data["Destination Pond"] + data["Group"].astype(str) + \
                          data["datetime"].astype(str)

    start_grp_data = data.groupby(["River", "grp_year", "grp_coll", "start_tank_id", "Group", "datetime", "grp_key"],
                              dropna=False, sort=False).size().reset_index()
    start_grp_data["start_grp_id"] = start_grp_data.apply(lambda row: utils.get_grp(row["River"], row["grp_year"], row["grp_coll"],
                                                                          row["start_tank_id"], at_date=row["datetime"],
                                                                          prog_str=row["Group"])[0], axis=1)
    start_grp_dict = dict(zip(start_grp_data['grp_key'], start_grp_data['start_grp_id']))
    for item, grp in start_grp_dict.items():
        utils.enter_anix(cleaned_data, grp_pk=grp.pk)

    end_grp_data = data.groupby(["River", "grp_year", "grp_coll", "end_tank_id", "start_tank_id", "Group", "datetime", "grp_key", "end_grp_key"],
                              dropna=False, sort=False).size().reset_index()
    end_grp_dict = {}
    for row in end_grp_data.to_dict('records'):
        grps = utils.get_grp(row["River"], row["grp_year"], row["grp_coll"], row["end_tank_id"], at_date=row["datetime"],
                              prog_str=row["Group"])
        start_grp_id = start_grp_dict[row["grp_key"]]
        start_contx = utils.enter_contx(row["start_tank_id"], cleaned_data, None, grp_pk=start_grp_id.pk,
                                        return_contx=True)

        if len(grps) > 0:
            end_grp_id = grps[0]
            end_grp_dict[row["end_grp_key"]] = grps[0]
        else:
            end_grp_id = copy.deepcopy(start_grp_id)
            end_grp_id.pk = None
            end_grp_id.save()
            end_grp_dict[row["end_grp_key"]] = end_grp_id

        grp_anix = utils.enter_anix(cleaned_data, grp_pk=end_grp_id.pk)
        utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, "Parent Group", frm_grp_id=start_grp_id)
        utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, "Program Group", row["Group"])
        utils.enter_contx(row["start_tank_id"], cleaned_data, False, grp_pk=end_grp_id.pk)
        end_contx = utils.enter_contx(row["end_tank_id"], cleaned_data, True, grp_pk=end_grp_id.pk, return_contx=True)
        utils.enter_cnt(cleaned_data, row[0], end_contx.pk)
        utils.enter_cnt(cleaned_data, row[0], start_contx.pk, cnt_code="Fish Removed from Container")


    # iterate through the rows:
    data_dict = data.to_dict('records')
    data_dict = {}
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_date = row["datetime"].date()

            end_tank_id = None
            if utils.nan_to_none(row["Origin Pond"]) != utils.nan_to_none(row["Destination Pond"]):
                start_tank_id = models.Tank.objects.filter(name__iexact=row["Origin Pond"],
                                                           facic_id=cleaned_data["facic_id"]).get()
                end_tank_id = models.Tank.objects.filter(name__iexact=row["Destination Pond"],
                                                         facic_id=cleaned_data["facic_id"]).get()
            year, coll = utils.year_coll_splitter(row["Year Class"])

            grps = utils.get_grp(row["River"], year, coll, start_tank_id, at_date=row["datetime"], prog_str=row["Group"])
            if len(grps) == 1:
                grp_id = grps[0]
                utils.enter_anix(cleaned_data, grp_pk=grp_id.pk)
            else:
                raise Exception("\nGroup {}-{}-{} in container: {} and program group {} not uniquely found in"
                                " db\n".format(row["River"], year, coll, start_tank_id.name, row["Group"]))

            # get group at destination:
            end_grp_id = None
            if end_tank_id:

                row_indv = models.Individual(stok_id=end_grp_id.stok_id,
                                             coll_id=end_grp_id.coll_id,
                                             indv_year=end_grp_id.grp_year,
                                             spec_id=end_grp_id.spec_id,
                                             indv_valid=False,
                                             grp_id=end_grp_id,
                                             created_by=end_grp_id.created_by,
                                             created_date=end_grp_id.created_date,
                                             )
                row_indv.clean()
                row_indv.save()
                row_anix = utils.enter_anix(cleaned_data, indv_pk=row_indv.pk)
            else:
                row_indv = models.Individual(stok_id=grp_id.stok_id,
                                             coll_id=grp_id.coll_id,
                                             indv_year=grp_id.grp_year,
                                             spec_id=grp_id.spec_id,
                                             indv_valid=False,
                                             grp_id=grp_id,
                                             created_by=grp_id.created_by,
                                             created_date=grp_id.created_date,
                                             )
                row_indv.clean()
                row_indv.save()
                row_anix = utils.enter_anix(cleaned_data, indv_pk=row_indv.pk)

            if row_indv:
                if utils.nan_to_none(row["Sex"]):
                    if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, sex_dict[row["Sex"]], "Gender", None,
                                         None):
                        row_entered = True
                if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None):
                    row_entered = True
                if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None):
                    row_entered = True
                if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Vial"], "Vial", None):
                    row_entered = True
                if utils.nan_to_none(row["Precocity (Y/N)"]):
                    if row["Precocity (Y/N)"].upper() == "Y":
                        if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, None, "Animal Health",
                                             "Tissue Sample"):
                            row_entered = True
                if utils.nan_to_none(row["Mortality (Y/N)"]):
                    if row["Mortality (Y/N)"].upper() == "Y":
                        mort_evnt, mort_anix = utils.enter_mortality(row_anix, cleaned_data, row_date)
                if utils.nan_to_none(row["Tissue Sample (Y/N)"]):
                    if row["Tissue Sample (Y/N)"].upper() == "Y":
                        if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, None, "Animal Health",
                                             "Tissue Sample"):
                            row_entered = True

                if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Scale Envelope"], "Scale Envelope",
                                     None):
                    row_entered = True

                if utils.nan_to_none(row["COMMENTS"]):
                    utils.comment_parser(row["COMMENTS"], row_anix, row_date)
            else:
                break

        except Exception as err:
            # nuke all valid individuals associated with the event
            fish_deleted = models.Individual.objects.filter(animal_details__evnt_id=cleaned_data["evnt_id"]).delete()
            nfish_deleted = fish_deleted[1]["bio_diversity.Individual"]
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err.__str__())
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database \n {} rows deleted from database".format(rows_parsed, len(data_dict), rows_entered,
                                                                           len(data_dict), nfish_deleted)
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
