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
    trof_key = "Trough"
    cross_key = "Cross"
    tray_key = "Tray"
    fecu_key = "Fecundity"
    comment_key = "Comments"

    header = 2
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
        pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                indv_id__stok_id=row["stok_id"], start_date__year=row[self.year_key]).get()

        anix_id = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id').first()
        grp_id = anix_id.grp_id
        self.row_entered += utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, return_sucess=True)

        tray_id = utils.create_tray(row["trof_id"], row[self.tray_key], row_date, cleaned_data)
        contx, contx_entered = utils.enter_contx(tray_id, cleaned_data, True, grp_pk=grp_id.pk, return_contx=True)
        self.row_entered += contx_entered

        if utils.nan_to_none(row.get(self.fecu_key)):
            cnt, cnt_entered = utils.enter_cnt(cleaned_data, row[self.fecu_key], contx_pk=contx.pk, cnt_code="Photo Count")
            self.row_entered += cnt_entered

        self.row_entered += utils.enter_bulk_grpd(anix_id.pk, cleaned_data, row_date,
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
    comment_key = "Comments"

    header = 2
    sheet_name = "Picking"
    converters = {trof_key: str, tray_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}
    default_pickc_id = None

    date_dict = {}

    def load_data(self):
        self.mandatory_keys.extend([self.stock_key, self.trof_key, self.cross_key, self.tray_key])
        super(EDPickParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.default_pickc_id = models.CountCode.objects.filter(name="Cleaning Loss").get()

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
        self.row_entered += utils.enter_contx(row["trof_id"], cleaned_data)
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

        grp_anix = None
        shock = False
        for pickc_id in cleaned_data["pickc_id"]:
            if utils.nan_to_none(row[pickc_id.name]):
                shock = utils.y_n_to_bool(row.get(self.shocking_key))
                grp_anix, evnt_entered = utils.create_picks_evnt(cleaned_data, cont_id, grp_id.pk, row[pickc_id.name],
                                                                 row_date, pickc_id.name,
                                                                 cleaned_data["evnt_id"].perc_id, shocking=shock,
                                                                 return_anix=True,
                                                                 pick_comments=row.get(self.comment_key))
                self.row_entered += evnt_entered

        for col_name in row.keys():
            col_date = utils.get_col_date(col_name)

            if col_date:
                col_date_str = datetime.strftime(col_date, "%Y-%b-%d")
                self.date_dict[col_date_str] = True
                if utils.nan_to_none(row.get(col_name)):
                    self.row_entered += utils.create_picks_evnt(cleaned_data, cont_id, grp_id.pk, row[col_name],
                                                                col_date, self.default_pickc_id,
                                                                cleaned_data["evnt_id"].perc_id,
                                                                pick_comments=row.get(self.comment_key))

        # record development
        if grp_anix and shock:
            pick_evnt_cleaned_data = cleaned_data.copy()
            pick_evnt_cleaned_data["evnt_id"] = grp_anix.evnt_id
            dev_at_pick = grp_id.get_development(row_date)
            utils.enter_grpd(grp_anix.pk, pick_evnt_cleaned_data, row_date, dev_at_pick, None,
                             anidc_str="Development")
            self.row_entered += utils.enter_contx(row["trof_id"], cleaned_data)

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

    header = 2
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
        pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                indv_id__stok_id=row["stok_id"], start_date__year=row[self.year_key]).first()

        grp_id = utils.get_tray_group(pair_id, tray_id, row_date)

        # want to shift the hu move event, so that the counting math always works out.
        hu_move_date = row_date + timedelta(minutes=1)
        hu_cleaned_data = utils.create_new_evnt(cleaned_data, "Allocation", hu_move_date)
        hu_anix, data_entered = utils.enter_anix(hu_cleaned_data, grp_pk=grp_id.pk)
        self.row_entered += data_entered
        hu_contx, data_entered = utils.enter_contx(tray_id, hu_cleaned_data, None, grp_pk=grp_id.pk,
                                                   return_contx=True)
        self.row_entered += data_entered
        # record development
        dev_at_hu_transfer = grp_id.get_development(hu_move_date)
        utils.enter_grpd(hu_anix.pk, hu_cleaned_data, hu_move_date, dev_at_hu_transfer, None,
                         anidc_str="Development")
        self.row_entered += utils.enter_contx(row["trof_id"], cleaned_data)

        # HU Picks:
        self.row_entered += utils.enter_cnt(cleaned_data, row[self.loss_key], hu_contx.pk,
                                            cnt_code="HU Transfer Loss")[1]

        # generate new group, cup, and movement event:
        cont = None
        if utils.nan_to_none(row[self.end_tray_key]):
            trof_id = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"], name=row[self.end_trof_key]).get()
            tray_qs = models.Tray.objects.filter(trof_id=trof_id, name=row[self.tray_key])
            cont = tray_qs.filter(
                Q(start_date__lte=row_date, end_date__gte=row_date) | Q(end_date__isnull=True)).get()
        elif utils.nan_to_none(row[self.end_trof_key]):
            cont = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"], name=row[self.end_trof_key]).get()
        elif utils.nan_to_none(row[self.heatl_key]):
            cont = utils.get_cont_from_dot(row[self.cont_key], cleaned_data, row_date)
        elif utils.nan_to_none(row[self.tank_key]):
            cont = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"], name=row[self.tank_key])

        self.row_entered += utils.enter_contx(cont, cleaned_data)
        if not utils.y_n_to_bool(row[self.final_key]):
            # NEW GROUPS TAKEN FROM INITIAL
            out_cnt = utils.enter_cnt(cleaned_data, 0, hu_contx.pk, cnt_code="Eggs Removed")[0]
            utils.enter_cnt_det(cleaned_data, out_cnt, row[self.cnt_key], "Program Group Split", row[self.prog_key])

            indv, final_grp = cont.fish_in_cont(row_date)
            if not final_grp:
                final_grp = models.Group(spec_id=grp_id.spec_id,
                                         coll_id=grp_id.coll_id,
                                         grp_year=grp_id.grp_year,
                                         stok_id=grp_id.stok_id,
                                         grp_valid=True,
                                         created_by=cleaned_data["created_by"],
                                         created_date=cleaned_data["created_date"],
                                         )
                try:
                    final_grp.clean()
                    final_grp.save()
                except (ValidationError, IntegrityError):
                    return None
            else:
                # MAIN GROUP GETTING MOVED
                final_grp = final_grp[0]
            final_grp_anix = utils.enter_anix(cleaned_data, grp_pk=final_grp.pk, return_anix=True)
            self.row_entered += utils.enter_anix(hu_cleaned_data, grp_pk=final_grp.pk, return_sucess=True)
            self.row_entered += utils.enter_bulk_grpd(final_grp_anix, cleaned_data, row_date,
                                                      prnt_grp=grp_id,
                                                      prog_grp=row.get(self.prog_key),
                                                      comments=row.get(self.comment_key)
                                                      )
            self.row_entered += utils.enter_grpd(final_grp_anix.pk, cleaned_data, row_date, dev_at_hu_transfer, None,
                                                 anidc_str="Development")

            # create movement for the new group, create 2 contx's and 3 anix's
            # cup contx is contx used to link the positive counts
            cont_contx = utils.create_egg_movement_evnt(tray_id, cont, cleaned_data, row_date, final_grp.pk,
                                                        return_cup_contx=True)

            move_cleaned_data = cleaned_data.copy()
            move_cleaned_data["evnt_id"] = cont_contx.evnt_id
            cnt_contx = cont_contx
            cnt_contx.pk = None
            cnt_contx.tray_id = tray_id
            try:
                cnt_contx.save()
            except IntegrityError:
                cnt_contx = models.ContainerXRef.objects.filter(pk=cont_contx.pk).get()
            self.row_entered += utils.enter_anix(move_cleaned_data, grp_pk=final_grp.pk, contx_pk=cnt_contx.pk, return_sucess=True)
            # add the positive counts
            cnt = utils.enter_cnt(move_cleaned_data, row[self.cnt_key], cnt_contx.pk, cnt_code="Eggs Added", )[0]
            if utils.nan_to_none(self.weight_key):
                utils.enter_cnt_det(move_cleaned_data, cnt, row[self.weight_key], "Weight")
            utils.enter_cnt_det(move_cleaned_data, cnt, row[self.cnt_key], "Program Group Split", row[self.prog_key])
        else:
            # Move main group to drawer, and add end date to tray:
            if cont:
                end_contx = utils.create_movement_evnt(tray_id, cont, cleaned_data, row_date,
                                                       grp_pk=grp_id.pk, return_end_contx=True)
                tray_id.end_date = row_date
                tray_id.save()
                end_cnt = utils.enter_cnt(cleaned_data, row[self.cnt_key], end_contx.pk,
                                          cnt_code="Egg Count")[0]
                utils.enter_cnt_det(cleaned_data, end_cnt, row[self.weight_key], "Weight")
            else:
                self.log_data += "\n Draw {} from {} not found".format(cont, row[self.cont_key])

            # link cup to egg development event
            utils.enter_contx(cont, cleaned_data, None)
