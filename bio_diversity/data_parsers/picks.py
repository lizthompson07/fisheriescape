import math
from datetime import datetime, timedelta

import pytz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd
import numpy as np

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


# ED = egg development
class EDInitParser(DataParser):
    # used to create F1 groups, place them in trays and associate a count with them
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    fecu_key = "Fecundity"
    crew_key = "Crew"
    comment_key = "Comments"

    header = 2
    sheet_name = "Init"
    converters = {trof_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}

    prnt_grp_anidc_id = None
    prog_grp_anidc_id = None

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.prnt_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Parent Group").get()
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()

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
                                                indv_id__stok_id=row["stok_id"]).get()

        anix_id = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id').get()
        grp_id = anix_id.grp_id
        self.row_entered += utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, return_sucess=True)

        tray_id = utils.create_tray(row["trof_id"], row[self.cross_key], row_date, cleaned_data)
        contx, contx_entered = utils.enter_contx(tray_id, cleaned_data, True, grp_pk=grp_id.pk, return_contx=True)
        self.row_entered += contx_entered

        cnt, cnt_entered = utils.enter_cnt(cleaned_data, row[self.fecu_key], contx_pk=contx.pk, cnt_code="Photo Count")
        self.row_entered += cnt_entered

        self.team_parser(row[self.crew_key], row)

        if utils.nan_to_none(row[self.comment_key]):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix_id, row_date)
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row with stock ({}), cross ({}): \n {}" \
                                 " \n\n".format(row[self.stock_key], row[self.cross_key], row[self.comment_key])


def mactaquac_picks_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', sheet_name="LOSS", header=None).dropna(
            how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    trof_dfs = np.split(data, data.index[data[0] == "Trough Number"])

    for trof_df in trof_dfs[1:]:
        trof_df = trof_df.rename(columns=trof_df.iloc[0]).reset_index(drop=True)
        trof_df = trof_df.drop(0).drop(trof_df.index[trof_df["Tray Number"] == "Totals"]).reset_index(drop=True)

        trof = models.Trough.objects.filter(name=trof_df["Trough Number"][1], facic_id=cleaned_data["facic_id"]).get()
        utils.enter_trof_contx(trof.name, cleaned_data)
        pick_dates_df = trof_df.iloc[[0]].dropna(axis=1).drop(trof_df.iloc[[0]].iloc[:, 0:1], axis=1)
        pick_date = datetime.now().date()
        for row in trof_df.to_dict("records")[1:]:
            tray = models.Tray.objects.filter(trof_id=trof, name=row["Tray Number"], end_date__isnull=True).get()
            cross_grp = models.Group.objects.filter(animal_details__contx_id__tray_id=tray).get()
            contx, data_entered = utils.enter_contx(tray, cleaned_data, grp_pk=cross_grp.pk, return_contx=True)
            utils.create_picks_evnt(cleaned_data, tray, cross_grp.pk, row["Picks"], pick_date, "Egg Picks")

    log_data += "\n\n\n {} of {} rows entered to " \
                "database".format(rows_entered, len(data_dict))
    return log_data, True


