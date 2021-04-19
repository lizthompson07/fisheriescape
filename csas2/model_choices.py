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
    (3,	_("under review")),
    # all status below here should correspond to review decision choice + 10
    (11,	_("on")),
    (12,	_("off")),
    (13,	_("withdrawn")),
)

request_decision_choices = (
    (1,	_("on")),
    (2,	_("off")),
    (3,	_("withdrawn")),
    # (4,	_("tentative")),
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

