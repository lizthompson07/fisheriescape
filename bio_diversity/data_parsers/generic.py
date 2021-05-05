import copy
import pandas as pd

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.static import calculation_constants


class DataParser:
    log_data = "Loading Data Results: \n"
    success = True

    rows_parsed = 0
    rows_entered = 0
    row_entered = False

    cleaned_data = {}
    data = None
    data_dict = None

    year_key = "Year"
    month_key = "Month"
    day_key = "Day"

    def __init__(self, cleaned_data):
        self.cleaned_data = cleaned_data
        self.load_data()
        self.prep_data()
        self.iterate_rows()
        self.clean_data()

    def load_data(self):
        # load data
        try:
            self.data_reader()
            self.data_dict = self.data.to_dict('records')
        except Exception as err:
            self.log_data += "\n File format not valid: {}".format(err.__str__())
            self.success = False

    def data_reader(self):
        self.data = pd.read_excel(self.cleaned_data["data_csv"], header=1, engine='openpyxl',
                                  converters={self.year_key: str, self.month_key: str,
                                              self.day_key: str}).dropna(how="all")

    def prep_data(self):
        # prepare data
        if self.success:
            try:
                self.data_preper()
            except Exception as err:
                err_msg = utils.common_err_parser(err)
                self.log_data += "\n Error preparing data: {}".format(err_msg)
                self.success = False

    def data_preper(self):
        pass

    def iterate_rows(self):
        if self.success:
            # iterate over rows
            for row in self.data_dict:
                if self.success:
                    self.row_entered = False
                    try:
                        self.row_parser(row)
                    except Exception as err:
                        err_msg = utils.common_err_parser(err)
                        self.log_data += "Error parsing row: \n"
                        self.log_data += str(row)
                        self.log_data += "\n Error: {}".format(err_msg)
                        self.parsed_row_counter()
                        self.success = False
                    self.rows_parsed += 1
                    if self.row_entered:
                        self.rows_entered += 1

    def row_parser(self, row):
        pass

    def clean_data(self):
        if self.success:
            try:
                self.data_cleaner()
            except Exception as err:
                err_msg = utils.common_err_parser(err)

                self.log_data += "Error parsing common data: \n"
                self.log_data += "\n Error: {}".format(err_msg)
                self.parsed_row_counter()
                self.success = False

            self.parsed_row_counter()
            self.success = True

    def data_cleaner(self):
        pass

    def parsed_row_counter(self):
        self.log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered into database.  " \
                         "\n".format(self.rows_parsed, len(self.data_dict), self.rows_entered, len(self.data_dict))


class GenericIndvParser(DataParser):
    sex_dict = calculation_constants.sex_dict
    pit_key = "PIT"
    sex_key = "Sex"
    len_key = "Length (cm)"
    weight_key = "Weight (g)"
    vial_key = "Vial"
    envelope_key = "Scale Envelope"
    precocity_key = "Precocity (Y/N)"
    mort_key = "Mortality (Y/N)"
    tissue_key = "Tissue Sample (Y/N)"
    start_tank_key = "Origin Pond"
    end_tank_key = "Destination Pond"
    comment_key = "COMMENTS"

    def data_reader(self):
        self.data = pd.read_excel(self.cleaned_data["data_csv"], engine='openpyxl', header=0,
                                  converters={'PIT': str, 'Year': str, 'Month': str, 'Day': str}).dropna(how="all")

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

        if utils.nan_to_none(row[self.sex_key]):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, self.sex_dict[row[self.sex_key]],
                                                  "Gender", None, None)
        self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.len_key], "Length", None)
        self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.weight_key], "Weight", None)
        self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.vial_key], "Vial", None)
        self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, row[self.envelope_key],
                                              "Scale Envelope", None)
        if utils.y_n_to_bool(row[self.precocity_key]):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, None, "Animal Health",
                                                  "Tissue Sample")
        if utils.y_n_to_bool(row[self.mort_key]):
            mort_evnt, mort_anix, mort_entered = utils.enter_mortality(indv, self.cleaned_data, row_date)
            self.row_entered += mort_entered
        if utils.y_n_to_bool(row[self.tissue_key]):
            self.row_entered += utils.enter_indvd(anix.pk, self.cleaned_data, row_date, None, "Animal Health",
                                                  "Tissue Sample")

        if utils.nan_to_none(row[self.start_tank_key]) and utils.nan_to_none(row[self.end_tank_key]):
            in_tank = models.Tank.objects.filter(name=row[self.start_tank_key]).get()
            out_tank = models.Tank.objects.filter(name=row[self.end_tank_key]).get()
            self.row_entered += utils.create_movement_evnt(in_tank, out_tank, self.cleaned_data, row_datetime,
                                                           indv_pk=indv.pk)

        if utils.nan_to_none(row[self.comment_key]):
            comments_parsed, data_entered = utils.comment_parser(row[self.comment_key], anix, row_date)
            self.row_entered += data_entered
            if not comments_parsed:
                self.log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row[self.pit_key],
                                                                                             row[self.comment_key])


