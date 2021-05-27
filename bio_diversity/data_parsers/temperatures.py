
from datetime import datetime
import pytz
import pandas as pd
from pandas import read_excel

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


class TemperatureParser(DataParser):
    temp_key = "Temperature (°C)"
    date_key = "Date(yyyy-mm-dd)"
    time_key = "Time(hh:mm:ss)"

    def data_reader(self):
        self.data = pd.read_csv(self.cleaned_data["data_csv"], encoding='ISO-8859-1', header=7)
        # to keep parent parser classes happy:
        self.data_dict = {}

    def data_preper(self):
        cleaned_data = self.cleaned_data
        contx, data_entered = utils.enter_trof_contx(cleaned_data["trof_id"].name, cleaned_data, final_flag=None,
                                                     return_contx=True)
        qual_id = models.QualCode.objects.filter(name="Good").get()
        envc_id = models.EnvCode.objects.filter(name="Temperature").get()

        self.data["datetime"] = self.data.apply(
            lambda row: datetime.strptime(row[self.date_key] + ", " + row[self.time_key],
                                          "%Y-%m-%d, %H:%M:%S").replace(tzinfo=pytz.UTC), axis=1)

        self.data["env"] = self.data.apply(
            lambda row: utils.enter_env(row[self.temp_key], row["datetime"].date(), cleaned_data,
                                        envc_id, env_start=row["datetime"].time(), contx=contx,
                                        save=False, qual_id=qual_id), axis=1)
        entered_list = models.EnvCondition.objects.bulk_create(list(self.data["env"].dropna()))
        self.rows_parsed = len(self.data["env"])
        self.row_entered = len(self.data["env"].dropna())

    def iterate_rows(self):
        pass
