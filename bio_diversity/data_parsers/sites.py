
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count as django_Count
from django.db.models import Q

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class SitesParser(DataParser):
    name_key = "Name"
    desc_key = "Description"
    rive_key = "River"
    trib_key = "Tributary"
    subr_key = "Subriver"
    lat_key = "Min Lat"
    max_lat_key = "Max Lat"
    lon_key = "Min Long"
    max_lon_key = "Max Long"

    header = 2
    row_count = header + 2
    converters = {name_key: str, lat_key: str, lon_key: str, max_lon_key: str, max_lat_key: str}

    def load_data(self):
        self.mandatory_keys = [self.name_key, self.rive_key, self.lat_key, self.lon_key, self.max_lon_key,
                               self.max_lat_key, self.desc_key, self.subr_key, self.trib_key]
        self.mandatory_filled_keys = [self.name_key, self.rive_key]
        super(SitesParser, self).load_data()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        rive_id = models.RiverCode.objects.filter(name__iexact=row.get(self.rive_key)).get()
        if not rive_id:
            self.log_data += "River Code not found on row: {}".format(row)
            self.success = False
            return
        subr_id = None
        if rive_id and utils.nan_to_none(row.get(self.subr_key)):
            subr_id = models.SubRiverCode.objects.filter(name__iexact=row.get(self.subr_key), rive_id=rive_id).get()
            if not subr_id:
                self.log_data += "Subriver Code not found on row: {}".format(row)
                self.success = False
                return

        trib_id = None
        if rive_id and utils.nan_to_none(row.get(self.trib_key)):
            trib_id = models.Tributary.objects.filter(name__iexact=row.get(self.trib_key), rive_id=rive_id).get()
            if not trib_id:
                self.log_data += "Tributary not found on row: {}".format(row)
                self.success = False
                return

        site_id = models.ReleaseSiteCode(name=row.get(self.name_key),
                                         description_en=row.get(self.desc_key),
                                         rive_id=rive_id,
                                         trib_id=trib_id,
                                         subr_id=subr_id,
                                         min_lat=utils.nan_to_none(row.get(self.lat_key)),
                                         max_lat=utils.nan_to_none(row.get(self.max_lat_key)),
                                         min_lon=utils.nan_to_none(row.get(self.lon_key)),
                                         max_lon=utils.nan_to_none(row.get(self.max_lon_key)),
                                         created_by=cleaned_data["created_by"],
                                         created_date=cleaned_data["created_date"]
        )
        try:
            site_id.clean()
            site_id.save()
            self.row_entered = True
        except (IntegrityError, ValidationError) as err:
            self.log_data += "Row {} not entered. \n".format(self.row_count)
        self.row_count += 1


