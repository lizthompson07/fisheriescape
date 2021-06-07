import copy
import math
from datetime import datetime, timedelta

import pytz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd
import numpy as np
from django.db.models import Q

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static.calculation_constants import yes_values
from bio_diversity.utils import DataParser


# ED = egg development
class EDInitParser(DataParser):
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    fecu_key = "Fecundity"
    crew_key = "Crew"
    comment_key = "Comments"

    header = 2
    sheet_name = "Init"
    converters = {trof_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}

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


# ED = egg development
class EDPickParser(DataParser):
    # used to create record picks taken from groups
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    pick_key = "Pick Count"
    pickc_key = "Pick Type"
    crew_key = "Crew"
    comment_key = "Comments"

    header = 2
    sheet_name = "Picking"
    converters = {trof_key: str, cross_key: str, 'Year': str, 'Month': str, 'Day': str}

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
        row_date = utils.get_row_date(row)
        self.row_entered += utils.enter_contx(row["trof_id"], cleaned_data)
        pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                indv_id__stok_id=row["stok_id"]).get()

        anix_id = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id').get()
        grp_id = anix_id.grp_id
        tray_id = models.Tray.objects.filter(trof_id=row["trof_id"], end_date__isnull=True, name=row[self.cross_key]).get()
        perc_list, inits_not_found = utils.team_list_splitter(row[self.crew_key])

        self.row_entered += utils.create_picks_evnt(cleaned_data, tray_id, grp_id.pk, row[self.pick_key], row_date,
                                                    row[self.pickc_key], perc_list[0])
        for inits in inits_not_found:
            self.log_data += "No valid personnel with initials ({}) on row: \n{}\n".format(inits, row)


# ED = egg development
# HU = Heath Unit
class EDHUParser(DataParser):
    # used to create record movements into heath units
    stock_key = "Stock"
    trof_key = "Trough"
    cross_key = "Cross"
    prog_key = "Program"
    cnt_key = "Count"
    weight_key = "Weight (g)"
    cont_key = "Destination"
    loss_key = "Transfer Loss"
    final_key = "Final (Y/N)"
    crew_key = "Crew"
    comment_key = "Comments"

    header = 2
    sheet_name = "HU Transfer"
    converters = {trof_key: str, cross_key: str, cont_key:str, 'Year': str, 'Month': str, 'Day': str}

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

        tray_qs = models.Tray.objects.filter(trof_id=row["trof_id"], name=row[self.cross_key])
        tray_id = tray_qs.filter(Q(start_date__lte=row_date, end_date__gte=row_date) | Q(end_date__isnull=True)).get()
        pair_id = models.Pairing.objects.filter(cross=row[self.cross_key], end_date__isnull=True,
                                                indv_id__stok_id=row["stok_id"]).get()

        anix_id = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id').get()
        grp_id = anix_id.grp_id
        # want to shift the hu move event, so that the counting math always works out.
        hu_move_date = row_date + timedelta(minutes=1)
        hu_cleaned_data = utils.create_new_evnt(cleaned_data, "Heath Unit Transfer", hu_move_date)
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
        cont = utils.get_cont_from_dot(row[self.cont_key], cleaned_data, row_date)
        self.row_entered += utils.enter_contx(cont, cleaned_data)
        if not utils.nan_to_none(row[self.final_key]) in yes_values:
            # NEW GROUPS TAKEN FROM INITIAL
            out_cnt = utils.enter_cnt(cleaned_data, 0, hu_contx.pk, cnt_code="Eggs Removed")[0]
            utils.enter_cnt_det(cleaned_data, out_cnt, row[self.cnt_key], "Program Group", row[self.prog_key])

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
            self.row_entered += utils.enter_grpd(final_grp_anix.pk, cleaned_data, row_date, grp_id.__str__(), None,
                                                 anidc_str="Parent Group", frm_grp_id=grp_id)
            self.row_entered += utils.enter_grpd(final_grp_anix.pk, cleaned_data, row_date, None, None,
                                                 anidc_str="Program Group", adsc_str=row[self.prog_key])
            self.row_entered += utils.enter_grpd(final_grp_anix.pk, cleaned_data, row_date, dev_at_hu_transfer, None,
                                                 anidc_str="Development")

            # create movement for the new group, create 2 contx's and 3 anix's
            # cup contx is contx used tyo link the positive counts
            cup_contx = utils.create_egg_movement_evnt(tray_id, cont, cleaned_data, row_date, final_grp.pk,
                                                       return_cup_contx=True)

            move_cleaned_data = cleaned_data.copy()
            move_cleaned_data["evnt_id"] = cup_contx.evnt_id
            cnt_contx = cup_contx
            cnt_contx.pk = None
            cnt_contx.tray_id = tray_id
            try:
                cnt_contx.save()
            except IntegrityError:
                cnt_contx = models.ContainerXRef.objects.filter(pk=cup_contx.pk).get()
            self.data_entered += utils.enter_anix(move_cleaned_data, grp_pk=final_grp.pk, contx_pk=cnt_contx.pk)
            # add the positive counts
            cnt = utils.enter_cnt(move_cleaned_data, row[self.cnt_key], cnt_contx.pk, cnt_code="Eggs Added", )[0]
            if utils.nan_to_none(self.weight_key):
                utils.enter_cnt_det(move_cleaned_data, cnt, row[self.weight_key], "Weight")
            utils.enter_cnt_det(move_cleaned_data, cnt, row[self.cnt_key], "Program Group", row[self.prog_key])
        else:
            # Move main group to drawer, and add end date to tray:
            draw = utils.get_draw_from_dot(str(row[self.cont_key]), cleaned_data)
            if draw:
                end_contx = utils.create_movement_evnt(tray_id, draw, cleaned_data, row_date,
                                                       grp_pk=grp_id.pk, return_end_contx=True)
                tray_id.end_date = row_date
                tray_id.save()
                end_cnt = utils.enter_cnt(cleaned_data, row[self.cnt_key], end_contx.pk,
                                          cnt_code="Egg Count")[0]
                utils.enter_cnt_det(cleaned_data, end_cnt, row[self.weight_key], "Weight")
            else:
                self.log_data += "\n Draw {} from {} not found".format(draw, row[self.cont_key])

            # link cup to egg development event
            utils.enter_contx(cont, cleaned_data, None)

        perc_list, inits_not_found = utils.team_list_splitter(row[self.crew_key])

        for inits in inits_not_found:
            self.log_data += "No valid personnel with initials ({}) on row: \n{}\n".format(inits, row)


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
                                    pick_code, cleaned_data["evnt_id"].perc_id)

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
