from datetime import datetime, timedelta

import pytz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


# ED = egg development
class EDInitParser(DataParser):
    stock_key = "Stock"
    prog_key = "Program"
    trof_key = "Trough"
    cross_key = "Cross"
    tray_key = "Tray"
    fecu_key = "Fecundity"
    comment_key = "Comments"

    header = 1
    comment_row = [2]
    sheet_name = "Init"
    converters = {trof_key: str, tray_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}

    def load_data(self):
        self.mandatory_keys.extend([self.stock_key, self.trof_key, self.tray_key, self.cross_key])
        self.mandatory_filled_keys.extend([self.stock_key, self.tray_key, self.trof_key, self.cross_key])
        super(EDInitParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data

        trof_qs = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"])
        len(trof_qs)  # force eval of lazy qs
        trof_dict = {trof.name: trof for trof in trof_qs}
        self.data["trof_id"] = self.data.apply(lambda row: trof_dict[row[self.trof_key]], axis=1)

        stok_qs = models.StockCode.objects.all()
        len(stok_qs)  # force eval of lazy qs
        stok_dict = {stok.name: stok for stok in stok_qs}
        self.data["stok_id"] = self.data.apply(lambda row: stok_dict[row[self.stock_key]], axis=1)

        self.data_dict = self.data.to_dict('records')

    def row_parser(self, row):
        # need to: find the pair's group, link it to it's pairing, create a tray, and add the count.
        cleaned_data = self.cleaned_data
        row_date = utils.get_row_date(row)
        pair_list = utils.get_pair(row[self.cross_key], row["stok_id"], row[self.year_key], prog_grp=utils.nan_to_none(row.get(self.prog_key)), fail_on_not_found=True)
        if len(pair_list) == 1:
            pair_id = pair_list[0]
        else:
            raise Exception("Too many pairs found for row \n{}".format(row))

        anix_id = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id').first()
        grp_id = anix_id.grp_id
        self.row_entered += utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, return_sucess=True)

        tray_id = utils.create_tray(row["trof_id"], row[self.tray_key], row_date, cleaned_data)
        grp_list = tray_id.fish_in_cont(row_date, get_grp=True)
        if grp_list and grp_id not in grp_list:
            end_grp = grp_list[0]
        else:
            end_grp = grp_id
        start_cnt, end_cnt, move_entered = utils.enter_move_cnts(cleaned_data, None, tray_id, row_date,
                                                                 start_grp_id=grp_id, end_grp_id=end_grp,
                                                                 set_origin_if_none=False)
        self.row_entered += move_entered
        end_anix, contx, contx_entered = utils.enter_contx(tray_id, cleaned_data, grp_pk=end_grp.pk, return_anix=True)
        self.row_entered += contx_entered

        if utils.nan_to_none(row.get(self.fecu_key)):
            self.row_entered += utils.enter_cnt(cleaned_data, row[self.fecu_key], row_date, anix_pk=end_anix.pk,
                                                cnt_code="Photo Count")[1]

        self.row_entered += utils.enter_bulk_grpd(end_anix.pk, cleaned_data, row_date,
                                                  comments=row.get(self.comment_key))


