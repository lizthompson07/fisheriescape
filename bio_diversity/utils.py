import json
import os
from copy import deepcopy
from datetime import datetime, time
import decimal
import math

import numpy as np
from django.db.models import Q
from django.utils import timezone
from pandas import read_excel
import pytz
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from decimal import Decimal
from django.template.defaulttags import register

from shapely.geometry import shape

from bio_diversity import models, calculation_constants
from bio_diversity.calculation_constants import *
from dm_apps import settings

contx_conts = ["contx_id__cup_id", "contx_id__draw_id", "contx_id__heat_id", "contx_id__tank_id", "contx_id__tray_id",
               "contx_id__trof_id"]

anix_contx_conts = ["anix_id__" + contx_cont for contx_cont in contx_conts]


class DataParser:

    # values to explain the results of parsing
    log_data = "Loading Data Results: \n"
    success = True

    # variables counting progress
    rows_parsed = 0
    rows_entered = 0
    row_entered = False

    # the data
    cleaned_data = {}
    data = None
    data_dict = None

    # standard column headers
    year_key = "Year"
    month_key = "Month"
    day_key = "Day"

    catch_error = Exception

    mandatory_keys = []
    mandatory_filled_keys = []

    header = 1
    comment_row = None
    converters = {year_key: str, month_key: str, day_key: str}
    sheet_name = 0
    """ The data is parsed on initializing. The process is broken into steps run sequentially in init.  Each step
     consists of two functions: a wrapper and a parser. The wrapper (eg. load_data) checks if self.success is still 
     true, catches errors from running the corresponding parser function (eg. data_loader) which should be overwritten 
     for each specific parser."""
    def __init__(self, cleaned_data, autorun=True):
        self.cleaned_data = cleaned_data
        self.mandatory_keys = [self.year_key, self.month_key, self.day_key]
        self.mandatory_filled_keys = [self.year_key, self.month_key, self.day_key]
        if cleaned_data.get("row_start"):
            skip_rows = cleaned_data["row_start"] - 1  # python counts from 0, excel row users do not.
        else:
            skip_rows = 0

        if autorun:
            self.load_data()
            self.prep_data()
            self.iterate_rows(skip_rows)
            self.clean_data()
        else:
            # to run only selection of parser functions
            pass

    def load_data(self):
        try:
            self.data_reader()
            self.data_dict = self.data.to_dict('records')
        except Exception as err:
            self.log_data += "\n File format not valid: {}".format(err.__str__())
            self.success = False

        for header_key in self.mandatory_keys:
            if header_key not in list(self.data):
                # Make sure mandatory key columns exist
                self.log_data += "Column with header \"{}\" not found in worksheet \n Headers should be on " \
                                 "row {}".format(header_key, (self.header + 1))
                self.success = False
        if self.success:
            for key in self.mandatory_filled_keys:
                # make sure mandatory columns are filled
                key_nan_cnt = self.data[key].astype(str).str.fullmatch('nan|none', case=False, na=True).any()
                if key_nan_cnt:
                    self.log_data += "Mandatory column with header \"{}\" has missing values. \n".format(key)
                    self.success = False

        if self.data is None:
            self.log_data += "\n No data in file.  Possible reasons include: incorrect sheet name or incorrect number" \
                             " of lines above the header row, which should be {}.".format(self.header)
            self.success = False

    def data_reader(self):
        self.data = read_excel(self.cleaned_data["data_csv"], header=self.header, skiprows=self.comment_row, engine='openpyxl',
                               converters=self.converters, sheet_name=self.sheet_name)
        self.data = self.data.mask(self.data.eq('None')).dropna(how="all")
        if self.data is None:
            self.success = False
            self.log_data += "\nError loading Data. Check if sheet named: {} exists.".format(self.sheet_name)

    def prep_data(self):
        if self.success:
            try:
                self.data_preper()
            except self.catch_error as err:
                err_msg = common_err_parser(err)
                self.log_data += "\n Error preparing data: {}".format(err_msg)
                self.success = False

    def data_preper(self):
        pass

    def iterate_rows(self, skip_rows=0):
        if self.success:
            for row in self.data_dict:
                if self.success:
                    if self.rows_parsed >= skip_rows:
                        self.row_entered = False
                        try:
                            self.row_parser(row)
                        except self.catch_error as err:
                            err_msg = common_err_parser(err)
                            self.log_data += "\nError:  {} \nError occured when parsing row: \n".format(err_msg)
                            self.log_data += str(row)
                            self.parsed_row_counter()
                            self.success = False
                        self.rows_parsed += 1
                        if self.row_entered:
                            self.rows_entered += 1
                    else:
                        self.rows_parsed += 1

    def row_parser(self, row):
        pass

    def clean_data(self):
        if self.success:
            try:
                self.data_cleaner()
            except self.catch_error as err:
                err_msg = common_err_parser(err)

                self.log_data += "Error parsing common data: \n"
                self.log_data += "\n Error: {}".format(err_msg)
                self.parsed_row_counter()
                self.success = False

            self.parsed_row_counter()

    def data_cleaner(self):
        pass

    def parsed_row_counter(self):
        self.log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered into database.  " \
                         "\n".format(self.rows_parsed, len(self.data_dict), self.rows_entered, len(self.data_dict))

    def team_parser(self, init_str, row, role_id=None, loc_id=None):
        if nan_to_none(init_str):
            perc_list, inits_not_found = team_list_splitter(init_str)
            for perc_id in perc_list:
                self.row_entered += add_team_member(perc_id, self.cleaned_data["evnt_id"], role_id=role_id, loc_id=loc_id)
            for inits in inits_not_found:
                self.log_data += "No valid personnel with initials ({}) on row: \n{}\n".format(inits, row)


def bio_diverisity_authorized(user):
    # return user.is_user and user.groups.filter(name='bio_diversity_user').exists()
    return user.groups.filter(name='bio_diversity_user').exists() or bio_diverisity_admin(user)


