
from datetime import datetime
import pytz
import pandas as pd
from pandas import read_excel

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


class DataLoggerTemperatureParser(DataParser):
    temp_key = "Temperature (°C)"
    date_key = "Date(yyyy-mm-dd)"
    time_key = "Time(hh:mm:ss)"

    def load_data(self):
        self.mandatory_keys = []
        super(DataLoggerTemperatureParser, self).load_data()

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
                                        envc_id, env_time=row["datetime"].time(), contx=contx,
                                        save=False, qual_id=qual_id), axis=1)
        entered_list = models.EnvCondition.objects.bulk_create(list(self.data["env"].dropna()))
        self.rows_parsed = len(self.data["env"])
        self.row_entered = len(self.data["env"].dropna())

    def iterate_rows(self):
        pass


class TemperatureParser(DataParser):
    temp_key = "Temperature (C)"
    trof_key = "Trough"

    header = 2
    sheet_name = "Temperatures"
    converters = {trof_key: str, "Time": str, 'Year': str, 'Month': str, 'Day': str}
    qual_id = None
    envc_id = None

    def data_preper(self):
        self.qual_id = models.QualCode.objects.filter(name="Good").get()
        self.envc_id = models.EnvCode.objects.filter(name="Temperature").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row, get_time=True)

        trof_list = utils.parse_trof_str(row.get(self.trof_key), cleaned_data["facic_id"])
        for trof_id in trof_list:
            row_contx, contx_entered = utils.enter_contx(trof_id, cleaned_data, final_flag=None, return_contx=True)
            self.row_entered += contx_entered

            self.row_entered += utils.enter_env(row[self.temp_key], row_datetime.date(), cleaned_data,
                                                self.envc_id, env_time=row_datetime.time(), contx=row_contx,
                                                save=True, qual_id=self.qual_id)


