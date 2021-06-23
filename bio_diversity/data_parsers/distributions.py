
from django.core.exceptions import ValidationError
from django.db.models import Count as django_Count
from django.db.models import Q

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class DistributionParser(DataParser):
    time_key = "Time"
    driver_key = "Driver"
    crew_key = "Crew"
    truck_key = "Truck"
    site_key = "Site"
    lat_key = "Lat"
    lon_key = "Long"
    stok_key = "Stock"
    year_coll_key = "Year Collection"
    prog_key = "Program"
    tank_key = "Tank"
    trof_key = "Trough"
    relm_key = "Release Method"
    temp_key = "River Temp"
    truck_temp = "Truck Temp"
    acclimation_key = "Acclimation Time (mins)"
    lifestage_key = "Lifestage"
    len_key = "Len (cm)"
    len_key_mm = "Len (mm)"
    weight_key_kg = "Weight (kg)"
    weight_key = "Weight (g)"
    num_key = "NFish"
    comment_key = "Comments"

    temp_envc_id = None
    truck_locdc_id = None
    relm_locdc_id = None
    acclimation_locdc_id = None
    lifestage_locdc_id = None
    locc_id = None
    len_anidc_id = None
    weight_anidc_id = None
    driver_role_id = None

    header = 2
    converters = {tank_key: str, trof_key: str, 'Year': str, 'Month': str, 'Day': str}
    sheet_name = "Groups"

    def load_data(self):
        self.mandatory_keys.extend([self.stok_key, self.year_coll_key, self.prog_key, self.num_key])
        super(DistributionParser, self).load_data()

    def data_preper(self):
        self.temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
        self.truck_locdc_id = models.LocationDetCode.objects.filter(name="Truck").get()
        self.relm_locdc_id = models.LocationDetCode.objects.filter(name="Release Method").get()
        self.acclimation_locdc_id = models.LocationDetCode.objects.filter(name="Acclimation Time").get()
        self.lifestage_locdc_id = models.LocationDetCode.objects.filter(name="Lifestage").get()
        self.locc_id = models.LocCode.objects.filter(name__icontains="Distribution site").get()
        self.len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        self.weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        self.driver_role_id = models.RoleCode.objects.filter(name__iexact="Driver").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = utils.get_row_date(row)

        # need to find contanier and group for row:
        cont_id = None
        if utils.nan_to_none(row[self.tank_key]):
            if "," in str(row[self.tank_key]):
                tank_list = str(row[self.tank_key]).split(",")
                # TODO

            cont_id = models.Tank.objects.filter(name__iexact=row[self.tank_key], facic_id__name=cleaned_data["facic_id"]).get()
        elif utils.nan_to_none(row[self.trof_key]):
            if "," in row[self.trof_key]:
                trof_list = row[self.trof_key].split(",")
                # TODO

            cont_id = models.Trough.objects.filter(name__iexact=row[self.trof_key], facic_id__name=cleaned_data["facic_id"]).get()
        grp_year, coll = utils.year_coll_splitter(row[self.year_coll_key])
        grp_list = utils.get_grp(row[self.stok_key], grp_year, coll, cont=cont_id, at_date=row_date, prog_str=row[self.prog_key])
        if not grp_list:
            raise Exception("\n No group found in container: {}".format(cont_id.__str__()))
        grp_id = grp_list[0]
        self.row_entered += utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, return_sucess=True)
        self.row_entered += utils.enter_contx(cont_id, cleaned_data)

        relc_id = None
        rive_id = models.RiverCode.objects.filter(name__icontains=row[self.stok_key]).get()
        if utils.nan_to_none(row[self.site_key]):
            relc_id = models.ReleaseSiteCode.objects.filter(name__iexact=row[self.site_key], rive_id=rive_id).get()

        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=rive_id,
                              relc_id=relc_id,
                              loc_lat=utils.round_no_nan(row[self.lat_key], 5),
                              loc_lon=utils.round_no_nan(row[self.lon_key], 5),
                              loc_date=row_date,
                              comments=utils.nan_to_none(row[self.comment_key]),
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            loc.set_relc_latlng()
            loc.clean()
            loc.save()
            self.row_entered = True
        except ValidationError:
            loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                 rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                 relc_id=loc.relc_id, loc_lat=loc.loc_lat,
                                                 loc_lon=loc.loc_lon, loc_date=loc.loc_date).get()

        self.row_entered += utils.enter_anix(cleaned_data, grp_pk=grp_id.pk, loc_pk=loc.pk, return_sucess=True)

        if utils.nan_to_none(row.get(self.crew_key)):
            self.team_parser(row[self.crew_key], row, loc_id=loc)
        if utils.nan_to_none(row.get(self.driver_key)):
            self.team_parser(row[self.driver_key], row, loc_id=loc, role_id=self.driver_role_id)

        if utils.nan_to_none(row.get(self.temp_key)):
            self.row_entered += utils.enter_env(row[self.temp_key], row_date, cleaned_data, self.temp_envc_id,
                                                loc_id=loc)
        if utils.nan_to_none(row.get(self.truck_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.truck_key],
                                                 self.truck_locdc_id.pk, None)
        if utils.nan_to_none(row.get(self.relm_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.relm_key],
                                                 self.relm_locdc_id.pk, row[self.relm_key])
        if utils.nan_to_none(row.get(self.acclimation_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.acclimation_key],
                                                 self.acclimation_locdc_id.pk, None)
        if utils.nan_to_none(row.get(self.lifestage_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.lifestage_key],
                                                 self.lifestage_locdc_id.pk, row[self.lifestage_key])

        cnt, cnt_entered = utils.enter_cnt(cleaned_data, cnt_value=row[self.num_key], loc_pk=loc.pk,
                                           cnt_code="Fish Distributed")
        self.row_entered += cnt_entered

        if utils.nan_to_none(row.get(self.len_key)):
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt, row[self.len_key], self.len_anidc_id.name)
        if utils.nan_to_none(row.get(self.len_key_mm)):
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt, 0.1 * row[self.len_key_mm],
                                                    self.len_anidc_id.name)
        if utils.nan_to_none(row.get(self.weight_key_kg)):
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt, 1000 * row[self.weight_key_kg],
                                                    self.weight_anidc_id.name)
        if utils.nan_to_none(row.get(self.weight_key)):
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt, row[self.weight_key], self.weight_anidc_id.name)