# ED = egg development
class EDPickParser(DataParser):
    # used to create record picks taken from groups
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    tray_key = "Tray"
    hu_key = "Heath Unit Location"
    shocking_key = "Shocking (Y/N)"
    first_key = "First Hatch Observed (Y/N)"
    all_hatch_key = "100% Hatch Observed (Y/N)"
    comment_key = "Comments"

    header = 1
    comment_row = [2]
    sheet_name = "Picking"
    converters = {trof_key: str, tray_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}
    default_pickc_id = None
    ani_health_anidc_id = None

    date_dict = {}

    def load_data(self):
        self.mandatory_keys.extend([self.stock_key, self.trof_key, self.cross_key, self.tray_key])
        super(EDPickParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.default_pickc_id = models.CountCode.objects.filter(name="Cleaning Loss").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()

        for pickc_id in cleaned_data["pickc_id"]:
            if pickc_id.name not in self.data.keys():
                raise Exception("No column named {} in worksheet to match pick types choices".format(pickc_id.name))

        trof_qs = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"])
        len(trof_qs)  # force eval of lazy qs
        trof_dict = {trof.name: trof for trof in trof_qs}
        self.data["trof_id"] = self.data.apply(lambda row: trof_dict[row[self.trof_key]], axis=1)

        stok_qs = models.StockCode.objects.all()
        len(stok_qs)  # force eval of lazy qs
        stok_dict = {stok.name: stok for stok in stok_qs}
        self.data["stok_id"] = self.data.apply(lambda row: stok_dict[row[self.stock_key]], axis=1)

        self.data_dict = self.data.to_dict('records')

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = utils.get_row_date(row)

        # find group from either cross or tray:
        if utils.nan_to_none(row.get(self.hu_key)):
            cont_id = utils.get_cont_from_dot(row[self.hu_key], cleaned_data, row_date)
        elif utils.nan_to_none(row.get(self.tray_key)):
            cont_id = models.Tray.objects.filter(trof_id=row["trof_id"], end_date__isnull=True, name=row[self.tray_key]).get()
        else:
            cont_id = row["trof_id"]

        if utils.nan_to_none(row.get(self.cross_key)):
            pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                    indv_id__stok_id=row["stok_id"], start_date__year=row[self.year_key]).first()
            grp_id = utils.get_tray_group(pair_id, cont_id, row_date)
        else:
            grp_id = cont_id.fish_in_cont(row_date, get_grp=True)

        grp_anix, grp_contx, contx_entered = utils.enter_contx(row["trof_id"], cleaned_data, grp_pk=grp_id.pk,
                                                               return_anix=True)
        self.row_entered += contx_entered
        for pickc_id in cleaned_data["pickc_id"]:
            if utils.nan_to_none(row[pickc_id.name]):
                self.row_entered += utils.enter_cnt(cleaned_data, row[pickc_id.name], row_date, anix_pk=grp_anix.pk,
                                                    cnt_code=pickc_id.name)[1]

        # extra pick columns
        for col_name in row.keys():
            col_date = utils.get_col_date(col_name)

            if col_date:
                col_date_str = datetime.strftime(col_date, "%Y-%b-%d")
                self.date_dict[col_date_str] = True
                if utils.nan_to_none(row.get(col_name)):
                    self.row_entered += utils.enter_cnt(cleaned_data, row[col_name], col_date, anix_pk=grp_anix.pk,
                                                        cnt_code=self.default_pickc_id.name)[1]

        self.row_entered += utils.enter_bulk_grpd(grp_anix.pk, cleaned_data, row_date,
                                                  comments=row.get(self.comment_key))

        # record development and shocking:
        if utils.y_n_to_bool(row.get(self.shocking_key)):
            dev_at_shock = grp_id.get_development(row_date)
            self.row_entered += utils.enter_grpd(grp_anix.pk, self.cleaned_data, row_date, dev_at_shock, None,
                                                 anidc_str="Development")
            self.row_entered += utils.enter_grpd(grp_anix.pk, self.cleaned_data, row_date, "Shocking",
                                                 anidc_pk=self.ani_health_anidc_id.pk, adsc_str="Shocking")

    def data_cleaner(self):
        self.log_data += "\nDate columns read from headers:"
        for date_str in self.date_dict.keys():
            self.log_data += "{}\n".format(date_str)


