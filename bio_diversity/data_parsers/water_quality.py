import pytz
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


class WaterQualityParser(DataParser):
    tank_key = "Pond"
    time_key = "Time (24HR)"
    temp_key = "Temp °C"
    dox_key = "DO%"
    ph_key = "pH"
    dn_key = "Dissolved Nitrogen %"
    source_key = "Source"

    comment_key = "Comments"
    crew_key = "Initials"

    header = 2
    converters = {tank_key: str, 'Year': str, 'Month': str, 'Day': str}

    temp_envc_id = None
    oxlvl_envc_id = None
    ph_envc_id = None
    disn_envc_id = None
    ws_envc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.tank_key, self.crew_key])
        super(WaterQualityParser, self).load_data()

    def data_preper(self):
        self.temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
        self.oxlvl_envc_id = models.EnvCode.objects.filter(name="Oxygen Level").get()
        self.ph_envc_id = models.EnvCode.objects.filter(name="pH").get()
        self.disn_envc_id = models.EnvCode.objects.filter(name="Dissolved Nitrogen").get()
        self.ws_envc_id = models.EnvCode.objects.filter(name="Water Source").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        contx, data_entered = utils.enter_tank_contx(row[self.tank_key], cleaned_data, None, return_contx=True)
        self.row_entered += data_entered
        row_date = utils.get_row_date(row)
        if utils.nan_to_none(row[self.time_key]):
            row_time = row[self.time_key].replace(tzinfo=pytz.UTC)
        else:
            row_time = None

        if utils.nan_to_none(row.get(self.temp_key)):
            self.row_entered += utils.enter_env(row[self.temp_key], row_date, cleaned_data, self.temp_envc_id,
                                                contx=contx, env_time=row_time)
        if utils.nan_to_none(row.get(self.dox_key)):
            self.row_entered += utils.enter_env(row[self.dox_key], row_date, cleaned_data, self.oxlvl_envc_id,
                                                contx=contx, env_time=row_time)
        if utils.nan_to_none(row.get(self.ph_key)):
            self.row_entered += utils.enter_env(row[self.ph_key], row_date, cleaned_data, self.ph_envc_id, contx=contx,
                                                env_time=row_time)
        if utils.nan_to_none(row.get(self.dn_key)):
            self.row_entered += utils.enter_env(row[self.dn_key], row_date, cleaned_data, self.disn_envc_id,
                                                contx=contx, env_time=row_time)
        if utils.nan_to_none(row.get(self.source_key)):
            source_envsc_id = models.EnvSubjCode.objects.filter(name__icontains=row[self.source_key]).get()
            self.row_entered += utils.enter_env(row[self.source_key], row_date, cleaned_data, self.ws_envc_id,
                                                envsc_id=source_envsc_id, contx=contx, env_time=row_time)

        if utils.nan_to_none(row.get(self.crew_key)):
            perc_list, inits_not_found = utils.team_list_splitter(row[self.crew_key])
            for perc_id in perc_list:
                team_id, team_entered = utils.add_team_member(perc_id, cleaned_data["evnt_id"], return_team=True)
                self.row_entered += team_entered
                if team_id:
                    self.row_entered += utils.enter_tank_contx(row[self.tank_key], cleaned_data, team_pk=team_id.pk)
            for inits in inits_not_found:
                self.log_data += "No valid personnel with initials ({}) for row {} \n".format(inits, row)