def bio_diverisity_admin(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()


def in_bio_diversity_admin_group(user):
    if user:
        return bool(hasattr(user, "bio_user") and user.bio_user.is_admin)


def in_bio_diversity_author_group(user):
    if user:
        return bool(hasattr(user, "bio_user") and (user.bio_user.is_author or user.bio_user.is_admin))


def in_bio_diversity_user_group(user):
    if user:
        return bool(hasattr(user, "bio_user") and (user.bio_user.is_user or user.bio_user.is_admin))


def get_comment_keywords_dict():
    my_dict = {}
    for obj in models.CommentKeywords.objects.all():
        my_dict[obj.keyword] = obj.adsc_id
    return my_dict


def get_help_text_dict(model=None, title=''):
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict


def toggle_help_text_edit(request, user_id):
    usr = models.User.objects.get(pk=user_id)

    user_mode = None
    # mode 1 is read only
    mode = 1
    if models.BioUser.objects.filter(user=usr):
        user_mode = models.BioUser.objects.get(user=usr)
        mode = user_mode.mode

    # fancy math way of toggling between 1 and 2
    mode = (mode % 2) + 1

    if not user_mode:
        user_mode = models.BioUser(user=usr)

    user_mode.mode = mode
    user_mode.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def aware_min():
    return timezone.make_aware(timezone.datetime(1, 1, 1, 0, 0))


def team_list_splitter(team_str, valid_only=True):
    team_str_list = team_str.split(",")
    team_str_list = [indv_str.strip() for indv_str in team_str_list]
    all_perc_qs = models.PersonnelCode.objects.filter(perc_valid=valid_only)
    found_list = []
    not_found_list = []
    for inits in team_str_list:
        perc_qs = all_perc_qs.filter(initials__iexact=inits)
        try:
            found_list.append(perc_qs.get())
        except (MultipleObjectsReturned, ObjectDoesNotExist):
            not_found_list.append(inits)
    return found_list, not_found_list


def year_coll_splitter(full_str):
    try:
        coll = full_str.lstrip(' 0123456789')
        year = int(full_str[:len(full_str) - len(coll)])
    except Exception:
        raise Exception("Collection column must be formated: YYYY AA, where AA is the collection name/acronym.  "
                        "Collction entered: {}".format(full_str))

    return year, coll.strip()


def val_unit_splitter(full_str):
    unit_str = full_str.lstrip(' 0123456789.')
    val = float(full_str[:len(full_str) - len(unit_str)])
    return val, unit_str.strip()


def coll_getter(coll_str):
    coll_str = str(coll_str)
    test_inits = "(" + coll_str.strip() + ")"
    coll_qs = models.Collection.objects.filter(name__icontains=test_inits)
    coll_id = None
    if len(coll_qs) == 1:
        coll_id = coll_qs.get()
    elif len(coll_qs) > 1:
        err_str = ", ".join([coll.name for coll in coll_qs])
        raise Exception("Multiple collections matched to input collection({}): {}".format(coll_str, err_str))
    else:
        coll_qs = models.Collection.objects.filter(name__istartswith=coll_str)
        if len(coll_qs) == 1:
            coll_id = coll_qs.get()
        elif len(coll_qs) > 1:
            err_str = ", ".join([coll.name for coll in coll_qs])
            raise Exception("Multiple collections matched to input collection given({}): {}".format(coll_str, err_str))
        else:
            coll_qs = models.Collection.objects.filter(name__icontains=coll_str)
            if len(coll_qs) == 1:
                coll_id = coll_qs.get()
            elif len(coll_qs) > 1:
                err_str = ", ".join([coll.name for coll in coll_qs])
                raise Exception(
                    "Multiple collections matched to input collection given({}): {}".format(coll_str, err_str))
            else:
                raise Exception("No collection in database matching: {}".format(coll_str))

    return coll_id


def daily_dev(degree_day):
    dev = 100 / math.exp(DEVELOPMENT_ALPHA * math.exp(DEVELOPMENT_BETA * degree_day))
    return dev


def condition_factor(len_cm, weight_g):
    if len_cm is not None and weight_g is not None:
        return 100 * float(weight_g) / (float(len_cm) ** 3)
    else:
        return None


def parse_concentration(concentration_str):
    if "%" in concentration_str:
        return Decimal(float(concentration_str.rstrip("%"))/100)
    elif ":" in concentration_str:
        concentration_str = concentration_str.replace(" ", "")
        concentration_str = concentration_str.replace("1:", "", 1)
        return Decimal(1.0/float(concentration_str))
    else:
        return None


def parse_extra_cols(row, cleaned_data, anix, indv=False, grp=False, samp=False):
    row_date = get_row_date(row)
    row_entered = False
    if indv:
        for adsc_id in cleaned_data["adsc_id"]:
            if y_n_to_bool(row.get(adsc_id.name)):
                row_entered += enter_indvd(anix.pk, cleaned_data, row_date, adsc_id.name,
                                           adsc_id.anidc_id.pk, adsc_str=adsc_id.name)

        for anidc_id in cleaned_data["anidc_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_indvd(anix.pk, cleaned_data, row_date, row.get(anidc_id.name),
                                           anidc_id.pk)

        for anidc_id in cleaned_data["anidc_subj_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_indvd(anix.pk, cleaned_data, row_date, row.get(anidc_id.name),
                                           anidc_id.pk, adsc_str=row.get(anidc_id.name))
    if grp:
        for adsc_id in cleaned_data["adsc_id"]:
            if y_n_to_bool(row.get(adsc_id.name)):
                row_entered += enter_grpd(anix.pk, cleaned_data, row_date, adsc_id.name,
                                          adsc_id.anidc_id.pk, adsc_str=adsc_id.name)

        for anidc_id in cleaned_data["anidc_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_grpd(anix.pk, cleaned_data, row_date, row.get(anidc_id.name),
                                          anidc_id.pk)

        for anidc_id in cleaned_data["anidc_subj_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_grpd(anix.pk, cleaned_data, row_date, row.get(anidc_id.name),
                                          anidc_id.pk, adsc_str=row.get(anidc_id.name))
    if samp:
        samp_pk = anix.pk
        for adsc_id in cleaned_data["adsc_id"]:
            if y_n_to_bool(row.get(adsc_id.name)):
                row_entered += enter_sampd(samp_pk, cleaned_data, row_date, adsc_id.name,
                                           adsc_id.anidc_id.pk, adsc_str=adsc_id.name)

        for anidc_id in cleaned_data["anidc_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_sampd(samp_pk, cleaned_data, row_date, row.get(anidc_id.name),
                                           anidc_id.pk)

        for anidc_id in cleaned_data["anidc_subj_id"]:
            if nan_to_none(row.get(anidc_id.name)):
                row_entered += enter_sampd(samp_pk, cleaned_data, row_date, row.get(anidc_id.name),
                                           anidc_id.pk, adsc_str=row.get(anidc_id.name))

    return row_entered


def parse_cont_strs(cont_str, facic_id, at_date, exclude_str):
    cont_str = cont_str.replace(" ", "")
    if nan_to_none(exclude_str):
        exclude_str = exclude_str.replace(" ", "")
        exclude_list = exclude_str.split("")
    else:
        exclude_list = []
    cont_ids = []
    if "," in cont_str:
        cont_list = cont_str.split(",")
    else:
        cont_list = [cont_str]

    for cont in cont_list:
        if "-" in cont:
            cont_lims = cont.split("-")
            if "." in cont_lims[0]:
                low_conts = cont_lims[0].split(".")
                high_conts = cont_lims[1].split(".")
                low_conts = [int(cont) for cont in low_conts]
                high_conts = [int(cont) for cont in high_conts]
                if len(low_conts) == 3:
                    hu = low_conts[0]
                    drawer = low_conts[1]
                    while hu <= high_conts[0]:
                        draw_qs = models.Drawer.objects.filter(heat_id__facic_id=facic_id, heat_id__name__iexact=hu)
                        cup_qs = models.Cup.objects.filter(draw_id__heat_id__facic_id=facic_id, draw_id__heat_id__name__iexact=hu, start_date__lte=at_date)
                        cup_qs = cup_qs.filter(Q(end_date__gte=at_date) | Q(end_date__isnull=True)).select_related('draw_id')
                        # loop through all drawers in hu:
                        for draw_id in draw_qs:
                            if draw_id.dot_str not in exclude_list:
                                # first cup in drawer:
                                if int(draw_id.name) == low_conts[1] and int(hu) == low_conts[0]:
                                    cup = low_conts[2]
                                else:
                                    cup = 0

                                if int(draw_id.name) >= drawer and (int(draw_id.name) <= high_conts[1] or hu < high_conts[0]):
                                    for cup_id in cup_qs:
                                        if (cup_id.draw_id == draw_id) and int(cup_id.name) >= cup \
                                                and (int(cup_id.name) <= high_conts[2] or
                                                     (hu < high_conts[0] or int(draw_id.name) < high_conts[1])):
                                            if cup_id.dot_str not in exclude_list:
                                                cont_ids.append(cup_id)
                        hu += 1
                        drawer = 0

                else:
                    hu = low_conts[0]
                    drawer = low_conts[1]
                    while hu <= high_conts[0]:
                        draw_qs = models.Drawer.objects.filter(heat_id__facic_id=facic_id, heat_id__name__iexact=hu)
                        for draw_id in draw_qs:
                            if int(draw_id.name) >= drawer and (int(draw_id.name) <= high_conts[1] or hu < high_conts[0]):
                                if draw_id.dot_str not in exclude_list:
                                    cont_ids.append(draw_id)
                        hu += 1
                        drawer = 0
            else:
                cont_range = range(int(cont_lims[0]), int(cont_lims[1]) + 1)
                for tank_name in cont_range:
                    tank_id = models.Tank.objects.filter(name__iexact=tank_name).get()
                    cont_ids.append(tank_id)
        else:
            if "." in cont:
                cont_list = cont.split(".")
                if len(cont_list) == 3:
                    hu, draw, cup = cont_list
                    cup_qs = models.Cup.objects.filter(draw_id__heat_id__facic_id=facic_id, name=cup,
                                                       draw_id__heat_id__name__iexact=hu, start_date__lte=at_date)
                    cup_qs = cup_qs.filter(Q(end_date__gte=at_date) | Q(end_date__isnull=True)).select_related(
                        'draw_id')
                    cont_ids.append(cup_qs.get())
                else:
                    trof, tray = cont_list
                    tray_qs = models.Tray.objects.filter(trof_id__facic_id=facic_id, trof_id__name__iexact=trof,
                                                         start_date__lte=at_date, name=tray)
                    tray_qs = tray_qs.filter(Q(end_date__gte=at_date) | Q(end_date__isnull=True))
                    cont_ids.append(tray_qs.get())
            else:
                tank_id = models.Tank.objects.filter(name__iexact=cont).get()
                cont_ids.append(tank_id)
    return cont_ids


def load_sfas():
    sfa_file_name = os.path.join(settings.BASE_DIR, 'bio_diversity', 'static', "map_layers",
                                 "salmon_fishing_areas.geojson")

    f = open(sfa_file_name,)
    json_sfa = json.load(f)

    sfa_dict = {}
    for feature in json_sfa["features"]:
        sfa_dict[feature["properties"]["SFA"]] = shape(feature["geometry"])
    return sfa_dict


def get_cont_evnt(contx_id):
    # input should be in the form (contx, bool/null)
    output_dict = {"evnt_id": contx_id.evnt_id, "contx_id": contx_id}
    for cont in [contx_id.tank_id, contx_id.cup_id, contx_id.tray_id, contx_id.trof_id, contx_id.draw_id,
                 contx_id.heat_id]:
        if cont:
            output_dict["cont_id"] = cont
            break
    return output_dict


def get_view_cont_list(contx_id):
    # input should be in the form (contx_id)
    output_list = [contx_id.evnt_id.evntc_id.__str__(), contx_id.evnt_id.start_date]
    for cont in [contx_id.tank_id, contx_id.cup_id, contx_id.tray_id, contx_id.trof_id, contx_id.draw_id,
                 contx_id.heat_id]:
        if cont:
            output_list.append(cont)
            break
    return output_list


def get_cont_from_anix(anix, cont_key):
    if cont_key == "tank":
        return anix.contx_id.tank_id
    elif cont_key == "tray":
        return anix.contx_id.tray_id
    elif cont_key == "trof":
        return anix.contx_id.trof_id
    elif cont_key == "cup":
        return anix.contx_id.cup_id
    elif cont_key == "heat":
        return anix.contx_id.heat_id
    elif cont_key == "draw":
        return anix.contx_id.draw_id
    elif cont_key is None:
        all_conts = [anix.contx_id.tank_id, anix.contx_id.tray_id, anix.contx_id.trof_id, anix.contx_id.cup_id, anix.contx_id.heat_id, anix.contx_id.draw_id]
        return [cont for cont in all_conts if cont][0]
    else:
        return None


def get_cont_from_dot(dot_string, cleaned_data, start_date, get_trof=False):
    dot_string = str(dot_string)
    cup = get_cup_from_dot(dot_string, cleaned_data, start_date)
    if cup:
        return cup
    else:
        draw = get_draw_from_dot(dot_string, cleaned_data)
        if draw:
            return draw
        elif get_trof:
            trof_qs = models.Trough.objects.filter(name__icontains=dot_string)
            if len(trof_qs) == 1:
                return trof_qs.get()
            else:
                return None
        else:
            tank_qs = models.Tank.objects.filter(name__icontains=dot_string)
            if len(tank_qs) == 1:
                return tank_qs.get()
            else:
                return None


def get_cup_from_dot(dot_string, cleaned_data, start_date, create_on_not_found=True):
    cont_list = dot_string.split(".")
    if len(cont_list) == 3:
        heat, draw, cup = cont_list
    else:
        return None
    cup_qs = models.Cup.objects.filter(name=cup, draw_id__name=draw, draw_id__heat_id__name=heat, draw_id__heat_id__facic_id=cleaned_data["facic_id"], end_date__isnull=True)
    if cup_qs.exists():
        return cup_qs.get()
    elif create_on_not_found:
        cup_obj = models.Cup(name=cup,
                             start_date=start_date,
                             draw_id=models.Drawer.objects.filter(name=draw, heat_id__name=heat, heat_id__facic_id=cleaned_data["facic_id"]).get(),
                             description_en="Autogenerated by parser",
                             created_by=cleaned_data["created_by"],
                             created_date=cleaned_data["created_date"],
                             )
        try:
            cup_obj.clean()
            cup_obj.save()
        except (ValidationError, IntegrityError):
            return None
        return cup_obj
    else:
        return None


def get_draw_from_dot(dot_string, cleaned_data):
    cont_list = dot_string.split(".")
    if len(cont_list) == 2:
        heat, draw = cont_list
    else:
        return None
    draw_qs = models.Drawer.objects.filter(name=draw, heat_id__name=heat, heat_id__facic_id=cleaned_data["facic_id"])
    if draw_qs.exists():
        return draw_qs.get()
    else:
        return


def get_grp(stock_str, grp_year, coll_str, cont=None, at_date=None, prog_grp=None,
            prog_str=None, grp_mark=None, mark_str=None, fail_on_not_found=False):

    if not at_date:
        at_date = timezone.now().date()
    coll_id = None
    if nan_to_none(coll_str):
        coll_id = coll_getter(coll_str)

    if nan_to_none(cont):
        indv_list, grp_list = cont.fish_in_cont(at_date, select_fields=["anix_id__grp_id__coll_id",
                                                                        "anix_id__grp_id__stok_id"])
        if nan_to_none(stock_str):
            grp_list = [grp for grp in grp_list if grp.stok_id.name == stock_str]
        if nan_to_none(coll_id):
            grp_list = [grp for grp in grp_list if coll_id == grp.coll_id]
        if nan_to_none(grp_year):
            grp_list = [grp for grp in grp_list if grp.grp_year == grp_year]

    else:
        grp_qs = models.Group.objects.all()
        if nan_to_none(stock_str):
            grp_qs = grp_qs.filter(stok_id__name=stock_str)
        if nan_to_none(coll_id):
            grp_qs = grp_qs.filter(coll_id=coll_id)
        if nan_to_none(grp_year):
            grp_qs = grp_qs.filter(grp_year=grp_year)
        grp_list = [grp for grp in grp_qs]

    if nan_to_none(prog_str):
        prog_grp = models.AniDetSubjCode.objects.filter(name__iexact=prog_str).get()

    if nan_to_none(prog_grp) and not (type(prog_grp) == list):
        prog_grp = [prog_grp]

    if nan_to_none(mark_str):
        grp_mark = models.AniDetSubjCode.objects.filter(name__iexact=mark_str).get()

    if prog_grp:
        for prog in prog_grp:
            prog_grp_list = []
            for grp in grp_list:
                if prog in grp.prog_group():
                    prog_grp_list.append(grp)
            grp_list = prog_grp_list.copy()

    if grp_mark:
        mark_grp_list = []
        for grp in grp_list:
            if grp_mark in grp.group_mark():
                mark_grp_list.append(grp)
        grp_list = mark_grp_list.copy()

    final_grp_list = grp_list.copy()

    if len(final_grp_list) == 0 and fail_on_not_found:
        if cont:
            raise Exception("\nGroup {}-{}-{} in container {}, program group {} and mark {} not uniquely found in"
                            " db\n Groups in container are: {}".format(stock_str, grp_year, coll_str, cont.name,
                                                                       prog_str, mark_str, cont.fish_in_cont()[1]))
        else:
            raise Exception("\nGroup {}-{}-{} with program group {} and mark {} not uniquely found in"
                            " db\n".format(stock_str, grp_year, coll_str, prog_str, mark_str))
    return final_grp_list


def get_tray_group(pair_id, tray_id, row_date):
    if pair_id:
        anix_qs = models.AniDetailXref.objects.filter(pair_id=pair_id,
                                                      grp_id__isnull=False).select_related('grp_id')
        grp_list = anix_qs.values_list('grp_id', flat=True).distinct()
        if len(grp_list) == 1:
            grp_id = models.Group.objects.filter(pk=grp_list[0]).get()
        else:
            raise Exception("multiple groups associated with this pairing")
    else:
        grp_list = tray_id.fish_in_cont(row_date, get_grp=True)
        if grp_list:
            grp_id = grp_list[0]
        else:
            raise Exception("No group found in tray {}".format(tray_id.__str__()))
    return grp_id


def get_indv_or_samp(row, pit_key, samp_key, evnt_id):
    log_data = ""
    indv = None
    samp = None
    if nan_to_none(row[pit_key]):
        indv_qs = models.Individual.objects.filter(pit_tag=row[pit_key])
        if len(indv_qs) == 1:
            indv = indv_qs.get()
        else:
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\nFish with PIT {} not found in db\n".format(row[pit_key])
    elif nan_to_none(row[samp_key]):
        samp_qs = models.Sample.objects.filter(samp_num=row[samp_key], anix_id__evnt_id=evnt_id)
        if len(samp_qs) == 1:
            samp = samp_qs.get()
        else:
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\nSample associated with event and with ID {} not found in db\n".format(row[samp_key])

    return indv, samp, log_data


def get_pair(cross_str, stok_id, pair_year, end_date_isnull=True, prog_grp=None, prog_str=None,
             fail_on_not_found=False):

    if nan_to_none(prog_str):
        prog_grp = models.SpawnDetSubjCode.objects.filter(name__iexact=prog_str).get()

    pair_qs = models.Pairing.objects.filter(cross=cross_str, end_date__isnull=end_date_isnull, indv_id__stok_id=stok_id,
                                           start_date__year=pair_year)
    pair_list = [pair for pair in pair_qs]

    prog_pair_list = []
    for pair in pair_list:
        if prog_grp:
            if prog_grp in pair.prog_group():
                prog_pair_list.append(pair)
        else:
            if not pair.prog_group():
                prog_pair_list.append(pair)
    pair_list = prog_pair_list.copy()

    if len(pair_list) == 0 and fail_on_not_found:
        raise Exception("\nPair with cross {}, sotck {}, year {} and with program group {} not uniquely found in"
                        " db\n".format(cross_str, stok_id.name, pair_year, prog_str))
    return pair_list


def set_row_tank(df, cleaned_data, tank_key, col_name="tank_id"):
    tank_qs = models.Tank.objects.filter(facic_id=cleaned_data["facic_id"])
    tank_dict = {tank.name: tank for tank in tank_qs}
    # Set the value of no tank to string of "nan", which can be used as a key to find a group, but fails nan_to_none
    tank_dict[None] = "nan"
    try:
        df[col_name] = df.apply(lambda row: tank_dict[nan_to_none(row[tank_key])], axis=1)
    except KeyError as err:
        raise Exception("Tank {} not found in database".format(err.__str__()))
    return df


def set_row_datetime(df, datetime_key="datetime"):
    df[datetime_key] = df.apply(lambda row: get_row_date(row), axis=1)
    return df


def set_row_grp(df, stok_key, yr_coll_key, prio_key, cont_key, datetime_key, mark_key, grp_col_name="grp_id",
                return_dict=False):
    # function will return a df with a "grp_id" column containing the group associated with the values
    # datetime key must be a datetime object, cont_key must be a cont object
    grp_key = "grp_key"
    grp_year = "grp_year"
    grp_coll = "grp_coll"

    # split year-coll
    df[grp_year] = df.apply(lambda row: year_coll_splitter(row[yr_coll_key])[0], axis=1)
    df[grp_coll] = df.apply(lambda row: year_coll_splitter(row[yr_coll_key])[1], axis=1)

    # set a string on each row to search a dictionary of all groups in df:
    df[grp_key] = df[stok_key].astype(str) + df[yr_coll_key].astype(str) + df[cont_key].astype(str)\
                  + df[prio_key].astype(str) + df[datetime_key].astype(str) + df[mark_key].astype(str)

    # identify all unique groups in the table, grp_data is also a df:
    grp_data = df.groupby([stok_key, grp_year, grp_coll, cont_key, prio_key, datetime_key, mark_key, grp_key],
                          dropna=False, sort=False).size().reset_index()

    # for each row in this smaller df, find the grp_id, and then make a dictionary out of these
    grp_data["grp_id"] = grp_data.apply(lambda row: get_grp(row[stok_key], row[grp_year], row[grp_coll], row[cont_key],
                                                            at_date=row[datetime_key],
                                                            prog_str=nan_to_none(row[prio_key]),
                                                            mark_str=nan_to_none(row[mark_key]),
                                                            fail_on_not_found=True)[0], axis=1)

    grp_dict = dict(zip(grp_data[grp_key], grp_data["grp_id"]))

    df[grp_col_name] = df.apply(lambda row: grp_dict[nan_to_none(row[grp_key])], axis=1)

    if return_dict:
        return df, grp_dict
    else:
        return df


def get_relc_from_point(shapely_geom):
    relc_qs = models.ReleaseSiteCode.objects.all()
    relc_final = None
    for relc in relc_qs:
        # need to add infinitesimal buffer to deal with rounding issue
        if relc.bbox:
            if relc.bbox.buffer(1e-14).intersects(shapely_geom):
                if not relc_final:
                    relc_final = relc
                elif relc.area < relc_final.area:
                    relc_final = relc
    return relc_final


def get_row_date(row, get_time=False):
    try:
        if get_time:
            row_datetime = timezone.make_aware(datetime.strptime(row["Year"] + "-" + row["Month"] + "-" +
                                                                 row["Day"] + "-" + row["Time"], "%Y-%b-%d-%H:%M"))
        else:
            row_datetime = timezone.make_aware(datetime.strptime(row["Year"] + "-" + row["Month"] + "-" + row["Day"],
                                                                 "%Y-%b-%d"))
    except Exception as err:
        raise Exception("\nFailed to parse date from row, make sure column headers are : \"Year\", \"Month\", \"Day\" "
                        "and the format used is: 1999-Jan-1 \n \n {}".format(err))

    return row_datetime


def comment_parser(comment_str, anix_indv, det_date):
    data_entered = False
    com_key_dict = get_comment_keywords_dict()
    parser_list = com_key_dict.keys()
    parsed = False
    for term in parser_list:
        if term.lower() in comment_str.lower():
            parsed = True
            adsc = com_key_dict[term]
            indvd_parsed = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                anidc_id=adsc.anidc_id,
                                                adsc_id=adsc,
                                                qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                detail_date=det_date,
                                                comments=comment_str,
                                                created_by=anix_indv.created_by,
                                                created_date=anix_indv.created_date,
                                                )
            try:
                indvd_parsed.clean()
                indvd_parsed.save()
                data_entered = True
            except (ValidationError, IntegrityError):
                pass

    return parsed, data_entered


