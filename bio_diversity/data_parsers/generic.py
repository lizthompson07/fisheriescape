import copy

from pandas import DataFrame

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

    converters = {vial_key: str, envelope_key: str, start_tank_key: str, end_tank_key: str, pit_key: str, "Year": str, "Month": str, "Day": str}
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
        self.mandatory_filled_keys.extend([self.pit_key])
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

        utils.enter_bulk_indvd(anix, self.cleaned_data, row_date,
                               gender=row.get(self.sex_key),
                               len_mm=row.get(self.len_key_mm),
                               len=row.get(self.len_key),
                               weight=row.get(self.weight_key),
                               weight_kg=row.get(self.weight_key_kg),
                               vial=row.get(self.vial_key),
                               scale_envelope=row.get(self.envelope_key),
                               tissue_yn=row.get(self.tissue_key),
                               )

        if utils.nan_to_none(row.get(self.precocity_key)):
            if utils.y_n_to_bool(row[self.precocity_key]):
                self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, None,
                                                      self.ani_health_anidc_id.pk, "Precocity")
        if utils.nan_to_none(row.get(self.mort_key)):
            if utils.y_n_to_bool(row[self.mort_key]):
                mort_evnt, mort_anix, mort_entered = utils.enter_mortality(indv, self.cleaned_data, row_datetime)
                self.row_entered += mort_entered

        in_tank = None
        out_tank = None
        if utils.nan_to_none(row[self.start_tank_key]):
            in_tank = models.Tank.objects.filter(name=row[self.start_tank_key]).get()
        if utils.nan_to_none(row[self.end_tank_key]):
            out_tank = models.Tank.objects.filter(name=row[self.end_tank_key]).get()
        if in_tank or out_tank:
            self.row_entered += utils.create_movement_evnt(in_tank, out_tank, self.cleaned_data, row_datetime,
                                                           indv_pk=indv.pk)

        if utils.nan_to_none(row.get(self.comment_key)):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix, row_date)
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row[self.pit_key],
                                                                                             row[self.comment_key])

        for adsc_id in self.cleaned_data["adsc_id"]:
            if utils.y_n_to_bool(row.get(adsc_id.name)):
                self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, adsc_id.name,
                                                      adsc_id.anidc_id.pk, adsc_str=adsc_id.name)


class GenericUntaggedParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    yr_coll_key = "Year Class"
    rive_key = "River"
    prio_key = "Group"
    samp_key = "Sample"
    sex_key = "Sex"
    len_key = "Length (cm)"
    len_key_mm = "Length (mm)"
    weight_key = "Weight (g)"
    weight_key_kg = "Weight (kg)"
    vial_key = "Vial"
    envelope_key = "Scale Envelope"
    mort_key = "Mortality (Y/N)"
    precocity_key = "Precocity (Y/N)"
    tissue_key = "Tissue Sample (Y/N)"
    ufid_key = "UFID"
    start_tank_key = "Origin Pond"
    end_tank_key = "Destination Pond"
    comment_key = "Comments"

    header = 2
    sheet_name = "Untagged"
    start_grp_dict = {}
    end_grp_dict = {}
    converters = {samp_key: str, vial_key: str, envelope_key: str, start_tank_key: str, end_tank_key: str, ufid_key: str, 'Year': str, 'Month': str, 'Day': str}

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
        self.mandatory_keys.extend([self.yr_coll_key, self.rive_key, self.prio_key, self.samp_key])
        super(GenericUntaggedParser, self).load_data()

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

        # The following steps are to set additional columns on each row to facilitate parsing.
        # In particular,  columns set will be: "datetime", "grp_year", "grp_coll", "start_tank_id",
        # "end_tank_id", "grp_key", "end_grp_key".
        # The two grp_keys will link to dictionaries of the groups, which are also set below

        # set date
        self.data = utils.set_row_datetime(self.data)
        # split year-coll
        self.data["grp_year"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[0], axis=1)
        self.data["grp_coll"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[1], axis=1)

        # set start and end tank columns:
        self.data = utils.set_row_tank(self.data, cleaned_data, self.start_tank_key, col_name="start_tank_id")
        self.data = utils.set_row_tank(self.data, cleaned_data, self.end_tank_key, col_name="end_tank_id")

        # set the dict keys for groups, use astype(str) to handle anything that might be a nan.
        self.data, self.start_grp_dict = utils.set_row_grp(self.data, self.rive_key, self.yr_coll_key, self.prio_key,
                                                           "start_tank_id", "datetime", grp_col_name="start_grp_id",
                                                           return_dict=True)
        for item, grp in self.start_grp_dict.items():
            utils.enter_anix(cleaned_data, grp_pk=grp.pk)

        self.data["end_grp_key"] = self.data[self.rive_key] + self.data[self.yr_coll_key] + \
                                   self.data[self.end_tank_key].astype(str) + self.data[self.prio_key].astype(str) + \
                                   self.data["datetime"].astype(str)

        # create the end group dict and create, movement event, groups, counts, contxs, etc. necesarry
        end_grp_data = self.data.groupby(
            [self.rive_key, "grp_year", "grp_coll", "end_tank_id", "start_tank_id", self.prio_key, "datetime",
             "grp_key", "end_grp_key"],
            dropna=False, sort=False).size().reset_index()
        for row in end_grp_data.to_dict('records'):
            # check if end tank is set, otherwise, skip this step
            if not utils.nan_to_none(row["end_tank_id"]):
                self.end_grp_dict[row["end_grp_key"]] = None
                continue
            grps = utils.get_grp(row[self.rive_key], row["grp_year"], row["grp_coll"], row["end_tank_id"],
                                 at_date=row["datetime"], prog_str=row[self.prio_key])
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
                if utils.nan_to_none(row[self.prio_key]):
                    utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, self.prog_grp_anidc_id.pk,
                                     row[self.prio_key])
                end_contx = utils.create_movement_evnt(row["start_tank_id"], row["end_tank_id"], cleaned_data,
                                                       row["datetime"],
                                                       grp_pk=end_grp_id.pk, return_end_contx=True)
                if end_contx:
                    self.row_entered += utils.enter_cnt(cleaned_data, row[0], end_contx.pk)[1]
        self.data_dict = self.data.to_dict("records")

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = row["datetime"].date()
        row_grp = row["start_grp_id"]
        row_end_grp = self.end_grp_dict[row["end_grp_key"]]
        if row_end_grp:
            row_grp = row_end_grp
        row_anix, data_entered = utils.enter_anix(cleaned_data, grp_pk=row_grp.pk)
        self.row_entered += data_entered
        row_samp = None
        if utils.nan_to_none(row.get(self.mort_key)):
            if utils.y_n_to_bool(row[self.mort_key]):
                mort_out = utils.enter_grp_mortality(row_grp, row[self.samp_key], cleaned_data, row_date, cont=row.get("start_tank_id"))
                row_samp = mort_out[0]
                self.row_entered += mort_out[3]

        if not row_samp:
            row_samp, data_entered = utils.enter_samp(cleaned_data, row[self.samp_key], row_grp.spec_id.pk,
                                                      self.sampc_id.pk,
                                                      anix_pk=row_anix.pk)
            self.row_entered += data_entered

        if row_samp:
            if utils.nan_to_none(row.get(self.sex_key)):
                self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date,
                                                      self.sex_dict[row[self.sex_key].upper()], self.sex_anidc_id.pk)
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

            for adsc_id in cleaned_data["adsc_id"]:
                if utils.y_n_to_bool(row.get(adsc_id.name)):
                    self.row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, adsc_id.name,
                                                          adsc_id.anidc_id.pk, adsc_str=adsc_id.name)

        else:
            self.success = False


