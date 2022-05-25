from django.utils.translation import gettext_lazy as _

wind_speed_choices = (
    (1, _("no wind")),
    (2, _("calm / slight wind")),
    (3, _("light wind")),
    (4, _("moderate wind")),
    (5, _("heavy wind")),
    (6, _("variable")),
)

wind_direction_choices = (
    (1, _("north")),
    (2, _("northeast")),
    (3, _("east")),
    (4, _("southeast")),
    (5, _("south")),
    (6, _("southwest")),
    (7, _("west")),
    (8, _("northwest")),
)

precipitation_category_choices = (
    (1, _("no precipitation")),
    (2, _("mist")),
    (3, _("light rain")),
    (4, _("moderate rain")),
    (5, _("heavy rain")),
    (6, _("intermittent")),
    (7, _("flurries")),
)

operating_condition_choices = (
    (1, _("fully operational")),
    (2, _("partially operational")),
    (3, _("not operational")),
)

status_choices = (
    (1, _("unreviewed")),
    (2, _("reviewed")),
)

sample_type_choices = (
    (1, _("Rotary Screw Trap")),
    (2, _("Electrofishing")),
)

site_type_choices = (
    (1, _("Open")),
    (2, _("Closed")),
)

pulse_type_choices = (
    (1, _("Standard pulse ")),
    (2, _("Direct current")),
    (3, _("Burst of pulses")),
)

fish_size_choices = (
    (1, _("Fry")),
    (2, _("Parr")),
)

age_type_choices = (
    (1, _("scale")),
    (2, _("length-frequency")),
)
