
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd
from decimal import Decimal

from pandas import read_excel

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser, common_err_parser


class TreatmentParser(DataParser):
    tank_key = "Tank"
    trof_key = "Trough"
    quantity_ml_key = "Amount (ml)"
    quantity_gal_key = "Amount (Gal)"
    quantity_kg_key = "Amount (kg)"
    duration_key = "Duration (hours)"
    duration_mins_key = "Duration (mins)"
    concentration_key = "Concentration"
    treatment_key = "Treatment Type"
    water_level_key = "Water Level During Treatment (Inches)"
    team_key = "Initials"

    tank_data = None
    eggroom_data = None
    water_envc_id = None
    ml_unit_id = None
    kg_unit_id = None
    gal_unit_id = None

    header = 2
    converters = {tank_key: str, trof_key: str, 'Year': str, 'Month': str, 'Day': str}
    tank_sheet_name = "Ponds"
    eggroom_sheet_name = "Eggrooms"
    tank_data_dict = {}
    eggroom_data_dict = {}

    def load_data(self):
        self.mandatory_keys.extend([self.tank_key, self.treatment_key])
        super(TreatmentParser, self).load_data()

    def data_reader(self):
        self.tank_data = read_excel(self.cleaned_data["data_csv"], header=self.header, engine='openpyxl',
                                    converters=self.converters, sheet_name=self.tank_sheet_name)
        self.tank_data = self.tank_data.mask(self.tank_data.eq('None')).dropna(how="all")
        # to keep parent parser classes happy:
        self.data = self.tank_data
        self.tank_data_dict = self.tank_data.to_dict('records')

        self.eggroom_data = read_excel(self.cleaned_data["data_csv"], header=self.header, engine='openpyxl',
                                       converters=self.converters, sheet_name=self.eggroom_sheet_name)
        self.eggroom_data = self.eggroom_data.mask(self.eggroom_data.eq('None')).dropna(how="all")
        self.eggroom_data_dict = self.eggroom_data.to_dict('records')

    def data_preper(self):
        self.water_envc_id = models.EnvCode.objects.filter(name="Water Level").get()
        self.ml_unit_id = models.UnitCode.objects.filter(name__icontains="Milliliters").get()
        self.kg_unit_id = models.UnitCode.objects.filter(name__icontains="Kilograms").get()
        self.gal_unit_id = models.UnitCode.objects.filter(name__icontains="Gallons").get()

    def iterate_rows(self):
        self.data_dict = self.tank_data_dict
        for row in self.data_dict:
            if self.success:
                self.row_entered = False
                try:
                    self.tank_row_parser(row)
                except Exception as err:
                    err_msg = common_err_parser(err)
                    self.log_data += "\nError:  {} \nError occured when parsing row: \n".format(err_msg)
                    self.log_data += str(row)
                    self.parsed_row_counter()
                    self.success = False
                self.rows_parsed += 1
                if self.row_entered:
                    self.rows_entered += 1

        if self.success:
            self.log_data += "\nParsed Tank data: \n"
            self.parsed_row_counter()

        self.data_dict = self.eggroom_data_dict
        self.rows_parsed = 0
        self.rows_entered = 0
        for row in self.data_dict:
            if self.success:
                self.row_entered = False
                try:
                    self.eggroom_row_parser(row)
                except Exception as err:
                    err_msg = common_err_parser(err)
                    self.log_data += "\nError:  {} \nError occured when parsing row: \n".format(err_msg)
                    self.log_data += str(row)
                    self.parsed_row_counter()
                    self.success = False
                self.rows_parsed += 1
                if self.row_entered:
                    self.rows_entered += 1

    def tank_row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()

        contx, data_entered = utils.enter_tank_contx(row[self.tank_key], cleaned_data, None, return_contx=True)
        self.row_entered += data_entered
        duration = row[self.duration_key]

        amt = None
        unit = None
        if utils.nan_to_none(row.get(self.quantity_kg_key)):
            amt = row[self.quantity_kg_key]
            unit = self.kg_unit_id
        elif utils.nan_to_none(row.get(self.quantity_ml_key)):
            amt = row[self.quantity_ml_key]
            unit = self.ml_unit_id
        elif utils.nan_to_none(row.get(self.quantity_gal_key)):
            amt = utils.nan_to_none(row[self.quantity_gal_key])
            unit = self.gal_unit_id

        row_concentration = utils.parse_concentration(row[self.concentration_key])
        envt = models.EnvTreatment(contx_id=contx,
                                   envtc_id=models.EnvTreatCode.objects.filter(
                                       name__icontains=row[self.treatment_key]).get(),
                                   lot_num=None,
                                   amt=amt,
                                   unit_id=unit,
                                   duration=60 * duration,
                                   start_datetime=row_datetime,
                                   concentration=row_concentration.quantize(Decimal("0.000001")),
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )

        try:
            envt.clean()
            envt.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            pass

        self.row_entered += utils.enter_env(row[self.water_level_key], row_date, cleaned_data, self.water_envc_id,
                                            contx=contx)

        self.team_parser(row[self.team_key], row)

    def eggroom_row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()

        contx, data_entered = utils.enter_trof_contx(str(row[self.trof_key]), cleaned_data, None, return_contx=True)
        self.row_entered += data_entered
        amt = None
        unit = None
        if utils.nan_to_none(row.get(self.quantity_kg_key)):
            amt = row[self.quantity_kg_key]
            unit = self.kg_unit_id
        elif utils.nan_to_none(row.get(self.quantity_ml_key)):
            amt = row[self.quantity_ml_key]
            unit = self.ml_unit_id
        elif utils.nan_to_none(row.get(self.quantity_gal_key)):
            amt = utils.nan_to_none(row[self.quantity_gal_key])
            unit = self.gal_unit_id
        duration = row[self.duration_mins_key]
        row_concentration = utils.parse_concentration(row[self.concentration_key])
        envt = models.EnvTreatment(contx_id=contx,
                                   envtc_id=models.EnvTreatCode.objects.filter(
                                       name__icontains=row[self.treatment_key]).get(),
                                   lot_num=None,
                                   amt=amt,
                                   unit_id=unit,
                                   duration=duration,
                                   concentration=row_concentration.quantize(Decimal("0.000001")),
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )

        try:
            envt.clean()
            envt.save()
            self.row_entered = True
        except (ValidationError, IntegrityError):
            pass

        self.row_entered += utils.enter_env(row[self.water_level_key], row_date, cleaned_data, self.water_envc_id,
                                            contx=contx)

        self.team_parser(row[self.team_key], row)


class MactaquacTreatmentParser(TreatmentParser):
    pass


class ColdbrookTreatmentParser(TreatmentParser):
    pass
