from django.core.exceptions import ValidationError
import pandas as pd
from django.db import IntegrityError

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class ElectrofishingParser(DataParser):
    rive_key = "River"
    site_key = "site"
    lat_key = "Lat"
    lon_key = "Long"
    end_lat = "End Lat"
    end_lon = "End Long"
    comment_key = "Comments"
    crew_key = "Crew"
    crew_lead_key = "Crew lead"
    temp_key = "Temperature"
    fish_caught_key = "# of salmon collected"
    fish_obs_key = "# of salmon observed"
    settings_key = "Settings"
    fishing_time_key = "fishing seconds"
    voltage_key = "Voltage"
    prio_key = "Group"
    coll_key = "Collection"
    tank_key = "End Tank"

    header = 2
    converters = {tank_key: str, 'Year': str, 'Month': str, 'Day': str}
    start_grp_dict = {}
    end_grp_dict = {}

    temp_envc_id = None
    leader_code = None
    settings_locdc_id = None
    voltage_locdc_id = None
    fishing_time_locdc_id = None

    loc = None
    locc_id = None
    river_dict = {}

    def load_data(self):
        self.mandatory_keys.extend([self.rive_key, self.prio_key, self.coll_key, self.tank_key, self.crew_key,
                                    self.fish_caught_key, self.fish_obs_key, self.site_key])
        self.mandatory_filled_keys.extend([self.rive_key, self.coll_key])
        super(ElectrofishingParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
        self.leader_code = models.RoleCode.objects.filter(name__iexact="Crew Lead").get()
        self.settings_locdc_id = models.LocationDetCode.objects.filter(name__iexact="Electrofishing Settings").get()
        self.voltage_locdc_id = models.LocationDetCode.objects.filter(name__iexact="Voltage").get()
        self.fishing_time_locdc_id = models.LocationDetCode.objects.filter(name__iexact="Electrofishing Seconds").get()

        for river_name in self.data[self.rive_key].unique():
            self.river_dict[river_name] = models.RiverCode.objects.filter(name__icontains=river_name).get()

        if self.cleaned_data["evntc_id"].__str__() == "Electrofishing":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Electrofishing site").get()
        elif self.cleaned_data["evntc_id"].__str__() == "Smolt Wheel Collection":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Smolt Wheel site").get()
        elif self.cleaned_data["evntc_id"].__str__() == "Bypass Collection":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Bypass site").get()

        # assign groups to columns, add generic group data:
        self.data["grp_id"] = None

        river_group_data = self.data.groupby([self.rive_key, self.prio_key, self.year_key, self.coll_key, self.tank_key],
                                             dropna=False).size().reset_index()

        if not river_group_data[self.tank_key].is_unique:
            raise Exception("Too many different groups going into same tank. Create multiple events if needed")

        for index, row in river_group_data.iterrows():
            if not utils.nan_to_none(row[self.tank_key]):
                # if fish are only observed, don't make a group
                data_rows = (self.data[self.tank_key].isnull())
                self.data.loc[data_rows, "grp_id"] = None
                break
            stok_id = models.StockCode.objects.filter(name__icontains=row[self.rive_key]).get()

            coll_str = row[self.coll_key]
            if len(coll_str.lstrip(' 0123456789')) == len(coll_str):
                # year taken from year coll:
                coll_id = utils.coll_getter(row[self.coll_key])
                grp_year = row[self.year_key]
            else:
                grp_year, coll_str = utils.year_coll_splitter(row[self.coll_key])
                coll_id = utils.coll_getter(coll_str)

            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              grp_id__coll_id=coll_id,
                                                              grp_id__grp_year=grp_year,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)

            grp_found = False
            grp = None
            for anix in anix_grp_qs:
                anix_prog_grp_names = [adsc.name for adsc in anix.grp_id.prog_group()]
                if utils.nan_to_none(row[self.prio_key]) and row[self.prio_key] in anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
                elif not utils.nan_to_none(row[self.prio_key]) and not anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
            if not grp_found:
                grp = models.Group(spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                   stok_id=stok_id,
                                   coll_id=coll_id,
                                   grp_year=grp_year,
                                   grp_valid=True,
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
                try:
                    grp.clean()
                    grp.save()
                except ValidationError:
                    grp = models.Group.objects.filter(spec_id=grp.spec_id, stok_id=grp.stok_id,
                                                      grp_year=grp.grp_year, coll_id=grp.coll_id).get()

                anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk, return_anix=True)
                if utils.nan_to_none(row.get(self.prio_key)):
                    utils.enter_grpd(anix_grp.pk, cleaned_data, cleaned_data["evnt_id"].start_date, None,
                                     None, anidc_str="Program Group", adsc_str=row[self.prio_key])

            # create index column matching all rows in data to this group-tank-prio combination
            if utils.nan_to_none(row.get(self.prio_key)):
                data_rows = (self.data[self.rive_key] == row[self.rive_key]) & \
                            (self.data[self.prio_key] == row[self.prio_key]) & \
                            (self.data[self.tank_key] == row[self.tank_key]) & \
                            (self.data[self.coll_key] == row[self.coll_key])
            else:
                data_rows = (self.data[self.rive_key] == row[self.rive_key]) & \
                    (self.data[self.coll_key] == row[self.coll_key]) & \
                    (self.data[self.tank_key] == row[self.tank_key]) & \
                    (self.data[self.prio_key].isnull())

            # grp found, assign to all rows:
            self.data.loc[data_rows, "grp_id"] = grp
            contx, data_entered = utils.enter_tank_contx(row[self.tank_key], cleaned_data, True, None, grp.pk,
                                                         return_contx=True)

        self.data_dict = self.data.to_dict("records")

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row)
        relc_id = None
        rive_id = self.river_dict[row[self.rive_key]]

        if not utils.nan_to_none(row.get(self.tank_key)) and utils.nan_to_none(row.get(self.fish_caught_key)):
            # make sure if fish are caught they are assigned a tank:
            raise Exception("All Caught fish must be assigned a tank")

        if utils.nan_to_none(row.get(self.site_key)):
            relc_qs = models.ReleaseSiteCode.objects.filter(name__iexact=row[self.site_key])
            if len(relc_qs) == 1:
                relc_id = relc_qs.get()

        start_lat = utils.round_no_nan(row.get(self.lat_key), 6)
        start_lon = utils.round_no_nan(row.get(self.lon_key), 6)
        if not relc_id and not (start_lat and start_lon):
            raise Exception("Site code not found and lat-long not given for site on row")
        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=rive_id,
                              relc_id=relc_id,
                              loc_lat=start_lat,
                              loc_lon=start_lon,
                              end_lat=utils.round_no_nan(row.get(self.end_lat), 6),
                              end_lon=utils.round_no_nan(row.get(self.end_lon), 6),
                              loc_date=row_datetime,
                              comments=utils.nan_to_none(row.get(self.comment_key)),
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            loc.clean()
            loc.save()
            self.row_entered = True
        except ValidationError:
            loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                 rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                 relc_id=loc.relc_id, loc_lat=loc.loc_lat,
                                                 loc_lon=loc.loc_lon, loc_date=loc.loc_date).get()
        self.loc = loc
        if row["grp_id"]:
            self.row_entered += utils.enter_anix(cleaned_data, loc_pk=loc.pk, grp_pk=row["grp_id"].pk, return_sucess=True)
        if self.loc.loc_lon and self.loc.loc_lat and not self.loc.relc_id:
            self.log_data += "\nNo site found in db for Lat-Long ({}, {}) given on row: \n{}\n\n".format(self.loc.loc_lat, self.loc.loc_lon, row)

        self.team_parser(row[self.crew_key], row, loc_id=loc)

        if utils.nan_to_none(row.get(self.temp_key)):
            self.row_entered += utils.enter_env(row[self.temp_key], row_datetime, cleaned_data, self.temp_envc_id,
                                                loc_id=loc)

        cnt_caught, cnt_entered = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_caught_key], loc_pk=loc.pk,
                                                  cnt_code="Fish Caught")
        self.row_entered += cnt_entered
        cnt_obs, cnt_entered = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_obs_key], loc_pk=loc.pk,
                                               cnt_code="Fish Observed")
        self.row_entered += cnt_entered

        if utils.nan_to_none(row.get(self.settings_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.settings_key],
                                                 self.settings_locdc_id.pk)
        if utils.nan_to_none(row.get(self.fishing_time_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.fishing_time_key],
                                                 self.fishing_time_locdc_id.pk)
        if utils.nan_to_none(row.get(self.voltage_key)):
            self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.voltage_key],
                                                 self.voltage_locdc_id.pk)