class DistributionIndvParser(DataParser):
    time_key = "Time"
    driver_key = "Driver"
    crew_key = "Crew"
    truck_key = "Truck"
    site_key = "Site"
    lat_key = "Lat"
    lon_key = "Long"
    pit_key = "PIT Tag"
    vial_key = "Vial"
    prog_key = "Program"
    tank_key = "Tank"
    trof_key = "Trough"
    relm_key = "Release Method"
    temp_key = "River Temp"
    truck_temp = "Truck Temp"
    acclimation_key = "Acclimation Time (mins)"
    lifestage_key = "Lifestage"
    len_key = "Len (cm)"
    len_key_mm = "Len (mm)"
    weight_key_kg = "Weight (kg)"
    weight_key = "Weight (g)"
    sex_key = "Sex"
    tissue_key = "Tissue (Y/N)"
    comment_key = "Comments"

    temp_envc_id = None
    truck_locdc_id = None
    relm_locdc_id = None
    acclimation_locdc_id = None
    lifestage_locdc_id = None
    locc_id = None
    sex_anidc_id = None
    len_anidc_id = None
    weight_anidc_id = None
    vial_anidc_id = None
    ani_health_anidc_id = None
    driver_role_id = None

    sex_dict = calculation_constants.sex_dict

    header = 2
    converters = {tank_key: str, trof_key: str, pit_key: str, 'Year': str, 'Month': str, 'Day': str}
    sheet_name = "Individuals"

    def data_preper(self):
        self.temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
        self.truck_locdc_id = models.LocationDetCode.objects.filter(name="Truck").get()
        self.relm_locdc_id = models.LocationDetCode.objects.filter(name="Release Method").get()
        self.acclimation_locdc_id = models.LocationDetCode.objects.filter(name="Acclimation Time").get()
        self.lifestage_locdc_id = models.LocationDetCode.objects.filter(name="Lifestage").get()
        self.locc_id = models.LocCode.objects.filter(name__icontains="Distribution site").get()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        self.weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        self.vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()
        self.driver_role_id = models.RoleCode.objects.filter(name__iexact="Driver").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = utils.get_row_date(row)

        # need to find contanier and group for row:
        cont_id = None
        if utils.nan_to_none(row[self.tank_key]):
            if "," in str(row[self.tank_key]):
                tank_list = str(row[self.tank_key]).split(",")
                # TODO

            cont_id = models.Tank.objects.filter(name__iexact=row[self.tank_key], facic_id__name=cleaned_data["facic_id"]).get()
        elif utils.nan_to_none(row[self.trof_key]):
            if "," in row[self.trof_key]:
                trof_list = row[self.trof_key].split(",")
                # TODO

            cont_id = models.Trough.objects.filter(name__iexact=row[self.trof_key], facic_id__name=cleaned_data["facic_id"]).get()
        indv_id = models.Individual.objects.filter(pit_tag__iexact=row[self.pit_key]).get()
        self.row_entered += utils.enter_anix(cleaned_data, indv_pk=indv_id.pk, return_sucess=True)
        self.row_entered += utils.enter_contx(cont_id, cleaned_data)

        relc_id = None
        rive_id = models.RiverCode.objects.filter(name__icontains=indv_id.stok_id.name).get()
        if utils.nan_to_none(row[self.site_key]):
            relc_id = models.ReleaseSiteCode.objects.filter(name__iexact=row[self.site_key], rive_id=rive_id).get()

        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=rive_id,
                              relc_id=relc_id,
                              loc_lat=utils.round_no_nan(row[self.lat_key], 5),
                              loc_lon=utils.round_no_nan(row[self.lon_key], 5),
                              loc_date=row_date,
                              comments=utils.nan_to_none(row[self.comment_key]),
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            loc.set_relc_latlng()
            loc.clean()
            loc.save()
            self.row_entered = True
        except ValidationError:
            loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                 rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                 relc_id=loc.relc_id, loc_lat=loc.loc_lat,
                                                 loc_lon=loc.loc_lon, loc_date=loc.loc_date).get()

        anix, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv_id.pk, loc_pk=loc.pk)
        self.row_entered += anix_entered

        if utils.nan_to_none(row.get(self.crew_key)):
            self.team_parser(row[self.crew_key], row, loc_id=loc)
        if utils.nan_to_none(row.get(self.driver_key)):
            self.team_parser(row[self.driver_key], row, loc_id=loc, role_id=self.driver_role_id)

        if utils.nan_to_none(row.get(self.temp_key)):
            self.row_entered += utils.enter_env(row[self.temp_key], row_date, cleaned_data, self.temp_envc_id,
                                                loc_id=loc)
        if utils.nan_to_none(row.get(self.truck_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.truck_key],
                                                 self.truck_locdc_id.pk, None)
        if utils.nan_to_none(row.get(self.relm_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.relm_key],
                                                 self.relm_locdc_id.pk, row[self.relm_key])
        if utils.nan_to_none(row.get(self.acclimation_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.acclimation_key],
                                                 self.acclimation_locdc_id.pk, None)

        if utils.nan_to_none(row.get(self.lifestage_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_date, row[self.lifestage_key],
                                                 self.lifestage_locdc_id.pk, row[self.lifestage_key])
        if utils.nan_to_none(row.get(self.len_key)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row[self.len_key], self.len_anidc_id)
        if utils.nan_to_none(row.get(self.len_key_mm)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, 0.1 * row[self.len_key_mm],
                                                  self.len_anidc_id)

        if utils.nan_to_none(row.get(self.weight_key)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row[self.weight_key],
                                                  self.weight_anidc_id)
        if utils.nan_to_none(row.get(self.weight_key_kg)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, 1000 * row[self.weight_key_kg],
                                                  self.weight_anidc_id)
        if utils.nan_to_none(row.get(self.vial_key)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row[self.vial_key],
                                                  self.vial_anidc_id)
        if utils.nan_to_none(row.get(self.sex_key)):
            self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, self.sex_dict[row[self.sex_key]],
                                                  self.sex_anidc_id)
        if utils.nan_to_none(row.get(self.tissue_key)):
            if utils.y_n_to_bool(row[self.tissue_key]):
                self.row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, None, "Tissue Sample")

        if utils.nan_to_none(row.get(self.comment_key)):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix, row_date)
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row {}:\n {} \n\n".format(row, row[self.comment_key])

        # remove fish from system
        indv_id.indv_valid = False
        indv_id.save()

    def data_cleaner(self):
        cleaned_data = self.cleaned_data
        loc_list = models.Location.objects.filter(evnt_id=cleaned_data["evnt_id"]).annotate(
            indv_cnt=django_Count('animal_details', filter=Q(animal_details__indv_id__isnull=False)))
        for loc in loc_list:
            if loc.indv_cnt != 0:
                utils.enter_cnt(cleaned_data, loc.indv_cnt, loc_pk=loc.pk, cnt_code="Fish Distributed")

