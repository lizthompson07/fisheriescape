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
        evnt_date = cleaned_data["evnt_id"].start_date
        nfish = utils.nan_to_none(row.get(self.cnt_key))
        comments = utils.nan_to_none(row.get(self.comment_key))

        if utils.nan_to_none(row.get(self.grp_pk_key)):
            grp_id = models.Group.objects.filter(pk=row.get(self.grp_pk_key)).get()

            if comments:
                anix = utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, return_anix=True)
                utils.enter_bulk_grpd(anix.pk, cleaned_data, evnt_date, comments=comments)

            if utils.nan_to_none(row.get(self.cont_key)):
                new_cont_id = models.Tank.objects.filter(name=row.get(self.cont_key),
                                                         facic_id=cleaned_data["facic_id"]).get()

                # check if another group was already in the tank:
                prog_grp = grp_id.prog_group()
                mark = grp_id.group_mark()

                grp_list = utils.get_grp(grp_id.stok_id.__str__(), grp_id.grp_year, grp_id.coll_id.__str__(),
                                         cont=new_cont_id, prog_grp=prog_grp, grp_mark=mark)

                if grp_list and grp_id not in grp_list:
                    end_grp = grp_list[0]
                else:
                    end_grp = None

                utils.enter_move_cnts(cleaned_data, None, new_cont_id, evnt_date, start_grp_id=grp_id,
                                      end_grp_id=end_grp, nfish=nfish, whole_grp=True)

            if utils.nan_to_none(row.get(self.remove_key)):
                grp_id.grp_valid = False
                grp_id.save()