def samp_comment_parser(comment_str, cleaned_data, samp_pk, det_date):
    data_entered = False
    com_key_dict = get_comment_keywords_dict()
    parser_list = com_key_dict.keys()
    parsed = False
    for term in parser_list:
        if term.lower() in comment_str.lower():
            parsed = True
            adsc = com_key_dict[term]
            data_entered = enter_sampd(samp_pk, cleaned_data, det_date, adsc.name, adsc.anidc_id.pk, adsc_str=adsc.name)
    return parsed, data_entered


def create_new_evnt(cleaned_data, evntc_name, evnt_date):
    new_cleaned_data = cleaned_data.copy()
    new_evnt = models.Event(evntc_id=models.EventCode.objects.filter(name=evntc_name).get(),
                            facic_id=cleaned_data["evnt_id"].facic_id,
                            perc_id=cleaned_data["evnt_id"].perc_id,
                            prog_id=cleaned_data["evnt_id"].prog_id,
                            start_datetime=evnt_date,
                            end_datetime=evnt_date,
                            created_by=cleaned_data["created_by"],
                            created_date=cleaned_data["created_date"],
                            )
    try:
        new_evnt.clean()
        new_evnt.save()
    except (ValidationError, IntegrityError):
        new_evnt = models.Event.objects.filter(evntc_id=new_evnt.evntc_id,
                                               facic_id=new_evnt.facic_id,
                                               prog_id=new_evnt.prog_id,
                                               start_datetime=new_evnt.start_datetime,
                                               end_datetime=new_evnt.end_datetime,
                                               ).get()

    new_cleaned_data["evnt_id"] = new_evnt
    return new_cleaned_data


