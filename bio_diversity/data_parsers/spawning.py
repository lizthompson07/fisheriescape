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
    choice_key = "Choice"
    egg_est_key = "Exp. #"
    status_key_f = "Status, F"
    status_key_m = "Status, M"
    dest_key_f = "End Tank, F"
    dest_key_m = "End Tank, M"

    header = 2
    start_grp_dict = {}
    end_grp_dict = {}
    converters = {pit_key_f: str, pit_key_m: str, dest_key_m: str, dest_key_f:str, 'Year': str, 'Month': str, 'Day': str}

    fecu_spwndc_id = None
    dud_spwndc_id = None

    sex_dict = calculation_constants.sex_dict

    def load_data(self):
        self.mandatory_keys.extend([self.pit_key_f, self.pit_key_m, self.prio_key_f, self.prio_key_m, self.cross_key,
                                    self.prio_key_pair, self.choice_key, self.egg_est_key])
        super(SpawningParser, self).load_data()

    def data_preper(self):
        self.fecu_spwndc_id = models.SpawnDetCode.objects.filter(name="Fecundity").get()
        self.dud_spwndc_id = models.SpawnDetCode.objects.filter(name="Dud").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        indv_qs = models.Individual.objects.filter(pit_tag=row[self.pit_key_f])
        indv_qs_male = models.Individual.objects.filter(pit_tag=row[self.pit_key_m])
        if len(indv_qs) == 1 and len(indv_qs_male) == 1:
            indv_female = indv_qs.get()
            indv_male = indv_qs_male.get()
        else:
            self.log_data += "Error parsing row: \n"
            self.log_data += str(row)
            self.log_data += "\nFish with PIT {} or PIT {} not found in db\n".format(row[self.pit_key_f],
                                                                                     row[self.pit_key_m])
            return self.log_data, False

        if not utils.nan_to_none(row[self.choice_key]):
            raise Exception("Choice column cannot be empty. Set Fecundity column to zero to indicate Duds.")

        row_date = utils.get_row_date(row)
        anix_female, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv_female.pk)
        self.row_entered += anix_entered
        anix_male, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv_male.pk)
        self.row_entered += anix_entered

        self.row_entered += utils.enter_bulk_indvd(anix_female.pk, cleaned_data, row_date,
                                                   gender="F",
                                                   len_mm=row.get(self.len_key_f_mm),
                                                   len_val=row.get(self.len_key_f),
                                                   weight=row.get(self.weight_key_f),
                                                   weight_kg=row.get(self.weight_key_f_kg),
                                                   status=row.get(self.status_key_f),
                                                   comments=row.get(self.comment_key_f)
                                                   )

        self.row_entered += utils.enter_bulk_indvd(anix_male.pk, cleaned_data, row_date,
                                                   gender="M",
                                                   len_mm=row.get(self.len_key_m_mm),
                                                   len_val=row.get(self.len_key_m),
                                                   weight=row.get(self.weight_key_m),
                                                   weight_kg=row.get(self.weight_key_m_kg),
                                                   status=row.get(self.status_key_m),
                                                   comments=row.get(self.comment_key_m)
                                                   )

        if utils.nan_to_none(row.get(self.dest_key_f)):
            end_tank_id_f = models.Tank.objects.filter(name=row[self.dest_key_f], facic_id=cleaned_data["facic_id"]).get()
            self.row_entered += utils.create_movement_evnt(None, end_tank_id_f, cleaned_data, row_date, indv_female.pk)

        if utils.nan_to_none(row.get(self.dest_key_m)):
            end_tank_id_m = models.Tank.objects.filter(name=row[self.dest_key_m], facic_id=cleaned_data["facic_id"]).get()
            self.row_entered += utils.create_movement_evnt(None, end_tank_id_m, cleaned_data, row_date, indv_male.pk)

        # pair

        pair = models.Pairing(start_date=row_date,
                              prio_id=models.PriorityCode.objects.filter(
                                  name__iexact=prio_dict[row[self.prio_key_f]]).get(),
                              pair_prio_id=models.PriorityCode.objects.filter(
                                  name__iexact=prio_dict[row[self.prio_key_pair]]).get(),
                              cross=row[self.cross_key],
                              valid=True,
                              indv_id=indv_female,
                              comments=utils.nan_to_none(row[self.comment_key_pair]),
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            pair.clean()
            pair.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            pair = models.Pairing.objects.filter(start_date=row_date, indv_id=indv_female).get()

        # sire
        sire = models.Sire(prio_id=models.PriorityCode.objects.filter(name__iexact=prio_dict[row[self.prio_key_m]]).get(),
                           pair_id=pair,
                           indv_id=indv_male,
                           choice=[self.choice_key],
                           comments=utils.nan_to_none(row[self.comment_key_m]),
                           created_by=cleaned_data["created_by"],
                           created_date=cleaned_data["created_date"],
                           )
        try:
            sire.clean()
            sire.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            pass

        self.row_entered += utils.enter_anix(cleaned_data, pair_pk=pair.pk, return_sucess=True)

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
        if anix_grp_qs.count() == 0:

            grp = models.Group(spec_id=indv_female.spec_id,
                               stok_id=indv_female.stok_id,
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
                row_entered += utils.enter_anix(cleaned_data, grp_pk=grp.pk, return_sucess=True)
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

    def data_cleaner(self):
        # evntf
        cleaned_data = self.cleaned_data
        indv_qs = models.Individual.objects.filter(pit_tag=self.data[self.pit_key_f][0])
        if len(indv_qs) == 1:
            indv_female = indv_qs.get()
            evntf = models.EventFile(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     stok_id=indv_female.stok_id,
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
