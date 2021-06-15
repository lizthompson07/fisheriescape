from django.core.exceptions import ValidationError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
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
    crew_lead_key = "crew lead"
    temp_key = "Temperature"
    fish_caught_key = "# of salmon collected"
    fish_obs_key = "# of salmon observed"
    settings_key = "Settings"
    fishing_time_key = "fishing seconds"
    voltage_key = "Voltage"
    group_key = "Group"
    coll_key = "Collection"
    tank_key = "End Tank"

    header = 2
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
        river_group_data = self.data.groupby([self.rive_key, self.group_key, self.coll_key, self.tank_key],
                                             dropna=False).size().reset_index()

        if not river_group_data[self.tank_key].is_unique:
            raise Exception("Too many different groups going into same tank. Create multiple events if needed")

        for index, row in river_group_data.iterrows():
            stok_id = models.StockCode.objects.filter(name__icontains=row[self.rive_key]).get()
            coll_id = models.Collection.objects.filter(name__icontains=row[self.coll_key]).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              grp_id__coll_id=coll_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              pair_id__isnull=True)

            grp_found = False
            grp = None
            for anix in anix_grp_qs:
                anix_prog_grp_names = [adsc.name for adsc in anix.grp_id.prog_group()]
                if utils.nan_to_none(row[self.group_key]) and row[self.group_key] in anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
                elif not utils.nan_to_none(row[self.group_key]) and not anix_prog_grp_names:
                    grp_found = True
                    grp = anix.grp_id
                    break
            if not grp_found:
                grp = models.Group(spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                   stok_id=stok_id,
                                   coll_id=coll_id,
                                   grp_year=self.data[self.year_key][0],
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
                if utils.nan_to_none(row[self.group_key]):
                    utils.enter_grpd(anix_grp.pk, cleaned_data, cleaned_data["evnt_id"].start_date, None,
                                     None, anidc_str="Program Group", adsc_str=row[self.group_key])

            if utils.nan_to_none(row[self.group_key]):
                data_rows = (self.data[self.rive_key] == row[self.rive_key]) & \
                            (self.data[self.group_key] == row[self.group_key]) & \
                            (self.data[self.tank_key] == row[self.tank_key]) & \
                            (self.data[self.coll_key] == row[self.coll_key])
            else:
                data_rows = (self.data[self.rive_key] == row[self.rive_key]) & \
                    (self.data[self.coll_key] == row[self.coll_key]) & \
                    (self.data[self.tank_key] == row[self.tank_key]) & \
                    (self.data[self.group_key].isnull())

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
        if utils.nan_to_none(row[self.site_key]):
            relc_qs = models.ReleaseSiteCode.objects.filter(name__iexact=row[self.site_key])
            if len(relc_qs) == 1:
                relc_id = relc_qs.get()

        start_lat = utils.round_no_nan(row[self.lat_key], 5)
        start_lon = utils.round_no_nan(row[self.lon_key], 5)
        if not relc_id and not (start_lat and start_lon):
            raise Exception("Site code not found and lat-long not given for site on row")
        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=rive_id,
                              relc_id=relc_id,
                              loc_lat=start_lat,
                              loc_lon=start_lon,
                              end_lat=utils.round_no_nan(row[self.end_lat], 5),
                              end_lon=utils.round_no_nan(row[self.end_lon], 5),
                              loc_date=row_datetime,
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
        self.loc = loc
        self.row_entered += utils.enter_anix(cleaned_data, loc_pk=loc.pk, grp_pk=row["grp_id"].pk, return_sucess=True)
        if self.loc.loc_lon and self.loc.loc_lat and not self.loc.relc_id:
            self.log_data += "\nNo site found in db for Lat-Long ({}, {}) given on row: \n\n{}".format(self.loc.loc_lat, self.loc.loc_lon, row)
        self.team_parser(row[self.crew_key], row, loc_id=loc)

        self.row_entered += utils.enter_env(row[self.temp_key], row_datetime, cleaned_data, self.temp_envc_id, loc_id=loc)

        cnt_caught, cnt_entered = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_caught_key], loc_pk=loc.pk,
                                                  cnt_code="Fish Caught")
        self.row_entered += cnt_entered
        cnt_obs, cnt_entered = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_obs_key], loc_pk=loc.pk,
                                               cnt_code="Fish Observed")
        self.row_entered += cnt_entered

        self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.settings_key],
                                             self.settings_locdc_id.pk)
        self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.fishing_time_key],
                                             self.fishing_time_locdc_id.pk)
        self.row_entered += utils.enter_locd(loc.pk, cleaned_data, row_datetime, row[self.voltage_key],
                                             self.voltage_locdc_id.pk)


class ColdbrookElectrofishingParser(ElectrofishingParser):

    def row_parser(self, row):
        super().row_parser(row)

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