def parser_template(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0

    # loading data:
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=1, engine='openpyxl',
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prepare rows before iterating:

    # iterate over rows
    for row in data_dict:
        row_entered = False
        try:
            pass
        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                        " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        rows_parsed += 1
        if row_entered:
            rows_entered += 1

    # enter general data once all rows are entered:
    try:
        pass
    except Exception as err:
        err_msg = utils.common_err_parser(err)

        log_data += "Error parsing common data: \n"
        log_data += "\n Error: {}".format(err_msg)
        log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                    " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        return log_data, False

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def generic_indv_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'PIT': str, 'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # data prep:
    sex_dict = calculation_constants.sex_dict

    for row in data_dict:
        row_entered = 0
        try:
            row_datetime = utils.get_row_date(row)
            row_date = row_datetime.date()

            indv_qs = models.Individual.objects.filter(pit_tag=row["PIT"])
            if len(indv_qs) == 1:
                indv = indv_qs.get()
            else:
                log_data += "Error parsing row: \n"
                log_data += str(row)
                log_data += "\nFish with PIT {} not found in db\n".format(row["PIT"])
                return log_data, False

            anix, anix_entered = utils.enter_anix(cleaned_data, indv_pk=indv.pk)
            row_entered += anix_entered

            if utils.nan_to_none(row["Sex"]):
                row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, sex_dict[row["Sex"]], "Gender",
                                                 None, None)
            row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None)
            row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None)
            row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Vial"], "Vial", None)
            row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, row["Scale Envelope"], "Scale Envelope",
                                             None)
            if utils.y_n_to_bool(row["Precocity (Y/N)"]):
                row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, None, "Animal Health",
                                                 "Tissue Sample")
            if utils.y_n_to_bool(row["Mortality (Y/N)"]):
                mort_evnt, mort_anix, mort_entered = utils.enter_mortality(indv, cleaned_data, row_date)
                row_entered += mort_entered
            if utils.y_n_to_bool(row["Tissue Sample (Y/N)"]):
                row_entered += utils.enter_indvd(anix.pk, cleaned_data, row_date, None, "Animal Health",
                                                 "Tissue Sample")

            if utils.nan_to_none(row["Origin Pond"]) and utils.nan_to_none(row["Destination Pond"]):
                in_tank = models.Tank.objects.filter(name=row["Origin Pond"]).get()
                out_tank = models.Tank.objects.filter(name=row["Destination Pond"]).get()
                row_entered += utils.create_movement_evnt(in_tank, out_tank, cleaned_data, row_datetime,
                                                          indv_pk=indv.pk)

            if utils.nan_to_none(row["COMMENTS"]):
                comments_parsed, data_entered = utils.comment_parser(row["COMMENTS"], anix, row_date)
                row_entered += data_entered
                if not comments_parsed:
                    log_data += "Unparsed comment on row with pit tag {}:\n {} \n\n".format(row["PIT"],
                                                                                            row["COMMENTS"])

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        rows_parsed += 1
        if row_entered:
            rows_entered += 1

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def generic_grp_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                             converters={'Year': str, 'Month': str, 'Day': str}).dropna(how="all")
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False

    # prep data:
    try:
        sex_dict = calculation_constants.sex_dict

        sampc_id = models.SampleCode.objects.filter(name="Individual Sample").get()

        # set date
        data["datetime"] = data.apply(lambda row: utils.get_row_date(row), axis=1)
        # split year-coll
        data["grp_year"] = data.apply(lambda row: utils.year_coll_splitter(row["Year Class"])[0], axis=1)
        data["grp_coll"] = data.apply(lambda row: utils.year_coll_splitter(row["Year Class"])[1], axis=1)

        # set start and end tanks:
        tank_qs = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"])
        tank_dict = {tank.name: tank for tank in tank_qs}
        data["start_tank_id"] = data.apply(lambda row: tank_dict[row["Origin Pond"]], axis=1)
        data["end_tank_id"] = data.apply(lambda row: tank_dict[row["Destination Pond"]], axis=1)

        # set the dict keys for groups
        data["grp_key"] = data["River"] + data["Year Class"] + data["Origin Pond"] + data["Group"].astype(str) + \
                          data["datetime"].astype(str)

        data["end_grp_key"] = data["River"] + data["Year Class"] + data["Destination Pond"] + data["Group"].astype(str) + \
                              data["datetime"].astype(str)

        # create the start_grp dict and enter anixs:
        start_grp_data = data.groupby(["River", "grp_year", "grp_coll", "start_tank_id", "Group", "datetime", "grp_key"],
                                      dropna=False, sort=False).size().reset_index()
        start_grp_data["start_grp_id"] = start_grp_data.apply(
            lambda row: utils.get_grp(row["River"], row["grp_year"], row["grp_coll"],
                                      row["start_tank_id"], at_date=row["datetime"],
                                      prog_str=row["Group"], fail_on_not_found=True)[0], axis=1)
        start_grp_dict = dict(zip(start_grp_data['grp_key'], start_grp_data['start_grp_id']))
        for item, grp in start_grp_dict.items():
            utils.enter_anix(cleaned_data, grp_pk=grp.pk)

        # create the end group dict and create, movement event, groups, counts, contxs, etc. necesarry
        end_grp_data = data.groupby(
            ["River", "grp_year", "grp_coll", "end_tank_id", "start_tank_id", "Group", "datetime", "grp_key",
             "end_grp_key"],
            dropna=False, sort=False).size().reset_index()
        end_grp_dict = {}
        for row in end_grp_data.to_dict('records'):
            grps = utils.get_grp(row["River"], row["grp_year"], row["grp_coll"], row["end_tank_id"],
                                 at_date=row["datetime"],
                                 prog_str=row["Group"])
            start_grp_id = start_grp_dict[row["grp_key"]]
            start_contx = utils.enter_contx(row["start_tank_id"], cleaned_data, None, grp_pk=start_grp_id.pk,
                                            return_contx=True)
            utils.enter_cnt(cleaned_data, sum(end_grp_data[end_grp_data["grp_key"] == row["grp_key"]][0]),
                            start_contx.pk, cnt_code="Fish Removed from Container")

            if len(grps) > 0:
                end_grp_id = grps[0]
                end_grp_dict[row["end_grp_key"]] = grps[0]
            else:
                end_grp_id = copy.deepcopy(start_grp_id)
                end_grp_id.pk = None
                end_grp_id.save()
                end_grp_dict[row["end_grp_key"]] = end_grp_id

            grp_anix = utils.enter_anix(cleaned_data, grp_pk=end_grp_id.pk, return_anix=True)
            utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, "Parent Group", frm_grp_id=start_grp_id)
            utils.enter_grpd(grp_anix.pk, cleaned_data, row["datetime"], None, "Program Group", row["Group"])
            end_contx = utils.create_movement_evnt(row["start_tank_id"], row["end_tank_id"], cleaned_data, row["datetime"],
                                                   grp_pk=end_grp_id.pk, return_end_contx=True)
            utils.enter_cnt(cleaned_data, row[0], end_contx.pk)
    except Exception as err:
        err_msg = utils.common_err_parser(err)
        log_data += "\n Error preparing data and finding initial groups: {}".format(err_msg)
        return log_data, False

    # iterate through the rows:
    data_dict = data.to_dict('records')
    for row in data_dict:
        row_entered = False
        try:
            row_date = row["datetime"].date()
            row_grp = start_grp_dict[row["grp_key"]]
            row_end_grp = end_grp_dict[row["end_grp_key"]]
            if row_end_grp:
                row_grp = row_end_grp
            row_anix, data_entered = utils.enter_anix(cleaned_data, grp_pk=row_grp.pk)
            row_entered += data_entered
            row_samp, data_entered = utils.enter_samp(cleaned_data, row["Sample"], row_grp.spec_id.pk, sampc_id.pk,
                                                      anix_pk=row_anix.pk)
            row_entered += data_entered

            if row_samp:
                if utils.nan_to_none(row["Sex"]):
                    row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, sex_dict[row["Sex"]],
                                                     "Gender", None, None)
                row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row["Length (cm)"], "Length", None)
                row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row["Weight (g)"], "Weight", None)
                row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, row["Vial"], "Vial", None)
                if utils.y_n_to_bool(row["Precocity (Y/N)"]):
                    row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, None, "Animal Health",
                                                     "Tissue Sample")
                if utils.y_n_to_bool(row["Tissue Sample (Y/N)"]):
                    row_entered += utils.enter_sampd(row_samp.pk, cleaned_data, row_date, None, "Animal Health",
                                                     "Tissue Sample")

                row_entered += utils.enter_indvd(row_anix.pk, cleaned_data, row_date, row["Scale Envelope"],
                                                 "Scale Envelope", None)

                if utils.nan_to_none(row["COMMENTS"]):
                    comments_parsed, data_entered = utils.comment_parser(row["COMMENTS"], row_anix, row_date)
                    row_entered += data_entered
                    if not comments_parsed:
                        log_data += "Unparsed comment on row {}:\n {} \n\n".format(row, row["COMMENTS"])

            else:
                break

        except Exception as err:
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err.__str__())
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered,
                                                                           len(data_dict) )
            return log_data, False
        rows_parsed += 1
        if row_entered:
            rows_entered += 1

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True