class GenericGrpParser(DataParser):
    yr_coll_key = "Year Class"
    rive_key = "River"
    prio_key = "Group"
    start_tank_key = "Origin Pond"
    end_tank_key = "Destination Pond"
    nfish_key = "Number of Fish"
    abs_key = "Whole group (Y/N)"
    comment_key = "Comments"
    vax_key = "Vaccinated"
    mark_key = "Mark Applied"

    header = 2
    sheet_name = "Group"
    start_grp_dict = {}
    end_grp_dict = {}
    converters = {start_tank_key: str, end_tank_key: str, 'Year': str, 'Month': str, 'Day': str}

    prnt_grp_anidc_id = None
    prog_grp_anidc_id = None
    vax_anidc_id = None
    mark_anidc_id = None

    def load_data(self):
        self.mandatory_keys.extend([self.yr_coll_key, self.rive_key, self.prio_key])
        super(GenericGrpParser, self).load_data()

    def data_preper(self):
        cleaned_data = self.cleaned_data
        self.prnt_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Parent Group").get()
        self.prog_grp_anidc_id = models.AnimalDetCode.objects.filter(name="Program Group").get()
        self.vax_anidc_id = models.AnimalDetCode.objects.filter(name="Vaccination").get()
        self.mark_anidc_id = models.AnimalDetCode.objects.filter(name="Mark").get()

        # set date
        self.data = utils.set_row_datetime(self.data)
        # split year-coll
        self.data["grp_year"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[0], axis=1)
        self.data["grp_coll"] = self.data.apply(lambda row: utils.year_coll_splitter(row[self.yr_coll_key])[1], axis=1)

        # set start and end tank columns:
        self.data = utils.set_row_tank(self.data, cleaned_data, self.start_tank_key, col_name="start_tank_id")
        self.data = utils.set_row_tank(self.data, cleaned_data, self.end_tank_key, col_name="end_tank_id")
        self.data_dict = self.data.to_dict("records")

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        row_date = row["datetime"].date()
        row_start_grp = utils.get_grp(row[self.rive_key], row["grp_year"], row["grp_coll"], row["start_tank_id"],
                                      row_date, prog_str=row[self.prio_key], fail_on_not_found=True)[0]
        start_anix, self.row_entered = utils.enter_anix(cleaned_data, grp_pk=row_start_grp.pk)
        start_contx, contx_entered = utils.enter_contx(row["start_tank_id"], cleaned_data, None, return_contx=True)
        self.row_entered += contx_entered

        whole_grp = utils.y_n_to_bool(row[self.abs_key])
        det_anix = None
        row["start_contx_pk"] = None
        if not whole_grp:
            row["start_contx_pk"] = start_contx.pk

        if row["end_tank_id"]:
            # 4 possible cases here: group in tank or not and whole group move or not:
            row_end_grp_list = utils.get_grp(row[self.rive_key], row["grp_year"], row["grp_coll"], row["end_tank_id"],
                                             row_date, prog_str=row[self.prio_key])
            row_end_grp = None
            if not whole_grp and not row_end_grp_list:
                # splitting fish group, create end group:
                row_end_grp = copy.deepcopy(row_start_grp)
                row_end_grp.pk = None
                row_end_grp.id = None
                row_end_grp.save()
                end_grp_anix, anix_entered = utils.enter_anix(cleaned_data, grp_pk=row_end_grp.pk)
                self.row_entered = anix_entered
                if utils.nan_to_none(row[self.prio_key]):
                    self.row_entered += utils.enter_grpd(end_grp_anix.pk, cleaned_data, row_date, None,
                                                         self.prog_grp_anidc_id, adsc_str=row[self.prio_key])
            elif not whole_grp:
                row_end_grp = row_end_grp_list[0]

            if row_end_grp:
                move_contx = utils.create_movement_evnt(row["start_tank_id"], row["end_tank_id"], cleaned_data,
                                                        row_date, grp_pk=row_end_grp.pk, return_end_contx=True)
                end_grp_anix, anix_entered = utils.enter_anix(cleaned_data, grp_pk=row_end_grp.pk)
                self.row_entered += anix_entered
                self.row_entered += utils.enter_grpd(end_grp_anix.pk, cleaned_data, row_date, None,
                                                     self.prnt_grp_anidc_id.pk, frm_grp_id=row_start_grp)
                cnt, cnt_entered = utils.enter_cnt(cleaned_data, row[self.nfish_key], move_contx.pk)
                self.row_entered = cnt_entered

                det_anix = end_grp_anix

            else:
                det_anix = start_anix
                move_contx = utils.create_movement_evnt(row["start_tank_id"], row["end_tank_id"], cleaned_data,
                                                        row_date, grp_pk=row_start_grp.pk, return_end_contx=True)
                cnt, cnt_entered = utils.enter_cnt(cleaned_data, row[self.nfish_key], move_contx.pk,
                                                   cnt_code="Fish Count")
                self.row_entered = cnt_entered

        elif whole_grp:
            cnt, cnt_entered = utils.enter_cnt(cleaned_data, row[self.nfish_key], start_contx.pk,
                                               cnt_code="Fish Count")
            self.row_entered = cnt_entered


        # add details to det_anix:

        if utils.nan_to_none(row.get(self.vax_key)):
            self.row_entered += utils.enter_grpd(det_anix.pk, cleaned_data, row_date, None, self.vax_anidc_id.pk,
                                                 adsc_str=row[self.vax_key])
        if utils.nan_to_none(row.get(self.mark_key)):
            self.row_entered += utils.enter_grpd(det_anix.pk, cleaned_data, row_date, None, self.mark_anidc_id.pk,
                                                 adsc_str=row[self.mark_key])

    def clean_data(self):
        if self.success:
            contx_df = DataFrame(self.data_dict)
            cnt_df = contx_df.groupby("start_contx_pk", as_index=False).sum()
            for row in cnt_df.to_dict('records'):
                if utils.nan_to_none(row["start_contx_pk"]):
                    cnt, cnt_entered = utils.enter_cnt(self.cleaned_data, 0, int(row["start_contx_pk"]),
                                                       cnt_code="Fish Removed from Container")
                    cnt.cnt = row[self.nfish_key]
                    cnt.save()

