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
    (1,	_("draft")),
    (2,	_("submitted")),
    (3,	_("reviewed")),
    (9,	_("withdrawn")),
)

request_decision_choices = (
    (1,	_("on")),
    (2,	_("off")),
    (3,	_("tentative")),
)


priority_rating_choices = (
    (1, _('')),
)

_choices = (
    (1, _('regional')),
    (1, _('zonal')),
    (1, _('national')),
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

