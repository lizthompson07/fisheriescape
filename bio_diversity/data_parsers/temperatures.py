
from datetime import datetime
import pytz
import pandas as pd

from bio_diversity import models
from bio_diversity import utils


def temperature_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    try:
        data = pd.read_csv(cleaned_data["data_csv"], encoding='ISO-8859-1', header=7)
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prep the data:
    try:
        contx = utils.enter_trof_contx(cleaned_data["trof_id"].name, cleaned_data, final_flag=None, return_contx=True)
        qual_id = models.QualCode.objects.filter(name="Good").get()
        envc_id = models.EnvCode.objects.filter(name="Temperature").get()

        data["datetime"] = data.apply(lambda row: datetime.strptime(row["Date(yyyy-mm-dd)"] + ", " + row["Time(hh:mm:ss)"],
                                                                    "%Y-%m-%d, %H:%M:%S").replace(tzinfo=pytz.UTC), axis=1)

        data["env"] = data.apply(lambda row: utils.enter_env(row["Temperature (°C)"], row["datetime"].date(), cleaned_data,
                                                             envc_id, env_start=row["datetime"].time(), contx=contx,
                                                             save=False, qual_id=qual_id), axis=1)
    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error preparing data for entry \n "
        log_data += "\n Error: {}".format(err_msg)
        return log_data, False

    # enter the data
    try:
        entered_list = models.EnvCondition.objects.bulk_create(list(data["env"].dropna()))
    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error with bulk data entry \n "
        log_data += "\n Error: {}".format(err_msg)
        return log_data, False

    return log_data, True
