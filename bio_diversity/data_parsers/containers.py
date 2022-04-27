
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bio_diversity import models, utils
from bio_diversity.utils import DataParser


class ContainerParser(DataParser):
    name_key = "Name"
    desc_key = "Description"

    header = 1
    comment_row = [2]
    row_count = header + 3
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

    surf_area_key = "Effective Surface Area"

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        tank_id = models.Tank.objects.filter(name=row.get(self.name_key), facic_id=cleaned_data["facic_id"]).first()
        if tank_id:
            self.cont = tank_id
            self.cont.description_en = row.get(self.desc_key)
        else:
            self.cont = models.Tank(name=row.get(self.name_key),
                                    description_en=row.get(self.desc_key),
                                    facic_id=cleaned_data["facic_id"],
                                    created_by=cleaned_data["created_by"],
                                    created_date=cleaned_data["created_date"]
                                    )
        super(TankParser, self).row_parser(row)

        if utils.nan_to_none(row.get(self.surf_area_key)):
            self.row_entered += utils.enter_tankd(self.cont.pk, cleaned_data, start_date=utils.aware_min(),
                                                  det_value=row.get(self.surf_area_key), contdc_pk=None,
                                                  contdc_str="Effective Surface Area")


class TroughParser(ContainerParser):
    sheet_name = "Troughs"

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        trof_id = models.Trough.objects.filter(name=row.get(self.name_key), facic_id=cleaned_data["facic_id"]).first()
        if trof_id:
            self.cont = trof_id
            self.cont.description_en = row.get(self.desc_key)
        else:
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

        if "." in row.get(self.name_key):
            cont_list = row.get(self.name_key).split(".")
            hu_name = cont_list[0]
            draw_name = cont_list[1]
            hu_id = models.HeathUnit.objects.filter(name=hu_name, facic_id=cleaned_data["facic_id"]).first()
            if hu_id:
                self.cont = hu_id
                self.cont.description_en = row.get(self.desc_key)
            else:
                hu_id = models.HeathUnit(name=hu_name,
                                         description_en=row.get(self.desc_key),
                                         facic_id=cleaned_data["facic_id"],
                                         created_by=cleaned_data["created_by"],
                                         created_date=cleaned_data["created_date"]
                                         )
            try:
                hu_id.clean()
                hu_id.save()
            except (IntegrityError, ValidationError) as err:
                self.log_data += "{} Row {} not entered. \n".format(self.sheet_name, self.row_count)

            draw_id = models.Drawer.objects.filter(name=draw_name, heat_id=hu_id).first()
            if draw_id:
                draw_id.description_en = row.get(self.desc_key)
            else:
                draw_id = models.Drawer(name=draw_name,
                                        description_en=row.get(self.desc_key),
                                        heat_id=hu_id,
                                        created_by=cleaned_data["created_by"],
                                        created_date=cleaned_data["created_date"]
                                        )
            try:
                draw_id.clean()
                draw_id.save()
            except (IntegrityError, ValidationError) as err:
                self.log_data += "{} Row {} not entered. \n".format(self.sheet_name, self.row_count)
            self.row_count += 1

        else:
            hu_id = models.HeathUnit.objects.filter(name=row.get(self.name_key), facic_id=cleaned_data["facic_id"]).first()
            if hu_id:
                self.cont = hu_id
                self.cont.description_en = row.get(self.desc_key)
            else:
                self.cont = models.HeathUnit(name=row.get(self.name_key),
                                             description_en=row.get(self.desc_key),
                                             facic_id=cleaned_data["facic_id"],
                                             created_by=cleaned_data["created_by"],
                                             created_date=cleaned_data["created_date"]
                                             )
            super(HeathUnitParser, self).row_parser(row)