def create_feed_evnt(cleaned_data):
    new_evnt = models.Event(evntc_id=models.EventCode.objects.filter(name="Feeding").get(),
                            facic_id=cleaned_data["facic_id"],
                            perc_id=cleaned_data["perc_id"],
                            prog_id=cleaned_data["prog_id"],
                            start_datetime=cleaned_data["feed_date"],
                            end_datetime=cleaned_data["feed_date"],
                            created_by=cleaned_data["created_by"],
                            created_date=cleaned_data["created_date"],
                            )
    try:
        new_evnt.clean()
        new_evnt.save()
    except (ValidationError, IntegrityError):
        new_evnt = models.Event.objects.filter(evntc_id=new_evnt.evntc_id,
                                               facic_id=new_evnt.facic_id,
                                               prog_id=new_evnt.prog_id,
                                               start_datetime=new_evnt.start_datetime,
                                               end_datetime=new_evnt.end_datetime,
                                               ).get()

    return new_evnt


def add_team_member(perc_id, evnt_id, loc_id=None, role_id=None, return_team=False):
    row_entered = False
    team = models.TeamXRef(perc_id=perc_id,
                           evnt_id=evnt_id,
                           loc_id=loc_id,
                           role_id=role_id,
                           created_by=evnt_id.created_by,
                           created_date=evnt_id.created_date,
                           )
    try:
        team.clean()
        team.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        team = models.TeamXRef.objects.filter(perc_id=team.perc_id, evnt_id=team.evnt_id, loc_id=team.loc_id,
                                              role_id=team.role_id).get()
    if return_team:
        return team, row_entered

    return row_entered


def create_tray(trof, tray_name, start_date, cleaned_data, save=True):
    tray = models.Tray(trof_id=trof,
                       name=tray_name,
                       description_en="Auto generated tray",
                       start_date=start_date,
                       created_by=cleaned_data["created_by"],
                       created_date=cleaned_data["created_date"],
                       )
    try:
        if save:
            tray.clean()
            tray.save()
    except (ValidationError, IntegrityError):
        tray = models.Tray.objects.filter(trof_id=tray.trof_id, name=tray.name, start_date=tray.start_date).get()
    return tray


def enter_anix(cleaned_data, indv_pk=None, contx_pk=None, loc_pk=None, pair_pk=None, grp_pk=None, team_pk=None,
               return_sucess=False, return_anix=False):
    row_entered = False
    if any([indv_pk, contx_pk, loc_pk, pair_pk, grp_pk, team_pk]):
        anix = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                    indv_id_id=indv_pk,
                                    contx_id_id=contx_pk,
                                    loc_id_id=loc_pk,
                                    pair_id_id=pair_pk,
                                    grp_id_id=grp_pk,
                                    team_id_id=team_pk,
                                    created_by=cleaned_data["created_by"],
                                    created_date=cleaned_data["created_date"],
                                    )
        try:
            anix.clean()
            anix.save()
            row_entered = True
        except ValidationError:
            anix_qs = models.AniDetailXref.objects.filter(evnt_id=anix.evnt_id,
                                                          indv_id=anix.indv_id,
                                                          contx_id=anix.contx_id,
                                                          loc_id=anix.loc_id,
                                                          pair_id=anix.pair_id,
                                                          grp_id=anix.grp_id,
                                                          team_id=anix.team_id,
                                                          )
            if anix_qs:
                anix = anix_qs.get()
            else:
                raise Exception("Only move individuals/groups once per event.")
        if return_anix:
            return anix
        elif return_sucess:
            return row_entered
        else:
            return anix, row_entered


def enter_anix_contx(tank, cleaned_data):
    if tank:
        contx = models.ContainerXRef(evnt_id=cleaned_data["evnt_id"],
                                     tank_id=tank,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            return contx
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tank=contx.tank_id,
                                                        ).get()

        anix_contx = enter_anix(cleaned_data, contx_pk=contx.pk, return_anix=True)
        return anix_contx


def enter_cnt(cleaned_data, cnt_value, cnt_date, anix_pk=None, loc_pk=None, contx_ref_pk=None,
              cnt_code="Fish in Container", est=False, stok_id=None, coll_id=None, cnt_year=None):
    cnt = False
    entered = False
    if nan_to_none(cnt_value) is None:
        return False, False
    else:
        cnt_value = int(cnt_value)
    if cnt_date is None and loc_pk is not None:
        cnt_date = models.Location.objects.filter(pk=loc_pk).get().loc_date
    if not math.isnan(cnt_value):
        cnt = models.Count(loc_id_id=loc_pk,
                           anix_id_id=anix_pk,
                           contx_ref_id=contx_ref_pk,
                           spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                           cntc_id=models.CountCode.objects.filter(name__iexact=cnt_code).get(),
                           cnt=int(cnt_value),
                           cnt_date=naive_to_aware(cnt_date),
                           coll_id=coll_id,
                           stok_id=stok_id,
                           cnt_year=cnt_year,
                           est=est,
                           created_by=cleaned_data["created_by"],
                           created_date=cleaned_data["created_date"],
                           )
        try:
            cnt.clean()
            cnt.save()
            entered = True
        except ValidationError:
            cnt = models.Count.objects.filter(loc_id=cnt.loc_id, anix_id=cnt.anix_id, cntc_id=cnt.cntc_id,
                                              contx_ref=cnt.contx_ref, cnt_year=cnt.cnt_year, stok_id=cnt.stok_id,
                                              coll_id=cnt.coll_id).get()
            if cnt_code == "Mortality":
                cnt.cnt += 1
                cnt.save()
    return cnt, entered