class ColdbrookElectrofishingParser(ElectrofishingParser):

    def row_parser(self, row):
        super().row_parser(row)

        if utils.nan_to_none(row.get(self.crew_lead_key)):
            self.team_parser(row[self.crew_lead_key], row, loc_id=self.loc, role_id=self.leader_code)


class MactaquacElectrofishingParser(ElectrofishingParser):
    site_key = "Location Name"
    end_lat = "Lat.1"
    end_lon = "Long.1"
    temp_key = "Temperature"
    fish_caught_key = "# Fish Collected"
    fish_obs_key = "# Fish Observed"
    settings_key = "Fishing Settings"
    fishing_time_key = "Fishing Seconds"
    header = 2
    tank_key = "Destination Pond"
    coll_key = "Year Class"


class AdultCollectionParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    site_key = "Site"
    wr_key = "Wild Return"
    pit_key = "PIT Tag"
    new_pit_key = "Newly Applied"
    grp_key = "Group"
    coll_key = "Collection"
    tank_key = "End Tank"
    len_key = "Length (cm)"
    len_key_mm = "Length (mm)"
    weight_key = "Weight (g)"
    weight_key_kg = "Weight (kg)"
    sex_key = "Sex"
    scale_key = "Scale Sample"
    vial_key = "Vial"
    mort_key = "Mort"
    samp_key = "Sample #"
    aquaculture_key = "Aquaculture"
    comment_key = "Comments"
    crew_key = "Crew"

    header = 2
    converters = {tank_key: str, pit_key: str,  "Year": str, "Month": str, "Day": str}

    prog_grp_anidc_id = None
    sex_anidc_id = None
    len_anidc_id = None
    weight_anidc_id = None
    vial_anidc_id = None
    envelope_anidc_id = None
    ani_health_anidc_id = None
    locc_id = None
    salmon_id = None
    wr_adsc_id = None
    sampc_id = None

    site_dict = {}
    tank_dict = {}
    loc_obs_dict = {}
    loc_caught_dict = {}

    loc = None
    
    def load_data(self):
        self.mandatory_keys.extend([self.site_key, self.wr_key, self.pit_key, self.tank_key, self.crew_key,
                                    self.coll_key])
        self.mandatory_filled_keys.extend([self.site_key, self.coll_key])
        super(AdultCollectionParser, self).load_data()
        
    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        self.weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        self.vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()
        self.envelope_anidc_id = models.AnimalDetCode.objects.filter(name="Scale Envelope").get()
        self.wr_adsc_id = models.AniDetSubjCode.objects.filter(name="Wild Return").get()
        self.locc_id = models.LocCode.objects.filter(name="Adult Collection Site").get()
        self.salmon_id = models.SpeciesCode.objects.filter(name="Salmon").get()
        self.sampc_id = models.SampleCode.objects.filter(name="Individual Sample").get()

        for site_name in self.data[self.site_key].unique():
            if utils.nan_to_none(site_name):
                self.site_dict[site_name] = models.ReleaseSiteCode.objects.filter(name__icontains=site_name).select_related("rive_id").get()

        for tank_name in self.data[self.tank_key].unique():
            if utils.nan_to_none(tank_name):
                self.tank_dict[tank_name] = models.Tank.objects.filter(name__iexact=tank_name, facic_id=cleaned_data["facic_id"]).get()
                utils.enter_contx(self.tank_dict[tank_name], cleaned_data)

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row)
        relc_id = self.site_dict[row[self.site_key]]
        indv_id = None
        if utils.nan_to_none(row[self.pit_key]):
            indv_id = models.Individual.objects.filter(pit_tag=row[self.pit_key]).first()
            if not indv_id:
                year, coll = utils.year_coll_splitter(row[self.coll_key])
                coll_id = utils.coll_getter(coll)
                stok_id = models.StockCode.objects.filter(name__iexact=relc_id.rive_id.name).get()
                indv_id = models.Individual(spec_id=self.salmon_id,
                                            stok_id=stok_id,
                                            coll_id=coll_id,
                                            indv_year=year,
                                            pit_tag=row[self.pit_key],
                                            indv_valid=True,
                                            comments=utils.nan_to_none(row.get(self.comment_key)),
                                            created_by=cleaned_data["created_by"],
                                            created_date=cleaned_data["created_date"],
                                            )
                try:
                    indv_id.clean()
                    indv_id.save()
                    self.row_entered = True
                except (ValidationError, IntegrityError):
                    indv_id = models.Individual.objects.filter(pit_tag=indv_id.pit_tag).get()
            indv_anix, data_entered = utils.enter_anix(cleaned_data, indv_pk=indv_id.pk)
            self.row_entered += data_entered
            # add program group to individual if needed:

        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=relc_id.rive_id,
                              relc_id=relc_id,
                              loc_date=row_datetime,
                              created_by=cleaned_data["created_by"],
                              created_date=cleaned_data["created_date"],
                              )
        try:
            loc.clean()
            loc.save()
            self.row_entered = True
        except ValidationError:
            loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                 rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                 relc_id=loc.relc_id, loc_lat=loc.loc_lat,
                                                 loc_lon=loc.loc_lon, loc_date=loc.loc_date).get()
        self.loc = loc
        self.team_parser(row[self.crew_key], row, loc_id=loc)

        if indv_id:
            anix_loc_indv, anix_entered = utils.enter_anix(cleaned_data, loc_pk=loc.pk, indv_pk=indv_id.pk)
            self.row_entered += anix_entered
        elif utils.nan_to_none(row.get(self.samp_key)):
            samp, samp_entered = utils.enter_samp(cleaned_data, row[self.samp_key], self.salmon_id.pk, self.sampc_id.pk,
                                                  loc_pk=loc.pk, comments=utils.nan_to_none(row.get(self.comment_key)))
            self.row_entered += samp_entered
            if utils.nan_to_none(row[self.comment_key]):
                comments_parsed, data_entered = utils.samp_comment_parser(row[self.comment_key], cleaned_data,
                                                                          samp.pk, row_datetime)
                self.row_entered += data_entered
                if not comments_parsed:
                    self.log_data += "Unparsed comment on row {}:\n {} \n\n".format(row, row[self.comment_key])
        else:
            raise Exception("Fish must either be assigned a sample number or a pit tag.")

        if not indv_id:
            return

        self.row_entered += utils.enter_bulk_indvd(anix_loc_indv.pk, self.cleaned_data, row_datetime,
                                                   gender=row.get(self.sex_key),
                                                   len_mm=row.get(self.len_key_mm),
                                                   len_val=row.get(self.len_key),
                                                   weight=row.get(self.weight_key),
                                                   weight_kg=row.get(self.weight_key_kg),
                                                   vial=row.get(self.vial_key),
                                                   scale_envelope=row.get(self.scale_key),
                                                   prog_grp=row.get(self.grp_key),
                                                   comments=row.get(self.comment_key)
                                                   )

        if utils.nan_to_none(row.get(self.mort_key)):
            if utils.y_n_to_bool(row[self.mort_key]):
                mort_evnt, mort_anix, mort_entered = utils.enter_mortality(indv_id, self.cleaned_data, row_datetime)
                self.row_entered += mort_entered

        if utils.nan_to_none(row.get(self.wr_key)):
            if utils.y_n_to_bool(row[self.wr_key]):
                self.row_entered += utils.enter_indvd(anix_loc_indv.pk, cleaned_data, row_datetime, None,
                                                      self.ani_health_anidc_id.pk, adsc_str=self.wr_adsc_id.name)

        if utils.nan_to_none(row.get(self.aquaculture_key)):
            if utils.y_n_to_bool(row[self.aquaculture_key]):
                self.row_entered += utils.enter_indvd(anix_loc_indv.pk, cleaned_data, row_datetime, None,
                                                      self.ani_health_anidc_id.pk, adsc_str="Aquaculture")

        if utils.nan_to_none(row[self.tank_key]):
            self.row_entered += utils.enter_contx(self.tank_dict[row[self.tank_key]], cleaned_data, True, indv_id.pk)
            if self.loc.pk not in self.loc_caught_dict:
                self.loc_caught_dict[self.loc.pk] = 1
            else:
                self.loc_caught_dict[self.loc.pk] += 1
        else:
            if self.loc.pk not in self.loc_obs_dict:
                self.loc_obs_dict[self.loc.pk] = 1
            else:
                self.loc_obs_dict[self.loc.pk] += 1

    def data_cleaner(self):
        for loc_pk, cnt_caught in self.loc_caught_dict.items():
            utils.enter_cnt(self.cleaned_data, cnt_caught, loc_pk=loc_pk, cnt_code="Fish Caught")
        for loc_pk, cnt_obs in self.loc_obs_dict.items():
            utils.enter_cnt(self.cleaned_data, cnt_obs, loc_pk=loc_pk, cnt_code="Fish Observed")
