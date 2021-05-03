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
                log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                            "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
                return log_data, False

            if indv:
                anix_indv = utils.enter_anix(cleaned_data, indv_pk=indv.pk)

                row_datetime = utils.get_row_date(row)
                row_date = row_datetime.date()
                if utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, sex_dict[row["SEX"]], "Gender", None,
                                     comments=row["COMMENTS"]):
                    row_entered = True

                if not row["ORIGIN POND"] == "nan" and not row["DESTINATION POND"] == "nan":
                    in_tank = models.Tank.objects.filter(name=row["ORIGIN POND"]).get()
                    out_tank = models.Tank.objects.filter(name=row["DESTINATION POND"]).get()
                    if utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                                  indv_pk=indv.pk):
                        row_entered = True

                    row_entered = True

                if row["COMMENTS"]:
                    utils.comment_parser(row["COMMENTS"], anix_indv, row_date)
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
