from django.utils.translation import gettext as _

from shared_models.utils import remove_nulls


def is_admin(user):
    if user:
        return user.groups.filter(name='trapnet_admin').count() != 0


def can_access(user):
    if user:
        return is_admin(user) or user.groups.filter(name='trapnet_access').exists()


def get_sample_field_list(sample=None):
    is_rst = False
    is_electro = False
    if sample and sample.sample_type == 1:
        is_rst = True
    if sample and sample.sample_type == 2:
        is_electro = True

    my_list = [
        'site',
        'arrival_departure|{}'.format(_("arrival / departure")),
        'air_temp|{}'.format(_("air temperature (°C)")),
        'percent_cloud_cover',
        'wind|{}'.format(_("wind")),
        'precipitation_category',
        'precipitation_comment',
        'water_temp|{}'.format(_("water temperature (°C)")),
        'water_depth_display|{}'.format(_("water depth")),

        'rpms|{}'.format(_("RPMs")) if is_rst else None,
        'operating_condition' if is_rst else None,
        'operating_condition_comment' if is_rst else None,
        'samplers' if is_rst else None,

        'site_profile|{}'.format(_("site profile")) if is_electro else None,
        'substrate_profile|{}'.format(_("substrate profile")) if is_electro else None,
        'crew_display|{}'.format(_("crew")) if is_electro else None,
        "water_cond" if is_electro else None,
        'full_wetted_width|{}'.format(_("full wetted width (sq. meters)")) if is_electro else None,
        'avg_depth_lower|{}'.format(_("mean lower depth (cm)")) if is_electro else None,
        'avg_depth_middle|{}'.format(_("mean middle depth (cm)")) if is_electro else None,
        'avg_depth_upper|{}'.format(_("mean upper depth (cm)")) if is_electro else None,
        'overhanging_veg_display|{}'.format(_("overhanging vegetation (%)")) if is_electro else None,
        'max_overhanging_veg_display|{}'.format(_("max overhanging vegetation (m)")) if is_electro else None,
        "electrofisher" if is_electro else None,
        'electrofisher_params|{}'.format(_("electrofisher settings")) if is_electro else None,

        'species_list|{}'.format(_("species caught")),
        'tag_list|{}'.format(_("tags issued")),
        'notes',
        'metadata|{}'.format(_("metadata")),

    ]

    # remove any instances of None
    remove_nulls(my_list)

    return my_list