class ColdbrookPickParser(DataParser):
    stock_key = "Stock"
    cross_key = "cross"
    trof_key = "Trough"
    fecu_photo_key = "Fecundity Counts from Photos"
    shock_date_key = "Shocking Pick Date"
    hu_date_key = "Date Transferred to HU"
    hu_cnt_key = "HU transfer TOTAL"
    gen_tray_key = "General Location stack.tray"
    gen_cnt_key = "# of Generals"
    gen_weight_key = "Actual Wt of Generals"

    # format is: date_key, pick_key, pick_code
    pick_tuples = [
        ("Spawning Picks Date", "Morts 1st pick (day after spawning)", "Spawning Loss"),
        ("Cleaning Pick Date", "Morts after cleaning", "Cleaning Loss"),
        ("Shocking Pick Date", "Morts after shocking", "Shock Loss"),
    ]

    hu_pick_tuples = [("Morts", None),
                      ("Weak-Eyed", "Weak-Eyed"),
                      ("Pre-Hatch", "Pre-Hatch")]

    # list of movement column headers: count, cup, weight, and code
    move_tuples = [
        ("EQU A #", "EQU A Location", "Weight 1 (g)", "EQU A"),
        ("EQU B #", "EQU B Location", "Weight 2 (g)", "EQU B"),
        ("# of PEQUs", "PEQU Location stack.tray", "Actual PEQU Wt (g)", "PEQU"),
        ("AB Pools", "A Pool", None, "A Pool"),
        ("AB Pools", "B Pool", None, "B Pool"),
    ]

    header = 1
    sheet_name = "Matings and Losses"
    converters = {trof_key: str, cross_key: str}

    prnt_grp_anidc_id = None
    prog_grp_anidc_id = None

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.prnt_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Parent Group").get()
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()

        # add objects rows to dataframe:
        pair_qs = models.Pairing.objects.all().select_related('indv_id__stok_id')
        len(pair_qs)  # force lazy qs to evaluate
        self.data["pairs"] = self.data.apply(
            lambda row: pair_qs.filter(cross=row[self.cross_key], indv_id__stok_id__name=row[self.stock_key]).get(),
            axis=1)

        anix_qs = models.AniDetailXref.objects.filter(pair_id__in=self.data["pairs"],
                                                      grp_id__isnull=False).select_related('grp_id')
        self.data["grps"] = self.data.apply(lambda row: anix_qs.filter(pair_id=row["pairs"]).get().grp_id, axis=1)

        trof_qs = models.Trough.objects.filter(facic_id=cleaned_data["facic_id"])
        len(trof_qs)
        trof_dict = {trof.name: trof for trof in trof_qs}
        self.data["trofs"] = self.data.apply(lambda row: trof_dict[row[self.trof_key]], axis=1)

        # trays, date from cross
        self.data["trays"] = self.data.apply(lambda row: utils.create_tray(row["trofs"], row[self.cross_key],
                                                                           row["pairs"].start_date, cleaned_data,
                                                                           save=True), axis=1)

        self.data_dict = self.data.to_dict('records')

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        # move fish into their trays following spawning event.
        contx, data_entered = utils.enter_contx(row["trays"], cleaned_data, final_flag=True, grp_pk=row["grps"].pk,
                                                return_contx=True)
        self.row_entered += data_entered
        utils.enter_contx(row["trofs"], cleaned_data)
        anix = utils.enter_anix(cleaned_data, grp_pk=row["grps"].pk, return_anix=True)

        # convert fecundity from spawning to count on tray:
        spwn_qs = models.SpawnDet.objects.filter(pair_id=row["pairs"], spwndc_id__name="Fecundity")
        if spwn_qs.exists():
            fecu_est = int(spwn_qs.get().det_val)
            utils.enter_cnt(cleaned_data, fecu_est, contx.pk, cnt_code="Fecundity Estimate", est=True)
        utils.enter_cnt(cleaned_data, row[self.fecu_photo_key], contx.pk, cnt_code="Photo Count")

        # Picks
        for date_key, pick_key, pick_code in self.pick_tuples:
            pick_datetime = datetime.strptime(row[date_key], "%Y-%b-%d").replace(tzinfo=pytz.UTC)
            utils.create_picks_evnt(cleaned_data, row["trays"], row["grps"].pk, row[pick_key], pick_datetime,
                                    pick_code)

        # Shocking:
        shock_date = datetime.strptime(row[self.shock_date_key], "%Y-%b-%d").replace(tzinfo=pytz.UTC)
        shocking_cleaned_data = utils.create_new_evnt(cleaned_data, "Shocking", shock_date)
        utils.enter_contx(row["trays"], shocking_cleaned_data, None, grp_pk=row["grps"].pk)
        shock_anix = utils.enter_anix(shocking_cleaned_data, grp_pk=row["grps"].pk, return_anix=True)
        dev_at_shocking = row["grps"].get_development(shock_date)
        utils.enter_grpd(shock_anix.pk, shocking_cleaned_data, shock_date, dev_at_shocking, None,
                         anidc_str="Development")

        # HU Transfer:
        move_date = datetime.strptime(row[self.hu_date_key], "%Y-%b-%d").replace(tzinfo=pytz.UTC)
        # want to shift the hu move event, so that the counting math always works out.
        hu_move_date = move_date + timedelta(minutes=1)
        hu_cleaned_data = utils.create_new_evnt(cleaned_data, "Heath Unit Transfer", hu_move_date)
        hu_anix = utils.enter_anix(hu_cleaned_data, grp_pk=row["grps"].pk, return_anix=True)
        hu_contx, data_entered = utils.enter_contx(row["trays"], hu_cleaned_data, None, grp_pk=row["grps"].pk,
                                                   return_contx=True)
        dev_at_hu_transfer = row["grps"].get_development(hu_move_date)
        utils.enter_grpd(hu_anix.pk, hu_cleaned_data, hu_move_date, dev_at_hu_transfer, None,
                         anidc_str="Development")

        # HU Picks:
        hu_pick_cnt = utils.enter_cnt(cleaned_data, row[self.hu_cnt_key], hu_contx.pk,
                                      cnt_code="HU Transfer Loss")[0]

        for pick_cnt, pick_code in self.hu_pick_tuples:
            utils.enter_cnt_det(hu_cleaned_data, hu_pick_cnt, row[pick_cnt], "Mortality Observation", pick_code)

        # track eggs moving out:
        all_eggs_out = 0
        out_cnt = utils.enter_cnt(cleaned_data, 0, hu_contx.pk, cnt_code="Eggs Removed")[0]
        for move_cnt, move_cup, move_weight, cnt_code in self.move_tuples:
            if not math.isnan(row[move_cnt]):
                utils.enter_cnt_det(cleaned_data, out_cnt, row[move_cnt], "Program Group", cnt_code)
                all_eggs_out += row[move_cnt]
        if all_eggs_out:
            out_cnt.det_val = int(all_eggs_out)
            out_cnt.save()

        # generate new group, cup, and movement evnt:
        for move_cnt, move_cup, move_weight, cnt_code in self.move_tuples:
            cont = utils.get_cont_from_dot(row[move_cup], cleaned_data, move_date)
            indv, final_grp = cont.fish_in_cont(move_date)
            if not final_grp:
                final_grp = models.Group(spec_id=row["grps"].spec_id,
                                         coll_id=row["grps"].coll_id,
                                         grp_year=row["grps"].grp_year,
                                         stok_id=row["grps"].stok_id,
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
                final_grp = final_grp[0]
            final_grp_anix = utils.enter_anix(cleaned_data, grp_pk=final_grp.pk, return_anix=True)
            utils.enter_grpd(final_grp_anix.pk, cleaned_data, move_date, row["grps"].__str__(), None,
                             anidc_str="Parent Group", frm_grp_id=row["grps"])
            utils.enter_grpd(final_grp_anix.pk, cleaned_data, move_date, None, None, anidc_str="Program Group",
                             adsc_str=cnt_code)
            utils.enter_grpd(final_grp_anix.pk, cleaned_data, move_date, dev_at_hu_transfer, None,
                             anidc_str="Development")

            # create movement for the new group, create 2 contx's and 3 anix's
            # tray contx is contx used tyo link the positive counts
            cup_contx = utils.create_egg_movement_evnt(row["trays"], cont, cleaned_data, move_date, final_grp.pk,
                                                       return_cup_contx=True)

            # add the positive counts
            cnt = utils.enter_cnt(cleaned_data, row[move_cnt], cup_contx.pk, cnt_code="Eggs Added", )[0]
            if utils.nan_to_none(move_weight):
                utils.enter_cnt_det(cleaned_data, cnt, row[move_weight], "Weight")
            utils.enter_cnt_det(cleaned_data, cnt, row[move_cnt], "Program Group", cnt_code)

            # link cup to egg development event
            utils.enter_contx(cont, cleaned_data, None)

            # Move main group to drawer, and add end date to tray:
            draw = utils.get_draw_from_dot(str(row[self.gen_tray_key]), cleaned_data)
            if draw:
                end_contx = utils.create_movement_evnt(row["trays"], draw, cleaned_data, move_date,
                                                       grp_pk=row["grps"].pk, return_end_contx=True)
                end_cnt = utils.enter_cnt(cleaned_data, row[self.gen_cnt_key], end_contx.pk,
                                          cnt_code="Egg Count")[0]
                utils.enter_cnt_det(cleaned_data, end_cnt, row[self.gen_weight_key], "Weight")
            else:
                self.log_data += "\n Draw {} from {} not found".format(draw, row[self.gen_tray_key])

            tray = row["trays"]
            tray.end_date = move_date
            tray.save()
