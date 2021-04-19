from django.utils.translation import gettext_lazy as _

yes_no_choices = (
    (True, "Yes"),
    (False, "No"),
)

request_type_choices = (
    (1, _('New')),
    (2, _('Previous')),
)

language_choices = (
    (1, _('English')),
    (2, _('French')),
)

request_status_choices = (
    (1, _("Draft")),
    (2, _("Submitted")),
    (3, _("Under review")),
    # all status below here should correspond to review decision choice + 10
    (11, _("On")),
    (12, _("Off")),
    (13, _("Withdrawn")),
)

request_decision_choices = (
    (1, _("On")),
    (2, _("Off")),
    (3, _("Withdrawn")),
)

prioritization_choices = (
    (1, _('High')),
    (2, _('Medium')),
    (3, _('Low')),
)

process_type_choices = (
    (1, _('Regional')),
    (1, _('Zonal')),
    (1, _('National')),
)

_choices = (
    (1, _('')),
)

_choices = (
    (1, _('')),
)

_choices = (
    (1, _('')),
)
