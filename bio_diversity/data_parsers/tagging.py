from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd
from django.db.models.functions import Length

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class TaggingParser(DataParser):
    to_tank_key = "To Tank"
    to_tank_id_key = "to_tank_id"
    from_tank_id_key = "from_tank_id"
    from_tank_key = "From Tank"
    group_key = "Group"
    mark_key = "Mark"
    coll_key = "Collection"
    stok_key = "Stock"
    ufid_key = "Universal Fish ID"
    pit_key = "PIT Tag #"
    comment_key = "Comments"
    lifestage_key = "Lifestage"
    len_key = "Length (cm)"
    len_key_mm = "Length (mm)"
    weight_key = "Weight (g)"
    weight_key_kg = "Weight (kg)"
    vial_key = "Vial"
    crew_key = "Tagger"
    precocity_key = "Precocity (Y/N)"

    header = 0
    converters = {to_tank_key: str, from_tank_key: str, pit_key: str, 'Year': str, 'Month': str, 'Day': str}
    start_grp_dict = {}
    end_grp_dict = {}

    tagger_code = None
    salmon_id = None
    stok_id = None
    coll_id = None
    grp_id = None
    anix_indv = None

    ani_health_anidc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.to_tank_key, self.from_tank_key, self.group_key, self.pit_key, self.stok_key, self.coll_key])
        self.mandatory_filled_keys.extend([self.to_tank_key, self.from_tank_key, self.pit_key, self.stok_key, self.coll_key])
        super(TaggingParser, self).load_data()

    def data_preper(self):
        if len(self.data[self.group_key].unique()) > 1 or len(self.data[self.stok_key].unique()) > 1 or \
                len(self.data[self.coll_key].unique() or len(self.data[self.mark_key].unique())) > 1:
            self.log_data += "\n WARNING: Form only designed for use with single group. Check \"Group\" column and" \
                             " split sheet if needed. \n"

        self.tagger_code = models.RoleCode.objects.filter(name__iexact="Tagger").get()
        self.salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()

        # set datetimes:
        self.data = utils.set_row_datetime(self.data)

        # set tanks:
        self.data = utils.set_row_tank(self.data, self.cleaned_data, self.from_tank_key, col_name=self.from_tank_id_key)
        self.data = utils.set_row_tank(self.data, self.cleaned_data, self.to_tank_key, col_name=self.to_tank_id_key)

        # set column groups, should only be one of these
        self.data = utils.set_row_grp(self.data, self.stok_key, self.coll_key, self.group_key, self.from_tank_id_key, "datetime", self.mark_key)
        self.grp_id = self.data["grp_id"][0]

        year, coll = utils.year_coll_splitter(self.data[self.coll_key][0])
        self.stok_id = models.StockCode.objects.filter(name=self.data[self.stok_key][0]).get()
        self.coll_id = utils.coll_getter(coll)
        self.data_dict = self.data.to_dict("records")

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        year, coll = utils.year_coll_splitter(row[self.coll_key])
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()
        indv_ufid = utils.nan_to_none(row.get(self.ufid_key))
        indv = models.Individual(grp_id=self.grp_id,
                                 spec_id=self.salmon_id,
                                 stok_id=self.stok_id,
                                 coll_id=self.coll_id,
                                 indv_year=year,
                                 pit_tag=row[self.pit_key],
                                 ufid=indv_ufid,
                                 indv_valid=True,
                                 comments=utils.nan_to_none(row.get(self.comment_key)),
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
        try:
            indv.clean()
            indv.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            indv = models.Individual.objects.filter(pit_tag=indv.pit_tag).get()

        if utils.nan_to_none(row[self.from_tank_id_key]) or utils.nan_to_none(row[self.to_tank_id_key]):
            in_tank = row[self.from_tank_id_key]
            out_tank = row[self.to_tank_id_key]
            self.row_entered += utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                                           indv_pk=indv.pk)
            # if tagged fish goes back into same tank, still link fish to tank:
            if in_tank == out_tank:
                utils.enter_contx(in_tank, cleaned_data, True, indv_pk=indv.pk)

        anix_indv, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv.pk)
        self.row_entered += anix_entered
        self.anix_indv = anix_indv

        utils.enter_bulk_indvd(anix_indv.pk, self.cleaned_data, row_date,
                               len_mm=row.get(self.len_key_mm),
                               len_val=row.get(self.len_key),
                               weight=row.get(self.weight_key),
                               weight_kg=row.get(self.weight_key_kg),
                               vial=row.get(self.vial_key),
                               mark=row.get(self.mark_key),
                               prog_grp=row.get(self.group_key),
                               lifestage=row.get(self.lifestage_key),
                               comments=row.get(self.comment_key),
                               )

        if utils.nan_to_none(row.get(self.precocity_key)):
            self.row_entered += utils.enter_indvd(anix_indv.pk, cleaned_data, row_date, None,
                                                  self.ani_health_anidc_id.pk, "Precocity")

        if utils.nan_to_none(row.get(self.crew_key)):
            perc_list, inits_not_found = utils.team_list_splitter(row[self.crew_key])
            for perc_id in perc_list:
                team_id, team_entered = utils.add_team_member(perc_id, cleaned_data["evnt_id"],
                                                              role_id=self.tagger_code, return_team=True)
                self.row_entered += team_entered
                if team_id:
                    self.row_entered += utils.enter_anix(cleaned_data, indv_pk=indv.pk, team_pk=team_id.pk,
                                                         return_sucess=True)
            for inits in inits_not_found:
                self.log_data += "No valid personnel with initials ({}) for row with pit tag" \
                                 " {}\n".format(inits, row[self.pit_key])

    def data_cleaner(self):
        from_tanks = self.data[self.from_tank_key].value_counts()
        for tank_name in from_tanks.keys():
            fish_tagged_from_tank = int(from_tanks[tank_name])
            contx, data_entered = utils.enter_tank_contx(tank_name, self.cleaned_data, None, grp_pk=self.grp_id.pk,
                                                         return_contx=True)
            if contx:
                utils.enter_cnt(self.cleaned_data, fish_tagged_from_tank, contx.pk, cnt_code="Pit Tagged")