def enter_cnt_det(cleaned_data, cnt, det_val, det_code, det_subj_code=None, qual="Good"):
    row_entered = False
    # checks for truthness of det_val and if its a nan. Fails for None and nan (nan == nan is false), passes for values
    det_val = nan_to_none(det_val)

    if det_val:
        if type(det_val) != str:
            det_val = round(decimal.Decimal(det_val), 5)
        if not det_subj_code:
            cntd = models.CountDet(cnt_id=cnt,
                                   anidc_id=models.AnimalDetCode.objects.filter(name__iexact=det_code).get(),
                                   det_val=det_val,
                                   qual_id=models.QualCode.objects.filter(name=qual).get(),
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
        else:
            cntd = models.CountDet(cnt_id=cnt,
                                   anidc_id=models.AnimalDetCode.objects.filter(name__iexact=det_code).get(),
                                   adsc_id=models.AniDetSubjCode.objects.filter(name__iexact=det_subj_code).get(),
                                   det_val=det_val,
                                   qual_id=models.QualCode.objects.filter(name=qual).get(),
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
        try:
            cntd.clean()
            cntd.save()
            row_entered = True
        except (ValidationError, IntegrityError):
            row_entered = False

        # update count total if needed:
        if det_code == "Program Group Split":
            new_cnt = sum([float(cnt) for cnt in models.CountDet.objects.filter(anidc_id__name__iexact=det_code,
                                                                                cnt_id=cnt).values_list('det_val',
                                                                                                        flat=True)])
            if new_cnt > cnt.cnt:
                cnt.cnt = int(new_cnt)
                cnt.save()
                row_entered = True

    return row_entered


def enter_env(env_value, env_date, cleaned_data, envc_id, envsc_id=None, loc_id=None, contx=None, inst_id=None,
              env_time=None, avg=False, save=True, qual_id=False):

    row_entered = False
    if not env_time:
        env_time = aware_min().time()

    if not nan_to_none(env_value):
        return False
    env_datetime = naive_to_aware(env_date, env_time)

    if not qual_id:
        qual_id = models.QualCode.objects.filter(name="Good").get()

    if envsc_id:
        env = models.EnvCondition(contx_id=contx,
                                  loc_id=loc_id,
                                  envc_id=envc_id,
                                  envsc_id=envsc_id,
                                  inst_id=inst_id,
                                  env_val=None,
                                  env_avg=avg,
                                  start_datetime=env_datetime,
                                  qual_id=qual_id,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    else:
        env = models.EnvCondition(contx_id=contx,
                                  loc_id=loc_id,
                                  envc_id=envc_id,
                                  inst_id=inst_id,
                                  env_val=str(env_value),
                                  env_avg=avg,
                                  start_datetime=env_datetime,
                                  qual_id=qual_id,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    if save:
        try:
            env.clean()
            env.save()
            row_entered = True
        except (ValidationError, IntegrityError):
            pass
        return row_entered
    else:
        try:
            env.clean()
            return env
        except (ValidationError, IntegrityError):
            return None


def enter_feed(cleaned_data, contx_id, feedc_id, feedm_id, amt, comments=None, freq=None, lot_num=None):
    feed = models.Feeding(contx_id=contx_id,
                          feedm_id=feedm_id,
                          feedc_id=feedc_id,
                          lot_num=lot_num,
                          amt=amt,
                          freq=freq,
                          unit_id=models.UnitCode.objects.filter(name="Feed Size").get(),
                          comments=nan_to_none(comments),
                          created_by=cleaned_data["created_by"],
                          created_date=cleaned_data["created_date"],
                          )
    try:
        feed.clean()
        feed.save()
        row_entered = True
    except (ValidationError, IntegrityError) as err:
        raise Exception("Feeding not entered: {}".format(err))
    return row_entered


def enter_grpd(anix_pk, cleaned_data, det_date, det_value, anidc_pk, anidc_str=None, adsc_str=None, frm_grp_id=None,
               comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if anidc_str:
        anidc_pk = models.AnimalDetCode.objects.filter(name=anidc_str).get().pk

    if adsc_str:
        grpd = models.GroupDet(anix_id_id=anix_pk,
                               anidc_id_id=anidc_pk,
                               adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                               frm_grp_id=frm_grp_id,
                               det_val=det_value,
                               detail_date=det_date,
                               qual_id=models.QualCode.objects.filter(name="Good").get(),
                               comments=comments,
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
    else:
        grpd = models.GroupDet(anix_id_id=anix_pk,
                               anidc_id_id=anidc_pk,
                               frm_grp_id=frm_grp_id,
                               det_val=det_value,
                               detail_date=det_date,
                               qual_id=models.QualCode.objects.filter(name="Good").get(),
                               comments=comments,
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
    try:
        grpd.clean()
        grpd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_indvd(anix_pk, cleaned_data, det_date, det_value, anidc_pk, anidc_str=None, adsc_str=None, comments=None):
    row_entered = False
    det_date = naive_to_aware(det_date)
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False

    if anidc_str:
        anidc_pk = models.AnimalDetCode.objects.filter(name=anidc_str).get().pk

    if adsc_str:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id_id=anidc_pk,
                                     adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                                     det_val=det_value,
                                     detail_date=det_date,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     comments=comments,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    else:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id_id=anidc_pk,
                                     det_val=det_value,
                                     detail_date=det_date,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     comments=comments,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    try:
        indvd.clean()
        indvd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_bulk_indvd(anix_pk, cleaned_data, det_date, len_val=None, len_mm=None, weight=None, weight_kg=None, vial=None,
                     scale_envelope=None, gender=None, tissue_yn=None, status=None, mark=None, prog_grp=None,
                     vaccinated=None, lifestage=None, cryo_out=None, o_fluid_out=None, comments=None):
    data_entered = 0
    if nan_to_none(len_val):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, len_val, len_anidc_id.pk, None)
    if nan_to_none(len_mm):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, 0.1 * len_mm, len_anidc_id.pk, None)
    if nan_to_none(weight):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, weight, weight_anidc_id.pk, None)
    if nan_to_none(weight_kg):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, weight_kg * 1000, weight_anidc_id.pk, None)
    if nan_to_none(vial):
        vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, vial, vial_anidc_id.pk, None)
    if nan_to_none(scale_envelope):
        envelope_anidc_id = models.AnimalDetCode.objects.filter(name="Scale Envelope").get()
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, scale_envelope, envelope_anidc_id.pk, None)
    if nan_to_none(gender):
        sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        func_sex_dict = calculation_constants.sex_dict
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, func_sex_dict[gender.upper()],
                                    sex_anidc_id.pk, adsc_str=func_sex_dict[gender.upper()])
    if nan_to_none(status):
        status_anidc_pk = models.AnimalDetCode.objects.filter(name="Status").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, status, status_anidc_pk, adsc_str=status)
    if nan_to_none(mark):
        mark_anidc_pk = models.AnimalDetCode.objects.filter(name="Mark").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, mark, mark_anidc_pk, adsc_str=mark)
    if nan_to_none(lifestage):
        lifestage_anidc_pk = models.AnimalDetCode.objects.filter(name="Lifestage").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, lifestage, lifestage_anidc_pk, adsc_str=lifestage)
    if nan_to_none(cryo_out):
        if y_n_to_bool(cryo_out):
            cryo_anidc_pk = models.AnimalDetCode.objects.filter(name="Cryo Milt Taken").get().pk
            data_entered += enter_indvd(anix_pk, cleaned_data, det_date, None, cryo_anidc_pk, None)
    if nan_to_none(o_fluid_out):
        if y_n_to_bool(o_fluid_out):
            o_fluid_anidc_pk = models.AnimalDetCode.objects.filter(name="Ovarian Fluid Taken").get().pk
            data_entered += enter_indvd(anix_pk, cleaned_data, det_date, None, o_fluid_anidc_pk, None)
    if nan_to_none(prog_grp):
        prog_anidc_pk = models.AnimalDetCode.objects.filter(name="Program Group").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, prog_grp, prog_anidc_pk, adsc_str=prog_grp)
    if nan_to_none(vaccinated):
        vax_anidc_pk = models.AnimalDetCode.objects.filter(name="Vaccination").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, vaccinated, vax_anidc_pk, adsc_str=vaccinated)
    if nan_to_none(tissue_yn):
        if y_n_to_bool(tissue_yn):
            tissue_anidc_pk = models.AnimalDetCode.objects.filter(name="Tissue Sample").get().pk
            data_entered += enter_indvd(anix_pk, cleaned_data, det_date, None, tissue_anidc_pk, None)

    if nan_to_none(comments):
        comment_anidc_pk = models.AnimalDetCode.objects.filter(name="Comment").get().pk
        data_entered += enter_indvd(anix_pk, cleaned_data, det_date, None, comment_anidc_pk, comments=comments)

    return data_entered


def enter_bulk_grpd(anix_pk, cleaned_data, det_date, len_val=None, len_mm=None, weight=None, weight_kg=None,
                    status=None, mark=None, prnt_grp=None, prog_grp=None, vaccinated=None, lifestage=None,
                    comments=None):
    data_entered = 0
    if nan_to_none(len_val):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, len_val, len_anidc_id.pk, None)
    if nan_to_none(len_mm):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, 0.1 * len_mm, len_anidc_id.pk, None)
    if nan_to_none(weight):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, weight, weight_anidc_id.pk, None)
    if nan_to_none(weight_kg):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, weight_kg * 1000, weight_anidc_id.pk, None)

    if nan_to_none(status):
        status_anidc_pk = models.AnimalDetCode.objects.filter(name="Status").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, status,
                                   status_anidc_pk, adsc_str=status)
    if nan_to_none(mark):
        mark_anidc_pk = models.AnimalDetCode.objects.filter(name="Mark").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, mark,
                                   mark_anidc_pk, adsc_str=mark)
    if nan_to_none(lifestage):
        lifestage_anidc_pk = models.AnimalDetCode.objects.filter(name="Lifestage").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, lifestage,
                                   lifestage_anidc_pk, adsc_str=lifestage)
    if nan_to_none(prog_grp):
        prog_anidc_pk = models.AnimalDetCode.objects.filter(name="Program Group").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, prog_grp,
                                   prog_anidc_pk, adsc_str=prog_grp)
    if nan_to_none(prnt_grp):
        prnt_grp_anidc_pk = models.AnimalDetCode.objects.filter(name="Parent Group").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, prnt_grp.__str__(),
                                   prnt_grp_anidc_pk, frm_grp_id=prnt_grp)
    if nan_to_none(vaccinated):
        vax_anidc_pk = models.AnimalDetCode.objects.filter(name="Vaccination").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, vaccinated,
                                   vax_anidc_pk, adsc_str=vaccinated)

    if nan_to_none(comments):
        comment_anidc_pk = models.AnimalDetCode.objects.filter(name="Comment").get().pk
        data_entered += enter_grpd(anix_pk, cleaned_data, det_date, None, comment_anidc_pk, comments=comments)

    return data_entered


