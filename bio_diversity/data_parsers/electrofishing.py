from django.core.exceptions import ValidationError
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.utils import DataParser


class ElectrofishingParser(DataParser):
    yr_coll_key = "Year Class"
    rive_key = "River"
    site_key = "site"
    lat_key = "Lat"
    lon_key = "Long"
    end_lat = "End Lat"
    end_lon = "End Long"
    comment_key = "Comments"
    crew_key = "Crew"
    crew_lead_key = "crew lead"
    temp_key = "temp"
    fish_caught_key = "# of salmon collected"
    fish_obs_key = "# of salmon observed"
    settings_key = "Settings"
    fishing_time_key = "fishing seconds"
    voltage_key = "Voltage"
    group_key = "Group"
    coll_key = "Collection"

    header = 0
    start_grp_dict = {}
    end_grp_dict = {}

    temp_envc_id = models.EnvCode.objects.filter(name="Temperature").get()
    leader_code = models.RoleCode.objects.filter(name__iexact="Crew Lead").get()

    loc = None
    locc_id = None
    river_dict = {}

    def data_preper(self):
        for river_name in self.data[self.rive_key].unique():
            self.river_dict[river_name] = models.RiverCode.objects.filter(name__icontains=river_name).get()

        if self.cleaned_data["evntc_id"].__str__() == "Electrofishing":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Electrofishing site").get()
        elif self.cleaned_data["evntc_id"].__str__() == "Smolt Wheel Collection":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Smolt Wheel site").get()
        elif self.cleaned_data["evntc_id"].__str__() == "Bypass Collection":
            self.locc_id = models.LocCode.objects.filter(name__icontains="Bypass site").get()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_datetime = utils.get_row_date(row)
        relc_id = None
        rive_id = self.river_dict[row[self.rive_key]]
        if utils.nan_to_none(row[self.site_key]):
            relc_qs = models.ReleaseSiteCode.objects.filter(name__iexact=row[self.site_key])
            if len(relc_qs) == 1:
                relc_id = relc_qs.get()
        loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                              locc_id=self.locc_id,
                              rive_id=rive_id,
                              relc_id=relc_id,
                              loc_lat=utils.round_no_nan(row[self.lat_key], 5),
                              loc_lon=utils.round_no_nan(row[self.lon_key], 5),
                              end_lat=utils.round_no_nan(row[self.end_lat], 5),
                              end_lon=utils.round_no_nan(row[self.end_lon], 5),
                              loc_date=row_datetime,
                              comments=row[self.comment_key],
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
        if utils.nan_to_none(row[self.crew_key]):
            row_percs, inits_not_found = utils.team_list_splitter(row[self.crew_key])
            for perc in row_percs:
                utils.add_team_member(perc, cleaned_data["evnt_id"], loc_id=loc)
            for inits in inits_not_found:
                self.log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                          row)

        self.row_entered += utils.enter_env(row[self.temp_key], row_datetime, cleaned_data, self.temp_envc_id, loc_id=loc)

        cnt_caught = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_caught_key], loc_pk=loc.pk,
                                     cnt_code="Fish Caught")
        cnt_obs = utils.enter_cnt(cleaned_data, cnt_value=row[self.fish_obs_key], loc_pk=loc.pk,
                                  cnt_code="Fish Observed")

        if cnt_caught:
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_caught, row[self.settings_key],
                                                    "Electrofishing Settings")
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_caught, row[self.fishing_time_key],
                                                    "Electrofishing Seconds")
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_caught, row[self.voltage_key], "Voltage")
        if cnt_obs:
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_obs, row[self.settings_key],
                                                    "Electrofishing Settings")
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_obs, row[self.fishing_time_key],
                                                    "Electrofishing Seconds")
            self.row_entered += utils.enter_cnt_det(cleaned_data, cnt_obs, row[self.voltage_key], "Voltage")

    def data_cleaner(self):
        cleaned_data = self.cleaned_data
        river_group_data = self.data.groupby([self.rive_key, self.group_key, self.coll_key],
                                             dropna=False).size().reset_index()
        for row in river_group_data:
            stok_id = models.StockCode.objects.filter(name__icontains=row[self.rive_key]).get()
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__stok_id=stok_id,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
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
                                   coll_id=models.Collection.objects.filter(name__icontains=row[self.coll_key]).get(),
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
                                     "Program Group", row[self.group_key])

            contx = utils.enter_tank_contx(cleaned_data["tank_id"].name, cleaned_data, True, None, grp.pk, True)

            if utils.nan_to_none(row[self.group_key]):
                utils.enter_cnt(cleaned_data, self.data[(self.data[self.rive_key] == row[self.rive_key]) &
                                                        (self.data[self.group_key] == row[self.group_key])][
                    self.fish_caught_key].sum(), contx_pk=contx.pk, cnt_code="Fish in Container", )
            else:
                utils.enter_cnt(cleaned_data, self.data[(self.data[self.rive_key] == row[self.rive_key]) &
                                                        (self.data[self.group_key].isnull())][
                    self.fish_caught_key].sum(), contx_pk=contx.pk, cnt_code="Fish in Container", )


class ColdbrookElectrofishingParser(ElectrofishingParser):

    def row_parser(self, row):
        super(ElectrofishingParser, self).row_parser()

        if utils.nan_to_none(row[self.crew_lead_key]):
            row_percs, inits_not_found = utils.team_list_splitter(row[self.crew_lead_key])
            for perc in row_percs:
                if utils.add_team_member(perc, self.cleaned_data["evnt_id"], loc_id=self.loc, role_id=self.leader_code):
                    self.row_entered = True
            for inits in inits_not_found:
                self.log_data += "No valid personnel with initials ({}) from this row in database {}\n".format(inits,
                                                                                                          row)


class MactaquacElectrofishingParser(ElectrofishingParser):
    site_key = "Location Name"
    end_lat = "Lat.1"
    end_lon = "Long.1"
    temp_key = " Temperature"
    fish_caught_key = "# Fish Collected"
    fish_obs_key = "# Fish Observed"
    settings_key = "Fishing Settings"
    fishing_time_key = "Fishing Seconds"
    header = 1