class MactaquacTaggingParser(TaggingParser):
    sex_dict = calculation_constants.sex_dict
    to_tank_key = "Destination Pond"
    from_tank_key = "Origin Pond"
    coll_key = "Collection"
    pit_key = "PIT"
    ufid_key = "UFID"
    sex_key = "Sex"
    tissue_key = "Tissue Sample"
    vial_key = "Vial Number"
    crew_key = "Crew"

    header = 2
    converters = {to_tank_key: str, from_tank_key: str, pit_key: str, 'Year': str, 'Month': str, 'Day': str}
    sex_anidc_id = None

    def data_preper(self):
        super(MactaquacTaggingParser, self).data_preper()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()

    def row_parser(self, row):
        super().row_parser(row)
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()
        utils.enter_bulk_indvd(self.anix_indv.pk, self.cleaned_data, row_date,
                               gender=row.get(self.sex_key),
                               tissue_yn=row.get(self.tissue_key),
                               )


class ColdbrookTaggingParser(TaggingParser):
    box_key = "Box"
    location_key = "Location"
    precocity_key = "pp"
    indt_key = "Treatment"
    indt_amt_key = "Amount"

    box_anidc_id = None
    boxl_anidc_id = None

    def data_preper(self):
        super(ColdbrookTaggingParser, self).data_preper()
        self.box_anidc_id = models.AnimalDetCode.objects.filter(name="Box").get()
        self.boxl_anidc_id = models.AnimalDetCode.objects.filter(name="Box Location").get()

    def row_parser(self, row):
        super().row_parser(row)
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()
        if utils.nan_to_none(row.get(self.box_key)):
            self.row_entered += utils.enter_indvd(self.anix_indv.pk, self.cleaned_data, row_date, row[self.box_key],
                                                  self.box_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.location_key)):
            self.row_entered += utils.enter_indvd(self.anix_indv.pk, self.cleaned_data, row_date,
                                                  row[self.location_key], self.boxl_anidc_id.pk, None)

        if utils.nan_to_none(row.get(self.indt_key)) and utils.nan_to_none(row.get(self.indt_amt_key)):
            indvtc_id = models.IndTreatCode.objects.filter(name__icontains=row[self.indt_key]).get()
            unit_id = models.UnitCode.objects.filter(name__icontains="gram").order_by(Length('name').asc()).first()
            self.row_entered += utils.enter_indvt(self.anix_indv.pk, self.cleaned_data, row_datetime,
                                                  row[self.indt_amt_key], indvtc_id.pk, unit_id=unit_id)
