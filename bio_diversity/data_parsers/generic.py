import copy

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants
from bio_diversity.utils import DataParser


class GenericIndvParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    pit_key = "PIT"
    sex_key = "Sex"
    len_key = "Length (cm)"
    len_key_mm = "Length (mm)"
    weight_key = "Weight (g)"
    weight_key_kg = "Weight (kg)"
    vial_key = "Vial"
    envelope_key = "Scale Envelope"
    precocity_key = "Precocity (Y/N)"
    mort_key = "Mortality (Y/N)"
    tissue_key = "Tissue Sample (Y/N)"
    start_tank_key = "Origin Pond"
    end_tank_key = "Destination Pond"
    comment_key = "Comments"

    converters = {pit_key: str, "Year": str, "Month": str, "Day": str}
    header = 2
    sheet_name = "Individual"

    sex_anidc_id = None
    len_anidc_id = None
    weight_anidc_id = None
    vial_anidc_id = None
    envelope_anidc_id = None
    ani_health_anidc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.pit_key])
        super(GenericIndvParser, self).load_data()

    def data_preper(self):
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        self.weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        self.vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        self.envelope_anidc_id = models.AnimalDetCode.objects.filter(name="Scale Envelope").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()

    def row_parser(self, row):
        row_datetime = utils.get_row_date(row)
        row_date = row_datetime.date()

        indv_qs = models.Individual.objects.filter(pit_tag=row[self.pit_key])
        if len(indv_qs) == 1:
            indv = indv_qs.get()
        else:
            self.log_data += "Error parsing row: \n"
            self.log_data += str(row)
            self.log_data += "\nFish with PIT {} not found in db\n".format(row[self.pit_key])
            self.success = False

        anix, anix_entered = utils.enter_anix(self.cleaned_data, indv_pk=indv.pk)
        self.row_entered += anix_entered

        if utils.nan_to_none(row.get(self.sex_key)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date,
                                                  self.sex_dict[row[self.sex_key].upper()],
                                                  self.sex_anidc_id.pk, None, None)
        if utils.nan_to_none(row.get(self.len_key_mm)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, 0.1 * row[self.len_key_mm],
                                                  self.len_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.len_key)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.len_key],
                                                  self.len_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.weight_key_kg)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, 1000 * row[self.weight_key_kg],
                                                  self.weight_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.weight_key)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.weight_key],
                                                  self.weight_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.vial_key)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.vial_key],
                                                  self.vial_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.envelope_key)):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.envelope_key],
                                                  self.envelope_anidc_id.pk, None)
        if utils.nan_to_none(row.get(self.precocity_key)):
            if utils.y_n_to_bool(row[self.precocity_key]):
                self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, None,
                                                      self.ani_health_anidc_id.pk, "Precocity")
        if utils.nan_to_none(row.get(self.mort_key)):
            if utils.y_n_to_bool(row[self.mort_key]):
                mort_evnt, mort_anix, mort_entered = utils.enter_mortality(indv, self.cleaned_data, row_date)
                self.row_entered += mort_entered
        if utils.nan_to_none(row.get(self.tissue_key)):
            if utils.y_n_to_bool(row[self.tissue_key]):
                self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, None,
                                                      self.ani_health_anidc_id.pk, "Tissue Sample")

        if utils.nan_to_none(row[self.start_tank_key]) or utils.nan_to_none(row[self.end_tank_key]):
            in_tank = models.Tank.objects.filter(name=row[self.start_tank_key]).get()
            out_tank = models.Tank.objects.filter(name=row[self.end_tank_key]).get()
            self.row_entered += utils.create_movement_evnt(in_tank, out_tank, self.cleaned_data, row_datetime,
                                                           indv_pk=indv.pk)

        if utils.nan_to_none(row.get(self.comment_key)):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix, row_date)
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row[self.pit_key],
                                                                                             row[self.comment_key])


class GenericGrpParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    yr_coll_key = "Year Class"
    rive_key = "River"
    group_key = "Group"
    samp_key = "Sample"
    sex_key = "Sex"
    len_key = "Length (cm)"
    len_key_mm = "Length (mm)"
    weight_key = "Weight (g)"
    weight_key_kg = "Weight (kg)"
    vial_key = "Vial"
    envelope_key = "Scale Envelope"
    precocity_key = "Precocity (Y/N)"
    tissue_key = "Tissue Sample (Y/N)"
    ufid_key = "UFID"
    start_tank_key = "Origin Pond"
    end_tank_key = "Destination Pond"
    comment_key = "Comments"

    header = 2
    sheet_name = "Group"
    start_grp_dict = {}
    end_grp_dict = {}
    converters = {ufid_key: str, 'Year': str, 'Month': str, 'Day': str}

    sampc_id = None
    prnt_grp_anidc_id = None
    prog_grp_anidc_id = None
    sex_anidc_id = None
    len_anidc_id = None
    weight_anidc_id = None
    vial_anidc_id = None
    envelope_anidc_id = None
    ani_health_anidc_id = None
    anidc_ufid_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.yr_coll_key, self.rive_key, self.group_key, self.samp_key])
        super(GenericGrpParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.sampc_id = models.SampleCode.objects.filter(name="Individual Sample").get()
        self.prnt_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Parent Group").get()
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()
        self.sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        self.len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        self.weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        self.vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        self.envelope_anidc_id = models.AnimalDetCode.objects.filter(name="Scale Envelope").get()
        self.ani_health_anidc_id = models.AnimalDetCode.objects.filter(name="Animal Health").get()
        self.anidc_ufid_id = models.AnimalDetCode.objects.filter(name="UFID").get()

        # set date
        self.data["datetime"] = self.data.apply(lambda row: utils.get_row_date(row), axis=1)
        # split year-coll
        self.data["grp_year"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[0], axis=1)
        self.data["grp_coll"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[1], axis=1)

        # set start and end tanks:
        tank_qs = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"])
        tank_dict = {tank.name: tank for tank in tank_qs}
        self.data["start_tank_id"] = self.data.apply(lambda row: tank_dict[row[self.start_tank_key]], axis=1)
        self.data["end_tank_id"] = self.data.apply(lambda row: tank_dict[row[self.end_tank_key]], axis=1)

        # set the dict keys for groups
        self.data["grp_key"] = self.data[self.rive_key] + self.data[self.yr_coll_key] + self.data[self.start_tank_key] \
                               + self.data[self.group_key].astype(str) + self.data["datetime"].astype(str)

        self.data["end_grp_key"] = self.data[self.rive_key] + self.data[self.yr_coll_key] + \
                                   self.data[self.end_tank_key] + self.data[self.group_key].astype(str) + \
                                   self.data["datetime"].astype(str)

        # create the start_grp dict and enter anixs:
        start_grp_data = self.data.groupby(
            [self.rive_key, "grp_year", "grp_coll", "start_tank_id", self.group_key, "datetime", "grp_key"],
            dropna=False, sort=False).size().reset_index()
        start_grp_data["start_grp_id"] = start_grp_data.apply(
            lambda row: utils.get_grp(row[self.rive_key], row["grp_year"], row["grp_coll"],
                                      row["start_tank_id"], at_date=row["datetime"],
                                      prog_str=row[self.group_key], fail_on_not_found=True)[0], axis=1)
        self.start_grp_dict = dict(zip(start_grp_data['grp_key'], start_grp_data['start_grp_id']))
        for item, grp in self.start_grp_dict.items():
            utils.enter_anix(cleaned_data, grp_pk=grp.pk)

        # create the end group dict and create, movement event, groups, counts, contxs, etc. necesarry
        end_grp_data = self.data.groupby(
            [self.rive_key, "grp_year", "grp_coll", "end_tank_id", "start_tank_id", self.group_key, "datetime",
             "grp_key", "end_grp_key"],
            dropna=False, sort=False).size().reset_index()
        for row in end_grp_data.to_dict('records'):
            grps = utils.get_grp(row[self.rive_key], row["grp_year"], row["grp_coll"], row["end_tank_id"],
                                 at_date=row["datetime"], prog_str=row[self.group_key])
            start_grp_id = self.start_grp_dict[row["grp_key"]]
            start_contx, contx_entered = utils.enter_contx(row["start_tank_id"], cleaned_data, None,
                                                           grp_pk=start_grp_id.pk, return_contx=True)
            self.row_entered += utils.enter_cnt(cleaned_data, sum(end_grp_data[end_grp_data["grp_key"] == row["grp_key"]][0]),
                                                start_contx.pk, cnt_code="Fish Removed from Container")[1]

            if len(grps) > 0:
                end_grp_id = grps[0]
                self.end_grp_dict[row["end_grp_key"]] = grps[0]
            else:
                end_grp_id = copy.deepcopy(start_grp_id)
                end_grp_id.pk = None
                end_grp_id.save()
                self.end_grp_dict[row["end_grp_key"]] = end_grp_id

            if end_grp_id.pk != start_grp_id.pk:
                grp_anix = utils.enter_anix(cleaned_data, grp_pk=end_grp_id.pk, return_anix=True)
                utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, self.prnt_grp_anidc_id.pk,
                                 frm_grp_id=start_grp_id)
                if utils.nan_to_none(row[self.group_key]):
                    utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, self.prog_grp_anidc_id.pk,
                                     row[self.group_key])
                end_contx = utils.create_movement_evnt(row["start_tank_id"], row["end_tank_id"], cleaned_data,
                                                       row["datetime"],
                                                       grp_pk=end_grp_id.pk, return_end_contx=True)
                if end_contx:
                    self.row_entered += utils.enter_cnt(cleaned_data, row[0], end_contx.pk)[1]
        self.data_dict = self.data.to_dict("records")

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = row["datetime"].date()
        row_grp = self.start_grp_dict[row["grp_key"]]
        row_end_grp = self.end_grp_dict[row["end_grp_key"]]
        if row_end_grp:
            row_grp = row_end_grp
        row_anix, data_entered = utils.enter_anix(cleaned_data, grp_pk=row_grp.pk)
        self.row_entered += data_entered
        row_samp, data_entered = utils.enter_samp(cleaned_data, row[self.samp_key], row_grp.spec_id.pk,
                                                  self.sampc_id.pk,
                                                  anix_pk=row_anix.pk)
        self.row_entered += data_entered

        if row_samp:
            if utils.nan_to_none(row.get(self.sex_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date,
                                                      self.sex_dict[row[self.sex_key]], self.sex_anidc_id.pk)
            if utils.nan_to_none(row.get(self.len_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row[self.len_key],
                                                      self.len_anidc_id.pk, )
            if utils.nan_to_none(row.get(self.len_key_mm)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, 0.1 * row[self.len_key_mm],
                                                      self.len_anidc_id.pk, )
            if utils.nan_to_none(row.get(self.weight_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row[self.weight_key],
                                                      self.weight_anidc_id.pk, )
            if utils.nan_to_none(row.get(self.weight_key_kg)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date,
                                                      1000 * row[self.weight_key_kg], self.weight_anidc_id.pk, )

            if utils.nan_to_none(row.get(self.vial_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row[self.vial_key],
                                                      self.vial_anidc_id.pk)
            if utils.nan_to_none(row.get(self.precocity_key)):
                if utils.y_n_to_bool(row[self.precocity_key]):
                    self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, "Precocity",
                                                          self.ani_health_anidc_id.pk, adsc_str="Precocity")
            if utils.nan_to_none(row.get(self.tissue_key)):
                if utils.y_n_to_bool(row[self.tissue_key]):
                    self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, "Tissue Sample",
                                                          self.ani_health_anidc_id.pk, adsc_str="Tissue Sample")
            if utils.nan_to_none(row.get(self.ufid_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row[self.ufid_key],
                                                      self.anidc_ufid_id.pk)
            if utils.nan_to_none(row.get(self.envelope_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row[self.envelope_key],
                                                      self.envelope_anidc_id.pk)

            if utils.nan_to_none(row[self.comment_key]):
                comments_parsed, data_entered = utils.samp_comment_parser(row[self.comment_key], cleaned_data,
                                                                          row_samp.pk, row_date)
                self.row_entered += data_entered
                if not comments_parsed:
                    self.log_data += "Unparsed comment on row {}:\n {} \n\n".format(row, row[self.comment_key])

        else:
            self.success = False