def enter_bulk_sampd(samp_pk, cleaned_data, det_date, len_val=None, len_mm=None, weight=None, weight_kg=None, vial=None,
                     scale_envelope=None, gender=None, tissue_yn=None, status=None, mark=None, prog_grp=None,
                     vaccinated=None, lifestage=None, cryo_out=None, o_fluid_out=None, comments=None):
    data_entered = 0
    if nan_to_none(len_val):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, len_val, len_anidc_id.pk, None)
    if nan_to_none(len_mm):
        len_anidc_id = models.AnimalDetCode.objects.filter(name="Length").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, 0.1 * len_mm, len_anidc_id.pk, None)
    if nan_to_none(weight):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, weight, weight_anidc_id.pk, None)
    if nan_to_none(weight_kg):
        weight_anidc_id = models.AnimalDetCode.objects.filter(name="Weight").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, weight_kg * 1000, weight_anidc_id.pk, None)
    if nan_to_none(vial):
        vial_anidc_id = models.AnimalDetCode.objects.filter(name="Vial").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, vial, vial_anidc_id.pk, None)
    if nan_to_none(scale_envelope):
        envelope_anidc_id = models.AnimalDetCode.objects.filter(name="Scale Envelope").get()
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, scale_envelope, envelope_anidc_id.pk, None)
    if nan_to_none(gender):
        sex_anidc_id = models.AnimalDetCode.objects.filter(name="Gender").get()
        func_sex_dict = calculation_constants.sex_dict
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, func_sex_dict[gender.upper()], sex_anidc_id.pk,
                                    adsc_str=func_sex_dict[gender.upper()])
    if nan_to_none(status):
        status_anidc_pk = models.AnimalDetCode.objects.filter(name="Status").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, status,
                                    status_anidc_pk, adsc_str=status)
    if nan_to_none(mark):
        mark_anidc_pk = models.AnimalDetCode.objects.filter(name="Mark").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, mark,
                                    mark_anidc_pk, adsc_str=mark)
    if nan_to_none(lifestage):
        lifestage_anidc_pk = models.AnimalDetCode.objects.filter(name="Lifestage").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, lifestage,
                                    lifestage_anidc_pk, adsc_str=lifestage)
    if nan_to_none(prog_grp):
        prog_anidc_pk = models.AnimalDetCode.objects.filter(name="Program Group").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, prog_grp,
                                    prog_anidc_pk, adsc_str=prog_grp)
    if nan_to_none(vaccinated):
        vax_anidc_pk = models.AnimalDetCode.objects.filter(name="Vaccination").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, vaccinated,
                                    vax_anidc_pk, adsc_str=vaccinated)
    if nan_to_none(tissue_yn):
        if y_n_to_bool(tissue_yn):
            tissue_anidc_pk = models.AnimalDetCode.objects.filter(name="Tissue Samp").get().pk
            data_entered += enter_sampd(samp_pk, cleaned_data, det_date, None, tissue_anidc_pk, None)
    if nan_to_none(cryo_out):
        if y_n_to_bool(cryo_out):
            cryo_anidc_pk = models.AnimalDetCode.objects.filter(name="Cryo Milt Taken").get().pk
            data_entered += enter_sampd(samp_pk, cleaned_data, det_date, None, cryo_anidc_pk, None)
    if nan_to_none(o_fluid_out):
        if y_n_to_bool(o_fluid_out):
            o_fluid_anidc_pk = models.AnimalDetCode.objects.filter(name="Ovarian Fluid Taken").get().pk
            data_entered += enter_sampd(samp_pk, cleaned_data, det_date, None, o_fluid_anidc_pk, None)
    if nan_to_none(comments):
        comment_anidc_pk = models.AnimalDetCode.objects.filter(name="Comment").get().pk
        data_entered += enter_sampd(samp_pk, cleaned_data, det_date, None, comment_anidc_pk, comments=comments)

    return data_entered


