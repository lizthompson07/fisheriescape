
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bio_diversity import models
from bio_diversity.utils import DataParser


class ContainerParser(DataParser):
    name_key = "Name"
    desc_key = "Description"

    header = 2
    row_count = header + 2
    converters = {name_key: str, desc_key: str, }
    sheet_name = "Template"
    cont = None

    def load_data(self):
        self.mandatory_keys = [self.name_key, self.desc_key]
        self.mandatory_filled_keys = [self.name_key, self.desc_key]
        super(ContainerParser, self).load_data()

    def row_parser(self, row):
        try:
            self.cont.clean()
            self.cont.save()
            self.row_entered = True
        except (IntegrityError, ValidationError) as err:
            self.log_data += "{} Row {} not entered. \n".format(self.sheet_name, self.row_count)
        self.row_count += 1


class TankParser(ContainerParser):
    sheet_name = "Tanks"

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        self.cont = models.Tank(name=row.get(self.name_key),
                                description_en=row.get(self.desc_key),
                                facic_id=cleaned_data["facic_id"],
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"]
                                )
        super(TankParser, self).row_parser(row)


class TroughParser(ContainerParser):
    sheet_name = "Troughs"

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        self.cont = models.Trough(name=row.get(self.name_key),
                                  description_en=row.get(self.desc_key),
                                  facic_id=cleaned_data["facic_id"],
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"]
                                  )
        super(TroughParser, self).row_parser(row)


class HeathUnitParser(ContainerParser):
    sheet_name = "HeathUnits"

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        self.cont = models.HeathUnit(name=row.get(self.name_key),
                                     description_en=row.get(self.desc_key),
                                     facic_id=cleaned_data["facic_id"],
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"]
                                     )
        super(HeathUnitParser, self).row_parser(row)
