import os
from django.core.exceptions import ValidationError
from django.db import IntegrityError


from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.static.calculation_constants import prio_dict
from bio_diversity.utils import DataParser


class SpawningParser(DataParser):
    pit_key_f = "PIT, F"
    pit_key_m = "PIT, M"
    samp_key_f = "Sample UFID, F"
    samp_key_m = "Sample UFID, M"
    prio_key_f = "Pri. F"
    prio_key_m = "Pri. M"
    prio_key_pair = "Pri."
    cross_key = "Tray #"
    comment_key_f = "Comments, F"
    comment_key_m = "Comments, M"
    comment_key_pair = "Comments"
    len_key_f = "Ln (cm), F"
    len_key_f_mm = "Ln (mm), F"
    weight_key_f = "Wt (g), F"
    weight_key_f_kg = "Wt (kg), F"
    len_key_m = "Ln (cm), M"
    len_key_m_mm = "Ln (mm), M"
    weight_key_m = "Wt (g), M"
    weight_key_m_kg = "Wt (kg), M"
    cryo_out_key = "Cryo Milt Taken"
    cryo_in_key = "Cryo Milt Used"
    fluid_out_key = "Ovarian Fluid Taken"
    fluid_in_key = "Ovarian Fluid Used"
    choice_key = "Choice"
    egg_est_key = "Exp. #"
    status_key_f = "Status, F"
    status_key_m = "Status, M"
    dest_key_f = "End Tank, F"
    dest_key_m = "End Tank, M"
    prog_key = "Program"

    header = 1
    comment_row = [2]
    start_grp_dict = {}
    end_grp_dict = {}
    converters = {pit_key_f: str, pit_key_m: str, dest_key_m: str, dest_key_f:str, 'Year': str, 'Month': str, 'Day': str}

    fecu_spwndc_id = None
    dud_spwndc_id = None
    prog_spwndc_id = None
    cryo_spwndc_id = None
    o_fluid_spwndc_id = None

    sex_dict = calculation_constants.sex_dict

    def load_data(self):
        self.mandatory_keys.extend([self.prio_key_f, self.prio_key_m, self.cross_key,
                                    self.prio_key_pair, self.choice_key, self.egg_est_key])
        super(SpawningParser, self).load_data()

    def data_preper(self):
        self.fecu_spwndc_id = models.SpawnDetCode.objects.filter(name="Fecundity").get()
        self.dud_spwndc_id = models.SpawnDetCode.objects.filter(name="Dud").get()
        self.prog_spwndc_id = models.SpawnDetCode.objects.filter(name="Program").get()
        self.cryo_spwndc_id = models.SpawnDetCode.objects.filter(name="Cryo Milt Used").get()
        self.o_fluid_spwndc_id = models.SpawnDetCode.objects.filter(name="Ovarian Fluid Used").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data

        indv_female, samp_female, new_log = utils.get_indv_or_samp(row, self.pit_key_f, self.samp_key_f,
                                                                   cleaned_data["evnt_id"])

        if new_log:
            self.log_data += new_log
            return self.log_data, False

        indv_male, samp_male, new_log = utils.get_indv_or_samp(row, self.pit_key_m, self.samp_key_m,
                                                               cleaned_data["evnt_id"])
        if new_log:
            self.log_data += new_log
            return self.log_data, False

        if not (indv_female or samp_female) or not (indv_male or samp_male):
            raise Exception("No Individual or Fish found for row {}".format(row))

        if not utils.nan_to_none(row[self.choice_key]):
            raise Exception("Choice column cannot be empty. Set Fecundity column to zero to indicate Duds.")

        row_date = utils.get_row_date(row)
        if indv_female:
            anix_female, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv_female.pk)
            self.row_entered += anix_entered
            self.row_entered += utils.enter_bulk_indvd(anix_female.pk, cleaned_data, row_date,
                                                       gender="F",
                                                       len_mm=row.get(self.len_key_f_mm),
                                                       len_val=row.get(self.len_key_f),
                                                       weight=row.get(self.weight_key_f),
                                                       weight_kg=row.get(self.weight_key_f_kg),
                                                       status=row.get(self.status_key_f),
                                                       o_fluid_out=row.get(self.fluid_out_key),
                                                       comments=row.get(self.comment_key_f)
                                                       )
        if indv_male:
            anix_male, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv_male.pk)
            self.row_entered += anix_entered

            self.row_entered += utils.enter_bulk_indvd(anix_male.pk, cleaned_data, row_date,
                                                       gender="M",
                                                       len_mm=row.get(self.len_key_m_mm),
                                                       len_val=row.get(self.len_key_m),
                                                       weight=row.get(self.weight_key_m),
                                                       weight_kg=row.get(self.weight_key_m_kg),
                                                       status=row.get(self.status_key_m),
                                                       cryo_out=row.get(self.cryo_out_key),
                                                       comments=row.get(self.comment_key_m)
                                                       )
        if samp_female:
            self.row_entered += utils.enter_bulk_sampd(samp_female.pk, cleaned_data, row_date,
                                                       gender="F",
                                                       len_mm=row.get(self.len_key_f_mm),
                                                       len_val=row.get(self.len_key_f),
                                                       weight=row.get(self.weight_key_f),
                                                       weight_kg=row.get(self.weight_key_f_kg),
                                                       status=row.get(self.status_key_f),
                                                       o_fluid_out=row.get(self.fluid_out_key),
                                                       comments=row.get(self.comment_key_f)
                                                       )
        if samp_male:
            self.row_entered += utils.enter_bulk_sampd(samp_male.pk, cleaned_data, row_date,
                                                       gender="M",
                                                       len_mm=row.get(self.len_key_m_mm),
                                                       len_val=row.get(self.len_key_m),
                                                       weight=row.get(self.weight_key_m),
                                                       weight_kg=row.get(self.weight_key_m_kg),
                                                       status=row.get(self.status_key_m),
                                                       cryo_out=row.get(self.cryo_out_key),
                                                       comments=row.get(self.comment_key_m)
                                                       )

        if utils.nan_to_none(row.get(self.dest_key_f)) and indv_female:
            end_tank_id_f = models.Tank.objects.filter(name=row[self.dest_key_f],
                                                       facic_id=cleaned_data["facic_id"]).get()
            self.row_entered += utils.enter_move(cleaned_data, None, end_tank_id_f, row_date, indv_pk=indv_female.pk,
                                                 return_sucess=True)

        if utils.nan_to_none(row.get(self.dest_key_m)) and indv_male:
            end_tank_id_m = models.Tank.objects.filter(name=row[self.dest_key_m],
                                                       facic_id=cleaned_data["facic_id"]).get()
            self.row_entered += utils.enter_move(cleaned_data, None, end_tank_id_m, row_date, indv_pk=indv_male.pk,
                                                 return_sucess=True)

        # pair
        pair = models.Pairing(start_date=row_date,
                              prio_id=models.PriorityCode.objects.filter(
                                  name__iexact=prio_dict[row[self.prio_key_f]]).get(),
                              pair_prio_id=models.PriorityCode.objects.filter(
                                  name__iexact=prio_dict[row[self.prio_key_pair]]).get(),
                              cross=row[self.cross_key],
                              valid=True,
                              indv_id=indv_female,
                              samp_id=samp_female,
                              comments=utils.nan_to_none(row[self.comment_key_pair]),
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            pair.clean()
            pair.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            pair = models.Pairing.objects.filter(start_date=row_date, indv_id=indv_female, samp_id=samp_female).get()

        # sire
        sire = models.Sire(prio_id=models.PriorityCode.objects.filter(name__iexact=prio_dict[row[self.prio_key_m]]).get(),
                           pair_id=pair,
                           indv_id=indv_male,
                           samp_id=samp_male,
                           choice=row[self.choice_key],
                           comments=utils.nan_to_none(row[self.comment_key_m]),
                           created_by=cleaned_data["created_by"],
                           created_date=cleaned_data["created_date"],
                           )
        try:
            sire.clean()
            sire.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            # don't use sire again anywhere
            pass

        self.row_entered += utils.enter_anix(cleaned_data, pair_pk=pair.pk, return_sucess=True)

        # pairing program:
        if utils.nan_to_none(row.get(self.prog_key)):
            self.row_entered += utils.enter_spwnd(pair.pk, cleaned_data, row[self.prog_key], self.prog_spwndc_id.pk,
                                                  spwnsc_str=row[self.prog_key])
        if utils.nan_to_none(row.get(self.cryo_in_key)):
            self.row_entered += utils.enter_spwnd(pair.pk, cleaned_data, None, self.cryo_spwndc_id.pk, None)
        if utils.nan_to_none(row.get(self.fluid_in_key)):
            self.row_entered += utils.enter_spwnd(pair.pk, cleaned_data, None, self.o_fluid_spwndc_id.pk, None)

        # fecu/dud/extra male
        if row[self.egg_est_key] > 0:
            self.row_entered += utils.enter_spwnd(pair.pk, cleaned_data, int(row[self.egg_est_key]),
                                                  self.fecu_spwndc_id.pk, None, "Calculated")
        else:
            self.row_entered += utils.enter_spwnd(pair.pk, cleaned_data, row[self.choice_key], self.dud_spwndc_id.pk,
                                                  None, "Good")

        # grp
        anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                          grp_id__isnull=False,
                                                          pair_id=pair,
                                                          indv_id__isnull=True,
                                                          contx_id__isnull=True,
                                                          loc_id__isnull=True,
                                                      )
        anix_grp = False
        if anix_grp_qs.count() == 0:
            if indv_female:
                stok_id = indv_female.stok_id
                spec_id = indv_female.spec_id
            else:
                stok_id = samp_female.stok_id
                spec_id = samp_female.spec_id

            grp = models.Group(spec_id=spec_id,
                               stok_id=stok_id,
                               coll_id=models.Collection.objects.filter(name="Egg (F1)").get(),
                               grp_year=row_date.year,
                               grp_valid=False,
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
            try:
                grp.clean()
                grp.save()
                row_entered = True
                anix_grp, anix_entered = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
                row_entered += utils.enter_anix(cleaned_data, grp_pk=grp.pk, pair_pk=pair.pk, return_sucess=True)
                grp.grp_valid = True
                grp.save()
                self.row_entered = True
            except ValidationError:
                # recovering the group is only doable through the anix with both grp and pair.
                # no way to find it here, so only make the group valid after anix's created.
                pass

        elif anix_grp_qs.count() == 1:
            anix_grp = anix_grp_qs.get()
            grp = anix_grp.grp_id

        if anix_grp and row.get(self.prog_key):
            utils.enter_bulk_grpd(anix_grp, cleaned_data, row_date, prog_grp=row[self.prog_key])

    def data_cleaner(self):
        # evntf
        cleaned_data = self.cleaned_data
        indv_female, samp_female, new_log = utils.get_indv_or_samp(self.data.iloc[0], self.pit_key_f, self.samp_key_f,
                                                                   cleaned_data["evnt_id"])
        stok_id = None
        if indv_female:
            stok_id = indv_female.stok_id
        elif samp_female:
            stok_id = samp_female.stok_id

        if stok_id:
            evntf = models.EventFile(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     stok_id=stok_id,
                                     evntfc_id=models.EventFileCode.objects.filter(name="Mating Plan").get(),
                                     evntf_xls=cleaned_data["data_csv"],
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
            try:
                evntf.clean()
                evntf.save()
            except (ValidationError, IntegrityError) as err:
                # delete mating plan if model did not save
                if type(err) == IntegrityError:
                    if os.path.isfile(evntf.evntf_xls.path):
                        os.remove(evntf.evntf_xls.path)


class MactaquacSpawningParser(SpawningParser):
    cross_key = "Cross"


class ColdbrookSpawningParser(SpawningParser):
    pass
