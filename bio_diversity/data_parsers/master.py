from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class MasterParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    tank_key = "Tank"
    group_key = "Group"
    stok_key = "Stock"
    year_coll_key = "Collection"
    pit_key = "PIT Tag"
    comment_key = "Comments"
    sex_key = "Sex"

    header = 2
    converters = {tank_key: str, 'Year': str, 'Month': str, 'Day': str}

    salmon_id = None
    sex_anidc_id = None
    ani_health_anidc_id = None

    def data_preper(self):
        self.salmon_id = models.SpeciesCode.objects.filter(name__iexact="Salmon").get()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        year, coll = utils.year_coll_splitter(row[self.year_coll_key])
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()
        comments = None
        if utils.nan_to_none(row[self.comment_key]):
            comments = utils.nan_to_none(row[self.comment_key])
        indv = models.Individual(grp_id_id=None,
                                 spec_id=self.salmon_id,
                                 stok_id=models.StockCode.objects.filter(name=row[self.stok_key]).get(),
                                 coll_id=models.Collection.objects.filter(name__icontains=coll).get(),
                                 indv_year=year,
                                 pit_tag=row[self.pit_key],
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
        if utils.nan_to_none(row[self.sex_key]):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date,
                                                  self.sex_dict[row[self.sex_key].upper()],
                                                  self.sex_anidc_id.pk, None, None)
        if utils.nan_to_none(row[self.comment_key]):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix,
                                                                 det_date=row_datetime.date())
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row[self.pit_key],
                                                                                             row[self.comment_key])
