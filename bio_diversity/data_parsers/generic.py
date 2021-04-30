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
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False


    # prep data:
    sex_dict = {"M": "Male",
                "F": "Female",
                "I": "Immature"}

    # iterate through the rows:
    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            row_datetime =utils.get_row_date(row)
            row_date = row_datetime.date()

            end_tank_id = None
            if utils.nan_to_none(row["Origin Pond"]) != utils.nan_to_none(row["Destination Pond"]):
                start_tank_id = models.Tank.objects.filter(name__iexact=row["Origin Pond"]).get()
                end_tank_id = models.Tank.objects.filter(name__iexact=row["Destination Pond"]).get()
            year, coll = utils.year_coll_splitter(row["Year Class"])
            prog_grp = None
            if utils.nan_to_none(row["Group"]):
                prog_grp = models.AniDetSubjCode.objects.filter(name__iexact=row["Group"]).get()
            grps = utils.get_grp(row["River"], year, coll, start_tank_id, at_date=row_datetime, prog_grp=prog_grp)
            if len(grps) == 1:
                grp_id = grps[0]
                utils.enter_anix(cleaned_data, grp_pk=grp_id.pk)
            else:
                raise Exception("\nGroup {}-{}-{} in container: {} and program group {} not uniquely found in" \
                            " db\n".format(row["River"], year, coll, start_tank_id.name, row["Group"]))

            # get group at destination:
            end_grp_id = None
            if end_tank_id:
                grps = utils.get_grp(row["River"], year, coll, end_tank_id, at_date=row_datetime, prog_grp=prog_grp)
                if len(grps) > 0:
                    end_grp_id = grps[0]
                else:
                    end_grp_id = copy.deepcopy(grp_id)
                    end_grp_id.pk = None
                    end_grp_id.save()
                    grp_anix = utils.enter_anix(cleaned_data, grp_pk=end_grp_id.pk)
                    utils.enter_grpd(grp_anix.pk, cleaned_data, row_date, None, "Parent Group", frm_grp_id=grp_id)
                    utils.enter_grpd(grp_anix.pk, cleaned_data, row_date, None, "Program Group", row["Group"])
                    utils.enter_contx(start_tank_id, cleaned_data, False, grp_pk=end_grp_id.pk)
                    utils.enter_contx(end_tank_id, cleaned_data, True, grp_pk=end_grp_id.pk)

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
                    if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, sex_dict[row["Sex"]], "Gender", None, None):
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

                if utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Scale Envelope"], "Scale Envelope", None):
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
