from django.utils.translation import gettext_lazy as _

yes_no_choices = (
    (True, "Yes"),
    (False, "No"),
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
    (14, _("Deferred")),
)

request_decision_choices = (
    (1, _("On")),
    (2, _("Off")),
    (3, _("Withdrawn")),
    (4, _("Deferred")),
)

prioritization_choices = (
    (1, _('High')),
    (2, _('Medium')),
    (3, _('Low')),
)

process_scope_choices = (
    (1, _('Regional')),
    (2, _('Zonal')),
    (3, _('National')),
)

process_type_choices = (
    (1, _('Advisory Meeting')),
    (2, _('Science Response Process')),
    (3, _('Peer Review')),
)

process_status_choices = (
    (1, _('In-progress')),
    (2, _('Complete')),
    (3, _('Deferred')),
    (4, _('Delayed')),
)

meeting_type_choices = (
    (1, _("Steering Committee Meeting")),
    (2, _("Science Management Meeting")),
    (3, _("Advisory Process Meeting (RAP)")),
)

note_type_choices = (
    (1, 'To Do'),
    (2, 'Next step'),
    (3, 'General comment'),
)

document_type_choices = (
    (1, _("Meeting Minutes")),
    (2, _("Science Advisory Report")),
    (3, _("Research Document")),
    (4, _("Proceedings")),
    (5, _("Science Response")),
    (6, _("Working Paper")),
)

document_status_choices = (
    (1, _("Draft")),
    (2, _("Submitted")),
    (3, _("Under review")),
)

invitee_role_choices = (
    (1, 'Chair'),
    (7, 'CSAS coordinator'),
    (3, 'Expert'),
    (6, 'External reviewer'),
    (5, 'Internal reviewer'),
    (2, 'Participant'),
    # (4, 'Steering Committee Member (is this is good category?)'),
)

invitee_status_choices = (
    (0, 'Invited'),
    (1, 'Accepted'),
    (2, 'Declined'),
    (3, 'Tentative'),
)

cost_category_choices = (
    (1, 'Translation'),
    (2, 'Travel'),
    (3, 'Hospitality'),
    (4, 'Space rental'),
    (9, 'Other'),
)
