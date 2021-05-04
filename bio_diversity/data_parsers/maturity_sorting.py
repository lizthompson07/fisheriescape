import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants


def mactaquac_maturity_sorting_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'PIT': str, 'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data["COMMENTS"] = data["COMMENTS"].fillna('')
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    sex_dict = calculation_constants.sex_dict

    for row in data_dict:
        row_entered = False
        try:
            row_datetime = utils.get_row_date(row)
            row_date = row_datetime.date()
            indv_qs = models.Individual.objects.filter(pit_tag=row["PIT"])
            if len(indv_qs) == 1:
                indv = indv_qs.get()
            else:
                log_data += "Error parsing row: \n"
                log_data += str(row)
                log_data += "\nFish with PIT {} not found in db\n".format(row["PIT"])
                log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                            "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
                return log_data, False

            anix_indv, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv.pk)
            row_entered += anix_entered

            row_entered += utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, sex_dict[row["SEX"]], "Gender", None,
                                             comments=row["COMMENTS"])

            if utils.nan_to_none(row["ORIGIN POND"]) and utils.nan_to_none(row["DESTINATION POND"]):
                in_tank = models.Tank.objects.filter(name=row["ORIGIN POND"]).get()
                out_tank = models.Tank.objects.filter(name=row["DESTINATION POND"]).get()
                row_entered += utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                                          indv_pk=indv.pk)

            if utils.nan_to_none(row["COMMENTS"]):
                comments_parsed, data_entered = utils.comment_parser(row["COMMENTS"], anix_indv, row_date)
                row_entered += data_entered
                if not comments_parsed:
                    log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row["PIT"],
                                                                                            row["COMMENTS"])

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

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