# ED = egg development
# HU = Heath Unit
class EDHUParser(DataParser):
    # used to create record movements into heath units
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    tray_key = "Tray"
    prog_key = "Program"
    cnt_key = "Count"
    weight_key = "Weight (g)"
    cont_key = "Destination"
    loss_key = "Transfer Loss"
    final_key = "Final (Y/N)"
    comment_key = "Comments"

    end_trof_key = "End Trough"
    end_tray_key = "End Tray"
    heatl_key = "Heath Unit Location"
    tank_key = "Tank"

    header = 1
    comment_row = [2]
    sheet_name = "Allocations"
    converters = {trof_key: str, cross_key: str, tray_key: str, cont_key: str, 'Year': str, 'Month': str, 'Day': str}

    def load_data(self):
        self.mandatory_keys.extend([self.stock_key, self.trof_key, self.cross_key, self.tray_key,
                                    self.prog_key, self.cnt_key, self.cont_key])
        super(EDHUParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data

        trof_qs = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"])
        len(trof_qs)  # force eval of lazy qs
        trof_dict = {trof.name: trof for trof in trof_qs}
        self.data["trof_id"] = self.data.apply(lambda row: trof_dict[row[self.trof_key]], axis=1)

        stok_qs = models.StockCode.objects.all()
        len(stok_qs)  # force eval of lazy qs
        stok_dict = {stok.name: stok for stok in stok_qs}
        self.data["stok_id"] = self.data.apply(lambda row: stok_dict[row[self.stock_key]], axis=1)

        self.data_dict = self.data.to_dict('records')

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        # get tray, group, and row date
        row_date = utils.get_row_date(row)

        tray_qs = models.Tray.objects.filter(trof_id=row["trof_id"], name=row[self.tray_key])
        tray_id = tray_qs.filter(Q(start_date__lte=row_date, end_date__gte=row_date) | Q(end_date__isnull=True)).get()
        hu_cont = utils.get_cont_from_dot(row[self.cont_key], cleaned_data, row_date)

        # find start group/container:
        pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                indv_id__stok_id=row["stok_id"], start_date__year=row[self.year_key]).first()
        if tray_id:
            grp_id = utils.get_tray_group(pair_id, tray_id, row_date)
            start_cont = tray_id
        elif hu_cont:
            grp_id = utils.get_tray_group(pair_id, hu_cont, row_date)
            start_cont = hu_cont
        else:
            raise Exception("No start container found")

        # find end group/container
        cont = None
        if utils.nan_to_none(row[self.end_tray_key]):
            trof_id = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"],
                                                   name=row[self.end_trof_key]).get()
            tray_qs = models.Tray.objects.filter(trof_id=trof_id, name=row[self.tray_key])
            cont = tray_qs.filter(
                Q(start_date__lte=row_date, end_date__gte=row_date) | Q(end_date__isnull=True)).get()
        elif utils.nan_to_none(row[self.end_trof_key]):
            cont = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"],
                                                name=row[self.end_trof_key]).get()
        elif utils.nan_to_none(row[self.heatl_key]):
            cont = utils.get_cont_from_dot(row[self.cont_key], cleaned_data, row_date)
        elif utils.nan_to_none(row[self.tank_key]):
            cont = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"], name=row[self.tank_key])

        grp_list = utils.get_grp(grp_id.stok_id.name, grp_id.grp_year, grp_id.coll_id.name, cont=cont,
                                 at_date=row_date, prog_str=utils.nan_to_none(row.get(self.prog_key)))
        if grp_list:
            end_grp_id = grp_list[0]
        else:
            end_grp_id = None

        whole_grp = utils.y_n_to_bool(row[self.final_key])
        start_cnt, end_cnt, data_entered = utils.enter_move_cnts(cleaned_data, start_cont, cont, row_date,
                                                                 nfish=row.get(self.cnt_key), start_grp_id=grp_id,
                                                                 end_grp_id=end_grp_id, whole_grp=whole_grp)
        self.row_entered += data_entered

        if utils.nan_to_none(row[self.prog_key]):
            utils.enter_bulk_grpd(end_cnt.anix_id, cleaned_data, row_date, prog_grp=row[self.prog_key])
            utils.enter_cnt_det(cleaned_data, start_cnt, row[self.cnt_key], "Program Group Split", row[self.prog_key])
            utils.enter_cnt_det(cleaned_data, end_cnt, row[self.cnt_key], "Program Group Split", row[self.prog_key])

        if utils.nan_to_none(row[self.weight_key]):
            utils.enter_cnt_det(cleaned_data, start_cnt, row[self.weight_key], "Weight")
            utils.enter_cnt_det(cleaned_data, end_cnt, row[self.weight_key], "Weight")

        if utils.nan_to_none(row[self.loss_key]):
            self.row_entered += utils.enter_cnt(cleaned_data, row[self.loss_key], row_date, anix_pk=end_cnt.anix_id.pk,
                                                cnt_code="HU Transfer Loss")[1]

        if whole_grp and  hasattr(start_cont, 'end_date'):
            start_cont.end_date = row_date
            start_cont.save()