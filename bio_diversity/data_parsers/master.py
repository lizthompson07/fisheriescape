from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class MasterIndvParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    tank_key = "Tank"
    stok_key = "Stock"
    year_coll_key = "Collection"
    pit_key = "PIT Tag"
    ufid_key = "UFID"
    comment_key = "Comments"
    sex_key = "Sex"
    lifestage_key = "Lifestage"

    header = 2
    sheet_name = "Individual"
    converters = {tank_key: str, pit_key: str, 'Year': str, 'Month': str, 'Day': str}

    salmon_id = None
    sex_anidc_id = None
    ani_health_anidc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.pit_key, self.tank_key, self.stok_key, self.year_coll_key])
        super(MasterIndvParser, self).load_data()

    def data_preper(self):
        self.salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        year, coll = utils.year_coll_splitter(row[self.year_coll_key])
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()
        comments = utils.nan_to_none(row.get(self.comment_key))
        ufid = utils.nan_to_none(row.get(self.ufid_key))

        indv = models.Individual(grp_id_id=None,
                                 spec_id=self.salmon_id,
                                 stok_id=models.StockCode.objects.filter(name=row[self.stok_key]).get(),
                                 coll_id=utils.coll_getter(coll),
                                 indv_year=year,
                                 pit_tag=row[self.pit_key],
                                 ufid=ufid,
                                 indv_valid=True,
                                 comments=comments,
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
        try:
            indv.clean()
            indv.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            indv = models.Individual.objects.filter(pit_tag=indv.pit_tag).get()

        tank_id = models.Tank.objects.filter(name=row[self.tank_key]).get()
        self.row_entered += utils.enter_contx(tank_id, cleaned_data, True, indv_pk=indv.pk)

        anix, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv.pk)
        self.row_entered += anix_entered

        self.row_entered += utils.enter_bulk_indvd(anix.pk, cleaned_data, row_date,
                                                   gender=row.get(self.sex_key),
                                                   lifestage=row.get(self.lifestage_key),
                                                   comments=row.get(self.comment_key))


class MasterGrpParser(DataParser):
    tank_key = "Tank"
    group_key = "Group"
    mark_key = "Mark"
    stok_key = "Stock"
    year_coll_key = "Collection"
    cnt_key = "Number of Fish"
    lifestage_key = "Lifestage"
    comment_key = "Comments"

    header = 2
    sheet_name = "Group"
    converters = {tank_key: str, 'Year': str, 'Month': str, 'Day': str}

    salmon_id = None
    prog_grp_anidc_id = None
    mark_anidc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.tank_key, self.group_key, self.stok_key, self.year_coll_key, self.cnt_key])
        self.mandatory_filled_keys.extend([self.tank_key, self.stok_key, self.year_coll_key, self.cnt_key])
        super(MasterGrpParser, self).load_data()

    def data_preper(self):
        self.salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()
        self.mark_anidc_id = models.AnimalDetCode.objects.filter(name="Mark").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        year, coll = utils.year_coll_splitter(row[self.year_coll_key])
        row_datetime = utils.get_row_date(row)
        comments = None
        if utils.nan_to_none(row.get(self.comment_key)):
            comments = utils.nan_to_none(row[self.comment_key])

        tank_id = models.Tank.objects.filter(name=row[self.tank_key]).get()
        prog_grp_id = None
        if utils.nan_to_none(row[self.group_key]):
            prog_grp_id = models.AniDetSubjCode.objects.filter(anidc_id=self.prog_grp_anidc_id,
                                                               name__icontains=row[self.group_key]).get()
        mark_id = None
        if utils.nan_to_none(row[self.mark_key]):
            mark_id = models.AniDetSubjCode.objects.filter(anidc_id=self.mark_anidc_id,
                                                               name__icontains=row[self.mark_key]).get()

        grp_list = utils.get_grp(row[self.stok_key], year, coll, cont=tank_id, at_date=row_datetime,
                                 prog_grp=prog_grp_id, grp_mark=mark_id)
        if grp_list:
            grp_id = grp_list[0]
        else:
            grp_id = models.Group(spec_id=self.salmon_id,
                                  stok_id=models.StockCode.objects.filter(name=row[self.stok_key]).get(),
                                  coll_id=utils.coll_getter(coll),
                                  grp_year=year,
                                  grp_valid=True,
                                  comments=comments,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
            try:
                grp_id.clean()
                grp_id.save()
                self.row_entered = True
            except (ValidationError, IntegrityError) as err:
                raise Exception("Error creating new group: {}".format(err))

        anix, anix_entered = utils.enter_anix(cleaned_data, grp_pk=grp_id.pk)
        self.row_entered += anix_entered

        self.row_entered = utils.enter_bulk_grpd(anix.pk, cleaned_data, row_datetime,
                                                 prog_grp=row.get(self.group_key),
                                                 mark=row.get(self.mark_key),
                                                 lifestage=row.get(self.lifestage_key),
                                                 comments=row.get(self.comment_key))

        contx, contx_entered = utils.enter_contx(tank_id, cleaned_data, True, grp_pk=grp_id.pk, return_contx=True)
        self.row_entered += contx_entered

        cnt, cnt_entered = utils.enter_cnt(cleaned_data, utils.nan_to_none(row[self.cnt_key]), contx_pk=contx.pk,
                                           cnt_code="Fish Count")
        self.row_entered += cnt_entered

        if utils.nan_to_none(row.get(self.comment_key)):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix,
                                                                 det_date=row_datetime.date())
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row:\n {} \n\n".format(row[self.comment_key])