def enter_indvt(anix_pk, cleaned_data, treat_datetime, dose, indvtc_pk, treat_endtime=None, lot_num=None, unit_id=None):
    row_entered = False
    if isinstance(dose, float):
        if math.isnan(dose):
            return False

    indvt = models.IndTreatment(anix_id_id=anix_pk,
                                indvtc_id_id=indvtc_pk,
                                lot_num=lot_num,
                                dose=dose,
                                start_datetime=treat_datetime,
                                end_datetime=treat_endtime,
                                unit_id=unit_id,
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"],
                                )
    try:
        indvt.clean()
        indvt.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_locd(loc_pk, cleaned_data, det_date, det_value, locdc_pk, ldsc_str=None, comments=None):
    row_entered = False
    if nan_to_none(det_value):
        return False

    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if ldsc_str:
        locd = models.LocationDet(loc_id_id=loc_pk,
                                  locdc_id_id=locdc_pk,
                                  ldsc_id=models.LocDetSubjCode.objects.filter(name=ldsc_str).get(),
                                  det_val=det_value,
                                  detail_date=det_date,
                                  qual_id=models.QualCode.objects.filter(name="Good").get(),
                                  comments=comments,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    else:
        locd = models.LocationDet(loc_id_id=loc_pk,
                                  locdc_id_id=locdc_pk,
                                  det_val=det_value,
                                  detail_date=det_date,
                                  qual_id=models.QualCode.objects.filter(name="Good").get(),
                                  comments=comments,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    try:
        locd.clean()
        locd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_mortality(indv, cleaned_data, mort_date):
    # enter indvd
    # record indvd on indv
    # remove indv from container
    data_entered = False
    mort_date = naive_to_aware(mort_date)

    mort_anidc = models.AnimalDetCode.objects.filter(name="Mortality Observation").get()

    anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv.pk)
    data_entered += enter_indvd(anix.pk, cleaned_data, mort_date, None, mort_anidc.pk)
    data_entered += anix_entered
    for cont in indv.current_cont(at_date=mort_date):
        data_entered += enter_move(cleaned_data, cont, None, mort_date, indv_pk=indv.pk, mort=True, return_sucess=True)

    indv.indv_valid = False
    indv.save()

    return anix, data_entered


def enter_samp_mortality(samp_id, cleaned_data, mort_date):
    # add sampd
    # record counts on group
    data_entered = False
    mort_date = naive_to_aware(mort_date)
    mort_anidc = models.AnimalDetCode.objects.filter(name="Mortality Observation").get()
    data_entered += enter_sampd(samp_id.pk, cleaned_data, mort_date, None, mort_anidc.pk)
    samp_contx_id = samp_id.anix_id.contx_id
    # one count per samp per mortality event, count up similar sample details:
    cnt_val = models.SampleDet.objects.filter(anidc_id=mort_anidc,
                                              samp_id__anix_id__evnt_id=cleaned_data["evnt_id"],
                                              samp_id__anix_id__grp_id=samp_id.anix_id.grp_id,
                                              ).distinct().count()

    cnt, cnt_entered = enter_cnt(cleaned_data, 0, mort_date, samp_id.anix_id.pk, cnt_code="Mortality")
    data_entered += cnt_entered
    cnt.cnt = cnt_val
    cnt.save()
    return data_entered


def enter_grp_mortality(grp, cleaned_data, mort_date, mort_cnt, cont=None):
    # add grdp
    # link to cont
    # record counts on group
    data_entered = False
    mort_date = naive_to_aware(mort_date)
    mort_anidc = models.AnimalDetCode.objects.filter(name="Mortality Observation").get()

    if not cont:
        cont = grp.current_cont(at_date=cleaned_data["mort_date"])[0]

    contx_id, contx_entered = enter_contx(cont, cleaned_data, return_contx=True)
    data_entered += contx_entered

    anix_id, anix_entered = enter_anix(cleaned_data, grp_pk=grp.pk, contx_pk=contx_id.pk)
    data_entered += anix_entered

    data_entered += enter_grpd(anix_id.pk, cleaned_data, mort_date, mort_cnt, mort_anidc.pk)

    # one detail per day, per group, per event, count up det_val from similar details:
    mort_cnt = sum(models.GroupDet.objects.filter(anidc_id=mort_anidc,
                                                  anix_id__evnt_id=cleaned_data["evnt_id"],
                                                  anix_id__grp_id=grp,
                                                  anix_id__contx_id=contx_id,
                                                  detail_date=mort_date,
                                                  ).distinct().values_list('det_val', flat=True))

    cnt, cnt_entered = enter_cnt(cleaned_data, 0, mort_date, anix_id.pk, cnt_code="Mortality")
    data_entered += cnt_entered
    cnt.cnt = mort_cnt
    cnt.save()

    return data_entered


def enter_samp(cleaned_data, samp_num, spec_pk, sampc_pk, anix_pk=None, loc_pk=None, comments=None):
    samp_entered = False
    samp = models.Sample(anix_id_id=anix_pk,
                         loc_id_id=loc_pk,
                         spec_id_id=spec_pk,
                         samp_num=samp_num,
                         sampc_id_id=sampc_pk,
                         comments=comments,
                         created_by=cleaned_data["created_by"],
                         created_date=cleaned_data["created_date"],
                         )
    try:
        samp.clean()
        samp.save()
        samp_entered = True
    except (ValidationError, IntegrityError):
        samp = models.Sample.objects.filter(anix_id=samp.anix_id,
                                            loc_id=samp.loc_id,
                                            spec_id=samp.spec_id,
                                            samp_num=samp.samp_num,
                                            sampc_id=samp.sampc_id,
                                            ).get()

    return samp, samp_entered


def enter_sampd(samp_pk, cleaned_data, det_date, det_value, anidc_pk, anidc_str=None, adsc_str=None, comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if anidc_str:
        anidc_pk = models.AnimalDetCode.objects.filter(name=anidc_str).get().pk
    if adsc_str:
        sampd = models.SampleDet(samp_id_id=samp_pk,
                                 anidc_id_id=anidc_pk,
                                 adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                                 det_val=adsc_str,
                                 detail_date=det_date,
                                 qual_id=models.QualCode.objects.filter(name="Good").get(),
                                 comments=comments,
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
    else:
        sampd = models.SampleDet(samp_id_id=samp_pk,
                                 anidc_id_id=anidc_pk,
                                 det_val=det_value,
                                 detail_date=det_date,
                                 qual_id=models.QualCode.objects.filter(name="Good").get(),
                                 comments=comments,
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
    try:
        sampd.clean()
        sampd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_spwnd(pair_pk, cleaned_data, det_value, spwndc_pk, spwnsc_str, qual_code="Good", comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if spwnsc_str:
        spwnd = models.SpawnDet(pair_id_id=pair_pk,
                                spwndc_id_id=spwndc_pk,
                                spwnsc_id=models.SpawnDetSubjCode.objects.filter(name=spwnsc_str).get(),
                                det_val=det_value,
                                qual_id=models.QualCode.objects.filter(name=qual_code).get(),
                                comments=comments,
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"],
                                )
    else:
        spwnd = models.SpawnDet(pair_id_id=pair_pk,
                                spwndc_id_id=spwndc_pk,
                                det_val=det_value,
                                qual_id=models.QualCode.objects.filter(name=qual_code).get(),
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"],
                                )
    try:
        spwnd.clean()
        spwnd.save()
        row_entered = True
    except ValidationError:
        pass
    return row_entered


def enter_move(cleaned_data, origin_id, destination_id, move_date, indv_pk=None, grp_pk=None, loc_pk=None, mort=None,
               set_origin_if_none=True, return_sucess=False):
    # cases:
    # origin == destination / no desitination
    # origin is none
    # origin != destination
    row_entered = False
    start_anix = None
    end_anix = None
    origin_conts = None

    # link indv/grp to evnt regardless:
    anix_id, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, loc_pk=loc_pk)
    row_entered += anix_entered

    if (origin_id == destination_id) or (nan_to_none(destination_id) is None and loc_pk is None and mort is None):
        # no movement, link indv/grp to cont:
        # destination is set
        anix, contx, contx_entered = enter_contx(origin_id, cleaned_data, return_anix=True,
                                                 indv_pk=indv_pk, grp_pk=grp_pk)
        row_entered += contx_entered
        if return_sucess:
            return row_entered
        else:
            return anix, anix, row_entered
    elif nan_to_none(destination_id) is None and (loc_pk or mort):
        end_contx_pk = None
    else:
        # destination is set
        end_anix, end_contx, contx_entered = enter_contx(destination_id, cleaned_data, return_anix=True,
                                                         indv_pk=indv_pk, grp_pk=grp_pk)
        row_entered += contx_entered
        end_contx_pk = end_contx.pk

    if nan_to_none(origin_id):
        origin_conts = [origin_id]
    elif set_origin_if_none:
        if indv_pk:
            indv = models.Individual.objects.filter(pk=indv_pk).get()
            origin_conts = indv.current_cont(move_date)
        if grp_pk:
            grp = models.Group.objects.filter(pk=grp_pk).get()
            origin_conts = grp.current_cont(move_date)
        if not origin_conts or loc_pk:
            origin_conts = [None]
    else:
        origin_conts = [None]

    for origin in origin_conts:
        if origin == destination_id:
            pass
        else:
            if origin:
                start_anix, start_contx, contx_entered = enter_contx(origin, cleaned_data, return_anix=True,
                                                                     indv_pk=indv_pk, grp_pk=grp_pk)
                row_entered += contx_entered
                start_contx_pk = start_contx.pk
            else:
                start_contx_pk = None

            move_id = models.MoveDet(anix_id=anix_id,
                                     contx_start_id=start_contx_pk,
                                     contx_end_id=end_contx_pk,
                                     move_date=move_date,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
            try:
                move_id.clean()
                move_id.save()
                row_entered = True
            except (ValidationError, IntegrityError) as err:
                pass

    if return_sucess:
        return row_entered
    else:
        return start_anix, end_anix, row_entered


def enter_move_cnts(cleaned_data, origin_id, destination_id, move_date, nfish=None, start_grp_id=None, end_grp_id=None,
                    whole_grp=True, set_origin_if_none=True):
    # end group is move group
    # 4 cases: whole group yes/no, fish at destination yes/no
    # split fish off main group:
    # adding fish to existing group
    start_cnt = None
    end_cnt = None
    data_entered = False

    if start_grp_id is None:
        raise Exception("Must specify a start group")

    if end_grp_id and end_grp_id != start_grp_id:
        end_grp_anix, contx, row_entered = enter_contx(destination_id, cleaned_data, grp_pk=end_grp_id.pk,
                                                       return_anix=True)
        data_entered += enter_bulk_grpd(end_grp_anix, cleaned_data, move_date, prnt_grp=start_grp_id)

        if whole_grp:
            # combine groups, record count and deactivate start group
            start_anix, end_anix, data_entered = enter_move(cleaned_data, origin_id, destination_id, move_date,
                                                            grp_pk=start_grp_id.pk,
                                                            set_origin_if_none=set_origin_if_none)

            start_grp_id.grp_end_date = move_date
            start_grp_id.save()

            if nfish:
                end_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, end_grp_anix.pk,
                                                 contx_ref_pk=start_anix.contx_id.pk,
                                                 cnt_code="Fish added to container")
                data_entered += cnt_entered
        else:
            # just record counts:
            start_cnt_anix, contx, row_entered = enter_contx(origin_id, cleaned_data, grp_pk=start_grp_id.pk,
                                                             return_anix=True)
            start_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, start_cnt_anix.pk,
                                               contx_ref_pk=end_grp_anix.contx_id.pk,
                                               cnt_code="Fish removed from container")
            data_entered += cnt_entered
            end_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, end_grp_anix.pk,
                                             contx_ref_pk=start_cnt_anix.contx_id.pk,
                                             cnt_code="Fish added to container")
            data_entered += cnt_entered

    else:  # no group at destination:
        if whole_grp:
            # whole group moves, record count
            start_anix, end_anix, data_entered = enter_move(cleaned_data, origin_id, destination_id, move_date,
                                                            grp_pk=start_grp_id.pk,
                                                            set_origin_if_none=set_origin_if_none)
            if nfish:
                end_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, end_anix.pk,
                                                 contx_ref_pk=start_anix.contx_id.pk,
                                                 cnt_code="Fish Count")
                data_entered += cnt_entered
        else:
            # split off new group from start group, record counts:
            new_end_grp = copy_grp(start_grp_id, move_date, cleaned_data)
            start_anix, end_anix, data_entered = enter_move(cleaned_data, origin_id, destination_id, move_date,
                                                            grp_pk=new_end_grp.pk,
                                                            set_origin_if_none=set_origin_if_none)
            if nfish:
                start_cnt_anix, contx, row_entered = enter_contx(origin_id, cleaned_data, grp_pk=start_grp_id.pk,
                                                                 return_anix=True)
                start_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, start_cnt_anix.pk,
                                                   contx_ref_pk=end_anix.contx_id.pk,
                                                   cnt_code="Fish removed from container")
                data_entered += cnt_entered
                end_cnt, cnt_entered = enter_cnt(cleaned_data, nfish, move_date, end_anix.pk,
                                                 contx_ref_pk=start_anix.contx_id.pk,
                                                 cnt_code="Fish added to container")
                data_entered += cnt_entered

    return start_cnt, end_cnt, data_entered


def copy_grp(in_grp_id, copy_date, cleaned_data):
    new_grp = deepcopy(in_grp_id)
    new_grp.pk = None
    new_grp.clean()
    new_grp.save()

    prog_grp_list = in_grp_id.prog_group()
    grp_mark_list = in_grp_id.group_mark()
    anix = enter_anix(cleaned_data, grp_pk=new_grp.pk, return_anix=True)
    for prog_id in prog_grp_list:
        enter_bulk_grpd(anix.pk, cleaned_data, copy_date, prog_grp=prog_id.name)
    for mark_id in grp_mark_list:
        enter_bulk_grpd(anix.pk, cleaned_data, copy_date, mark=mark_id.name)
    enter_bulk_grpd(anix.pk, cleaned_data, copy_date, prnt_grp=in_grp_id)
    return new_grp


