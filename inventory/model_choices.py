from django.utils.translation import gettext_lazy as _

from .data_fixtures import content_types, statuses, maintenance_levels, security_classifications, character_sets, \
    spatial_representation_types, spatial_reference_systems, resource_types

protocol_choices = (
    ("HTTP", "HTTP"),
    ("HTTPS", "HTTPS"),
    ("FTP", "FTP"),
)

service_language_choices = (
    ("urn:xml:lang:eng-CAN", "English"),
    ("urn:xml:lang:fra-CAN", "French"),
)

country_choices = (
    ('Canada', 'Canada'),
    ('United States', 'United States'),
)

review_decision_choices = (
    (3, _("In Progress")),
    (0, _("Unevaluated")),
    (1, _("Compliant")),
    (2, _("Non-compliant")),
)

dma_status_choices = (
    (0, _("Unevaluated")),
    (1, _("On-track")),
    (2, _("Complete")),
    (3, _("Encountering issues")),
    (4, _("Aborted / cancelled")),
    (5, _("Pending new evaluation")),
    (6, _("In Progress")),
)

dma_frequency_choices = (
    (1, _("Daily")),
    (2, _("Weekly")),
    (3, _("Monthly")),
    (4, _("Annually")),
    (5, _("Irregular / as needed")),
    (9, _("Other")),
)

content_type_choices = content_types.get_choices()
status_choices = statuses.get_choices()
maintenance_choices = maintenance_levels.get_choices()
security_classification_choices = security_classifications.get_choices()
data_char_set_choices = character_sets.get_choices()
spat_representation_choices = spatial_representation_types.get_choices()
spat_ref_system_choices = spatial_reference_systems.get_choices()
resource_type_choices = resource_types.get_choices()
