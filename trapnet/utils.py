from django.utils.translation import gettext as _


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
#         'rpms|{}'.format(_("RPMs")) if is_rst else None,
#         'time_released' if is_rst else None,
#         'operating_condition' if is_rst else None,
#         'operating_condition_comment' if is_rst else None,
#         'samplers' if is_rst else None,
#
#         'site_type' if is_electro else None,
#         'seine_type' if is_electro else None,
#         'site_profile|{}'.format(_("site profile")) if is_electro else None,
#         'substrate_profile|{}'.format(_("substrate profile")) if is_electro else None,
#         'crew_display|{}'.format(_("crew")) if is_electro else None,
#         "water_cond" if is_electro else None,
#         'full_wetted_width|{}'.format(_("full wetted width (sq meters)")) if is_electro else None,
#         'avg_depth_lower|{}'.format(_("mean lower depth (cm)")) if is_electro else None,
#         'avg_depth_middle|{}'.format(_("mean middle depth (cm)")) if is_electro else None,
#         'avg_depth_upper|{}'.format(_("mean upper depth (cm)")) if is_electro else None,
#         'overhanging_veg_display|{}'.format(_("overhanging vegetation (%)")) if is_electro else None,
#         'max_overhanging_veg_display|{}'.format(_("max overhanging vegetation (m)")) if is_electro else None,
#         "electrofisher" if is_electro else None,
#         'electrofisher_params|{}'.format(_("electrofisher settings")) if is_electro else None,
#         'didymo|{}'.format(_("Didymosphenia geminata?")) if is_electro else None,
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
        'arrival_departure|{}'.format(_("arrival / departure")),
        'air_temp|{}'.format(_("air temperature (°C)")),
        'percent_cloud_cover',
        'wind|{}'.format(_("wind")),
        "precipitation_category",
        "precipitation_comment",
        "water_temp_c",
        'didymo|{}'.format(_("Didymosphenia geminata?")),
        'thresholds|{}'.format(_("site-specific salmon age thresholds")),
        'species_list|{}'.format(_("species caught")),
        'tag_list|{}'.format(_("tags issued")),
        'notes',
        'old_id',
        'reviewed_status|{}'.format(_("review status")),
        'metadata|{}'.format(_("metadata")),

    ]
    return my_list


def get_ef_field_list(sample=None):
    my_list = [
        'site_type',
        'seine_type',
        'site_profile|{}'.format(_("site profile")),
        'substrate_profile|{}'.format(_("substrate profile")),
        'crew_display|{}'.format(_("crew")),
        'water_depth_display|{}'.format(_("water depth")),
        "water_cond",
        "water_ph",
        'full_wetted_width|{}'.format(_("full wetted width (sq meters)")),
        'avg_depth_lower|{}'.format(_("mean lower depth (cm)")),
        'avg_depth_middle|{}'.format(_("mean middle depth (cm)")),
        'avg_depth_upper|{}'.format(_("mean upper depth (cm)")),
        'overhanging_veg_display|{}'.format(_("overhanging vegetation (%)")),
        'max_overhanging_veg_display|{}'.format(_("max overhanging vegetation (m)")),
        "electrofisher",
        'electrofisher_params|{}'.format(_("electrofisher settings")),
    ]

    return my_list


def get_age_from_length(length, t0=None, t1=None):
    if t0 and t1:
        if length < t0:
            return 0
        elif length >= t1:
            return 2
        else:
            return 1
    elif t0 and length < t0:
        return 0
    elif t1 and length >= t1:
        return 2
    return None