def enter_contx(cont, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False, return_anix=False):
    cont_type = type(cont)
    if cont_type == models.Tank:
        return enter_tank_contx(cont.name, cleaned_data,indv_pk, grp_pk, team_pk, return_contx, return_anix)
    elif cont_type == models.Trough:
        return enter_trof_contx(cont.name, cleaned_data,indv_pk, grp_pk, team_pk, return_contx, return_anix)
    elif cont_type == models.Tray:
        return enter_tray_contx(cont, cleaned_data, indv_pk, grp_pk, team_pk, return_contx, return_anix)
    elif cont_type == models.Cup:
        return enter_cup_contx(cont, cleaned_data, indv_pk, grp_pk, team_pk, return_contx, return_anix)
    elif cont_type == models.Drawer:
        return enter_draw_contx(cont, cleaned_data, indv_pk, grp_pk, team_pk, return_contx, return_anix)
    elif cont_type == models.HeathUnit:
        return enter_heat_contx(cont, cleaned_data, indv_pk, grp_pk, team_pk, return_contx, return_anix)


def enter_tank_contx(tank_name, cleaned_data,  indv_pk=None, grp_pk=None, team_pk=None, return_contx=False,
                     return_anix=False):
    row_entered = False
    anix = None
    if not tank_name == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     tank_id=models.Tank.objects.filter(name=tank_name,
                                                                        facic_id=cleaned_data["facic_id"]).get(),
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tank_id=contx.tank_id,
                                                        tray_id__isnull=True,
                                                        cup_id__isnull=True,
                                                        trof_id__isnull=True,
                                                        draw_id__isnull=True,
                                                        heat_id__isnull=True,
                                                        team_id=contx.team_id).get()
        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk, )
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def enter_trof_contx(trof_name, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False,
                     return_anix=False):
    row_entered = False
    if not trof_name == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     trof_id=models.Trough.objects.filter(name=trof_name,
                                                                          facic_id=cleaned_data["facic_id"]).get(),
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        trof_id=contx.trof_id,
                                                        tray_id__isnull=True,
                                                        tank_id__isnull=True,
                                                        cup_id__isnull=True,
                                                        draw_id__isnull=True,
                                                        heat_id__isnull=True,
                                                        team_id=contx.team_id).get()
        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk)
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def enter_tray_contx(tray, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False,
                     return_anix=False):
    row_entered = False
    if not tray == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     tray_id=tray,
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tray_id=contx.tray_id,
                                                        cup_id__isnull=True,
                                                        tank_id__isnull=True,
                                                        trof_id__isnull=True,
                                                        draw_id__isnull=True,
                                                        heat_id__isnull=True,
                                                        team_id=contx.team_id).get()
        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk)
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def enter_cup_contx(cup, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False, return_anix=False):
    row_entered = False
    if not cup == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     cup_id=cup,
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        cup_id=contx.cup_id,
                                                        tray_id__isnull=True,
                                                        tank_id__isnull=True,
                                                        trof_id__isnull=True,
                                                        draw_id__isnull=True,
                                                        heat_id__isnull=True,
                                                        team_id=contx.team_id).get()

        draw_contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                          draw_id=cup.draw_id,
                                          created_by=cleaned_data["created_by"],
                                          created_date=cleaned_data["created_date"],
                                          )
        try:
            draw_contx.clean()
            draw_contx.save()
            row_entered = True
        except ValidationError:
            pass

        heat_contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                          heat_id=cup.draw_id.heat_id,
                                          created_by=cleaned_data["created_by"],
                                          created_date=cleaned_data["created_date"],
                                          )
        try:
            heat_contx.clean()
            heat_contx.save()
            row_entered = True
        except ValidationError:
            pass

        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk,
                                            )
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def enter_draw_contx(draw, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False,
                     return_anix=False):
    row_entered = False
    if draw:
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     draw_id=draw,
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        draw_id=contx.draw_id,
                                                        tray_id__isnull=True,
                                                        tank_id__isnull=True,
                                                        trof_id__isnull=True,
                                                        cup_id__isnull=True,
                                                        heat_id__isnull=True,
                                                        team_id=contx.team_id).get()

        heat_contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                          heat_id=draw.heat_id,
                                          created_by=cleaned_data["created_by"],
                                          created_date=cleaned_data["created_date"],
                                          )
        try:
            heat_contx.clean()
            heat_contx.save()
            row_entered = True
        except ValidationError:
            pass

        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk)
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def enter_heat_contx(heat, cleaned_data, indv_pk=None, grp_pk=None, team_pk=None, return_contx=False,
                     return_anix=False):
    row_entered = False
    if heat:
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     heat_id=heat,
                                     team_id_id=team_pk,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        heat_id=contx.heat_id,
                                                        tray_id__isnull=True,
                                                        tank_id__isnull=True,
                                                        trof_id__isnull=True,
                                                        draw_id__isnull=True,
                                                        cup_id__isnull=True,
                                                        team_id=contx.team_id).get()

        if indv_pk or grp_pk:
            anix, anix_entered = enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk)
            row_entered += anix_entered
        if return_anix:
            return anix, contx, row_entered
        if return_contx:
            return contx, row_entered
        else:
            return row_entered
    else:
        return False


def ajax_get_fields(request):
    model_name = request.GET.get('model', None)

    # use the model name passed from the web page to find the model in the apps models file
    model = models.__dict__[model_name]

    # use the retrieved model and get the doc string which is a string in the format
    # SomeModelName(id, field1, field2, field3)
    # remove the trailing parentheses, split the string up based on ', ', then drop the first element
    # which is the model name and the id.
    match = str(model.__dict__['__doc__']).replace(")", "").split(", ")[1:]
    fields = list()
    for f in match:
        label = "---"
        attr = getattr(model, f).field
        if hasattr(attr, 'verbose_name'):
            label = attr.verbose_name

        fields.append([f, label])

    data = {
        'fields': fields
    }

    return JsonResponse(data)


def naive_to_aware(naive_date, naive_time=None):
    # adds null time and timezone to dates
    if not nan_to_none(naive_time):
        naive_time = time(0, 0)
    return timezone.make_aware(datetime.combine(naive_date, naive_time))


def nan_to_none(test_item):
    if type(test_item) == float or type(test_item) == np.float64:
        if math.isnan(test_item):
            return None
    elif type(test_item) == str:
        if test_item == "nan":
            return None
    return test_item


def y_n_to_bool(test_item):
    if type(test_item) == float:
        if math.isnan(test_item):
            return False
        elif test_item:
            return True
    elif type(test_item) == int:
        if test_item:
            return True
    elif test_item.upper() in ["Y", "YES", "1"]:
        return True
    else:
        return False


def round_no_nan(data, precision):
    # data can be nan, decimal, float, etc.
    if data is None:
        return None
    elif math.isnan(data):
        return None
    else:
        return round(decimal.Decimal(data), precision)


def common_err_parser(err):
    err_msg = err.__str__()
    if issubclass(type(err), ObjectDoesNotExist):
        err_msg = "Could not find a {} object from worksheet in database.".format(err.__str__().split(" ")[0])
    return err_msg


def get_cont_from_tag(cont_tag, cont_id):
    cont = None
    if cont_tag == "cup":
        cont = models.Cup.objects.filter(pk=cont_id).get()
    elif cont_tag == "draw":
        cont = models.Drawer.objects.filter(pk=cont_id).get()
    elif cont_tag == "heat":
        cont = models.HeathUnit.objects.filter(pk=cont_id).get()
    elif cont_tag == "tank":
        cont = models.Tank.objects.filter(pk=cont_id).get()
    elif cont_tag == "tray":
        cont = models.Tray.objects.filter(pk=cont_id).get()
    elif cont_tag == "trof":
        cont = models.Trough.objects.filter(pk=cont_id).get()
    return cont


def get_col_date(col_name):
    try:
        col_date = datetime.strptime(col_name, "%Y-%b-%d").replace(tzinfo=pytz.UTC)
    except:
        col_date = False
    return col_date


def parse_trof_str(trof_str, facic_id):
    cont_str = trof_str.replace(" ", "")
    cont_ids = []
    if "," in cont_str:
        cont_list = cont_str.split(",")
    else:
        cont_list = [cont_str]

    for cont in cont_list:
        if "-" in cont:
            cont_lims = cont.split("-")
            cont_range = range(int(cont_lims[0]), int(cont_lims[1]) + 1)
            for trof_name in cont_range:
                trof_id = models.Trough.objects.filter(name__iexact=trof_name, facic_id=facic_id).get()
                cont_ids.append(trof_id)
        else:
            trof_id = models.Trough.objects.filter(name__iexact=cont, facic_id=facic_id).get()
            cont_ids.append(trof_id)
    return cont_ids


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def col_count_to_excel(col_count):
    # 0 returns A, 1 returns B, 26 returns AA
    # chr(65) returns "A"
    mod = col_count % 26
    floor = col_count // 26
    a_key = 65
    if floor:
        return "{}{}".format(chr(floor + a_key - 1), chr(mod + a_key))
    else:
        return chr(mod + a_key)


def get_object_from_request(request, param, model_type):
    obj_pk = request.GET.get(param)
    obj_id = None
    if obj_pk:
        obj_id = model_type.objects.filter(pk=obj_pk).get()
    return obj_id


def get_dict_from_move(move_id, destination):
    # out dict format:
    if destination:
        move_contx = move_id.contx_end
    else:
        move_contx = move_id.contx_start

    if move_contx:
        move_cont = move_contx.container
    else:
        return None

    out_dict = {"move_id": move_id, "cont_id": move_cont, "destination": destination}
    return out_dict
