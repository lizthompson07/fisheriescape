from django.utils.translation import gettext as _

from . import models


def is_admin(user):
    if user:
        return bool(hasattr(user, "trap_net_user") and user.trap_net_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(hasattr(user, "trap_net_user") and user.trap_net_user.is_crud_user)


def can_access(user):
    if user.id:
        return bool(hasattr(user, "trap_net_user"))


#
# def get_sample_field_list(sample=None):
#     is_rst = False
#     is_electro = False
#     if sample and sample.sample_type == 1:
#         is_rst = True
#     if sample and sample.sample_type == 2:
#         is_electro = True
#
#     my_list = [
#         'site',
#         'monitoring_program',
#         'arrival_departure|{}'.format(_("arrival / departure")),
#         'air_temp|{}'.format(_("air temperature (°C)")),
#         'percent_cloud_cover',
#         'wind|{}'.format(_("wind")),
#         'precipitation_category',
#         'precipitation_comment',
#         'water_temp|{}'.format(_("water temperature (°C)")),
#         'water_depth_display|{}'.format(_("water depth")),
#
#
#         'species_list|{}'.format(_("species caught")),
#         'tag_list|{}'.format(_("tags issued")),
#         'notes',
#         'old_id',
#         'reviewed_status|{}'.format(_("review status")),
#         'metadata|{}'.format(_("metadata")),
#
#     ]
#
#     # remove any instances of None
#     remove_nulls(my_list)
#
#     return my_list


def get_sample_field_list():
    my_list = [
        "site",
        "monitoring_program",
        "arrival_date",
        "departure_date",
        # "age_thresh_0_1",
        # "age_thresh_1_2",
        # "age_thresh_2_3",
        # "age_thresh_parr_smolt",
        # 'arrival_departure|{}'.format(_("arrival / departure")),
        # 'air_temp|{}'.format(_("air temperature (°C)")),
        # 'percent_cloud_cover',
        # 'wind|{}'.format(_("wind")),
        # "precipitation_category",
        # "precipitation_comment",
        # "water_temp_c",
        'didymo|{}'.format(_("Didymosphenia geminata?")),
        'thresholds|{}'.format(_(" salmon site-specific age thresholds")),
        'species_list|{}'.format(_("species caught")),
        'tag_list|{}'.format(_("tags issued")),
        'notes',
        'old_id',
        'reviewed_status|{}'.format(_("review status")),
        'metadata|{}'.format(_("metadata")),

    ]
    return my_list


def get_sub_field_list(sample):
    field_list = None
    if sample.sample_type == 1:
        field_list = get_rst_field_list()
    elif sample.sample_type == 2:
        field_list = get_ef_field_list()
    elif sample.sample_type == 3:
        field_list = get_trapnet_field_list()
    return field_list


def get_ef_field_list():
    my_list = [
        "air_temp_arrival",
        "water_temp_c",
        'site_type',
        'seine_type',
        'site_profile|{}'.format(_("site profile")),
        'substrate_profile|{}'.format(_("substrate profile")),
        'crew_display|{}'.format(_("crew")),
        'water_depth_display|{}'.format(_("water depth")),
        "water_cond",
        "water_ph",
        'avg_wetted_length|{}'.format(_("avg wetted length (meters)")),
        'avg_wetted_width|{}'.format(_("avg wetted width (meters)")),
        'full_wetted_area|{}'.format(_("full wetted area (sq meters)")),
        'overhanging_veg_display|{}'.format(_("overhanging vegetation (%)")),
        'max_overhanging_veg_display|{}'.format(_("max overhanging vegetation (m)")),
        "electrofisher",
        'electrofisher_params|{}'.format(_("electrofisher settings")),
    ]

    return my_list


def get_rst_field_list():
    my_list = [
        "air_temp_arrival",
        'water_temp_trap_c',
        'water_depth_m',
        'water_level_delta_m',
        'discharge_m3_sec',
        'rpm_arrival',
        'rpm_departure',
        'time_released',
        'operating_condition',
        'operating_condition_comment',
        'samplers',
    ]
    return my_list


def get_trapnet_field_list():
    my_list = [
        "air_temp_arrival",
        "water_temp_trap_c",
        "arrival_condition",
        "arrival_condition_comment",
        "departure_condition",
        "departure_condition_comment",
        "time_released",
        "samplers",
    ]
    return my_list


def get_age_from_length(length, threshold_0_1=None, threshold_1_2=None, threshold_2_3=None):
    age = None
    if threshold_0_1:
        # if there is a 0-1 threshold and the length is larger, it is a 0. end.
        if length < threshold_0_1:
            return 0
        # we can safely call it a 1+ but maybe it will get further refined
        else:
            age = 1

    # if there is a 1-2 threshold and the length is larger, it is a 2.
    if threshold_1_2 and length >= threshold_1_2:
        age = 2

    # if there is a 1-2 threshold and the length is larger, it is a 2.
    if threshold_2_3 and length >= threshold_2_3:
        age = 3

    return age




def get_restigouche_rst_samples():
    return models.Sample.objects.filter(sample_type=1, site__river__fishing_area__name__istartswith="sfa15")
