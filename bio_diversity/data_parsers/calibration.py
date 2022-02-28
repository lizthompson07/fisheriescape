from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class CalibrationParser(DataParser):
    cnt_key = "New Group Count "
    cont_key = "New Container"
    remove_key = "Remove Group"
    comment_key = "Comments"
    grp_pk_key = "Group ID"

    header = 2
    sheet_name = "Tank"
    converters = {cnt_key: str}

    def load_data(self):
        self.mandatory_keys = [self.cnt_key, self.cont_key, self.remove_key]
        super(CalibrationParser, self).load_data()

    def data_preper(self):
        pass

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        comments = utils.nan_to_none(row.get(self.comment_key))
        if utils.nan_to_none(row.get(self.grp_pk_key)):
            grp_id = models.Group.objects.filter(pk=row.get(self.grp_pk_key)).get()

            if utils.nan_to_none(row.get(self.cont_key)):
                new_cont_id = models.Tank.objects.filter(name=row.get(self.cont_key),
                                                         facic_id=cleaned_data["facic_id"]).get()
                current_conts = grp_id.current_cont()
                if new_cont_id != current_conts or len(current_conts) > 1:
                    for cont in current_conts:
                        if cont != new_cont_id:
                            utils.enter_contx(cont, cleaned_data, True, grp_pk=grp_id.pk)

            if utils.nan_to_none(row.get(self.cnt_key)):
                utils.enter_cnt(cleaned_data, cleaned_data["evnt_id"].start_date, row.get(self.cnt_key))


