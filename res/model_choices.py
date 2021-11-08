from django.utils.translation import gettext_lazy as _

yes_no_choices = (
    (True, "Yes"),
    (False, "No"),
)

language_choices = (
    (1, _('English')),
    (2, _('French')),
)

decision_choices = (
    (1, _("In my opinion, the dossier contains sufficient evidence to warrant consideration of the application by the appropriate committee.")),
    (2, _("In my opinion, the dossier does not contain sufficient evidence to warrant consideration of the application by the appropriate committee.")),
)

application_status_choices = (
    (10, _("Draft")),
    (20, _("Submitted")),
    (30, _("Awaiting manager decision")),  # client submits request
    (40, _("Awaiting applicant signature")),  # client submits request
    (50, _("Under further review")),  # ??
    (90, _("Not approved")),  # ??
    (100, _("Approved")),  # ??
)
#
# request_decision_choices = (
#     (1, _("Accepted")),
#     (2, _("Withdrawn")),
# )
#
# prioritization_choices = (
#     (1, _('High')),
#     (2, _('Medium')),
#     (3, _('Low')),
# )
#
# process_scope_choices = (
#     (1, _('Regional')),
#     (2, _('Zonal')),
#     (3, _('National')),
# )
#
# process_type_choices = (
#     (1, _('Advisory Meeting')),
#     (2, _('Science Response Process')),
#     # (3, _('Peer Review')),
# )
#
# # process_status_choices = (
# #     (1, _('In-progress')),
# #     (2, _('Complete')),
# #     (3, _('Deferred')),
# #     (4, _('Delayed')),
# #     (5, _('Tentative')),
# # )
#
# process_status_dict = (
#     dict(trigger=None, stage="initiation", text=_("Initiated"), value=1),
#     ####################
#     dict(trigger=None, stage="in-progress", text=_("On"), value=20),
#     dict(trigger=None, stage="in-progress", text=_("ToR Complete"), value=22),
#     dict(trigger=None, stage="in-progress", text=_("Meeting Complete"), value=25),
#     ####################
#     dict(trigger=None, stage="deferred", text=_("Deferred"), value=30),
#     ####################
#     dict(trigger=None, stage="complete", text=_("Complete"), value=100),
#     ####################
#     dict(trigger=None, stage="withdrawn", text=_("Withdrawn"), value=90),
# )
#
#
# def get_process_status_choices():
#     return [(item["value"], item["text"]) for item in process_status_dict]
#
#
# def get_process_status_lookup():
#     my_dict = dict()
#     for item in process_status_dict:
#         my_dict[item["value"]] = dict()
#         my_dict[item["value"]]["stage"] = item["stage"]
#         my_dict[item["value"]]["text"] = item["text"]
#     return my_dict
#
#
# # meeting_type_choices = (
# #     (1, _("Planning")),
# #     # (2, _("Science Management Meeting (Planning)")), is this a planning meeting?
# #     (3, _("Keystone")),
# # )
#
# # meeting_quarter_choices = (
# #     (1, _("Spring")),
# #     (2, _("Summer")),
# #     (3, _("Fall")),
# #     (4, _("Winter")),
# # )
# #
#
# note_type_choices = (
#     (1, _('General comment')),
#     (2, _('To Do')),
# )
#
# # document_type_choices = (
# #     (1, _("Meeting Minutes")),
# #     (2, _("Science Advisory Report")),
# #     (3, _("Research Document")),
# #     (4, _("Proceedings")),
# #     (5, _("Science Response")),
# #     (6, _("Working Paper")),
# #     (7, _("Terms of Reference")),
# # )
# #
# # document_type_dict = (
# #     dict(text="Meeting Minutes", value=1, days_due=None),
# #     dict(text=_("Science Advisory Report"), value=2, days_due=56),
# #     dict(text=_("Research Document"), value=3, days_due=122),
# #     dict(text=_("Proceedings"), value=4, days_due=122),
# #     dict(text=_("Science Response"), value=5, days_due=56),
# #     dict(text=_("Working Paper"), value=6, days_due=None),
# #     dict(text=_("Terms of Reference"), value=7, days_due=None),
# # )
# #
# # def get_document_type_choices():
# #     return [(item["value"], item["text"]) for item in document_type_dict]
# #
# #
# # def get_document_type_lookup():
# #     my_dict = dict()
# #     for item in document_type_dict:
# #         my_dict[item["value"]] = dict()
# #         my_dict[item["value"]]["days_due"] = item["days_due"]
# #         my_dict[item["value"]]["text"] = item["text"]
# #     return my_dict
#
#
# document_status_dict = (
#     dict(trigger=None, stage="ok", text=_("OK"), value=0),
#     ####################
#     dict(trigger=None, stage="preparation", text=_("Tracking initiated"), value=1),
#     dict(trigger="submission_date", stage="preparation", text=_("Submitted by author"), value=2),
#     ####################
#     dict(trigger="date_chair_sent", stage="review", text=_("Under review by chair"), value=3),
#     dict(trigger="date_chair_appr", stage="review", text=_("Approved by chair"), value=4),
#     dict(trigger="date_coordinator_sent", stage="review", text=_("Under review by CSAS coordinator"), value=5),
#     dict(trigger="date_coordinator_appr", stage="review", text=_("Approved by CSAS coordinator"), value=6),
#     dict(trigger="date_section_head_sent", stage="review", text=_("Under review by section head"), value=13),
#     dict(trigger="date_section_head_appr", stage="review", text=_("Approved by section head"), value=14),
#     dict(trigger="date_division_manager_sent", stage="review", text=_("Under review by division manager"), value=15),
#     dict(trigger="date_division_manager_appr", stage="review", text=_("Approved by division manager"), value=16),
#     dict(trigger="date_director_sent", stage="review", text=_("Under review by director"), value=7),
#     dict(trigger="date_director_appr", stage="review", text=_("Approved by director"), value=8),
#
#     ####################
#     dict(trigger="date_doc_submitted", stage="finalization", text=_("Submitted to CSAS office"), value=9),
#     dict(trigger="date_proof_author_sent", stage="finalization", text=_("Proof sent to author"), value=10),
#     dict(trigger="date_proof_author_approved", stage="finalization", text=_("Proof approved by author"), value=11),
#     ####################
#     dict(trigger="actual_posting_date", stage="final", text=_("Posted"), value=12),
#     dict(trigger="updated_posting_date", stage="final", text=_("Posted (updated)"), value=17),
# )
#
#
# def get_document_status_choices():
#     return [(item["value"], item["text"]) for item in document_status_dict]
#
#
# def get_document_status_lookup():
#     my_dict = dict()
#     for item in document_status_dict:
#         my_dict[item["value"]] = dict()
#         my_dict[item["value"]]["stage"] = item["stage"]
#         my_dict[item["value"]]["text"] = item["text"]
#     return my_dict
#
#
# translation_status_dict = (
#     dict(trigger=None, stage="", text="----", value=0),
#     dict(trigger="date_translation_sent", stage="preparation", text=_("In progress"), value=1),
#     dict(trigger="date_returned", stage="finalization", text=_("Translated, unreviewed"), value=2),
#     dict(trigger="translation_review_date", stage="final", text=_("Translated, reviewed"), value=3),
# )
#
#
# def get_translation_status_choices():
#     return [(item["value"], item["text"]) for item in translation_status_dict]
#
#
# def get_translation_status_lookup():
#     my_dict = dict()
#     for item in translation_status_dict:
#         my_dict[item["value"]] = dict()
#         my_dict[item["value"]]["stage"] = item["stage"]
#         my_dict[item["value"]]["text"] = item["text"]
#     return my_dict
#
#
# translation_status_choices = (
#     (0, _("---")),
#     (1, _("In-progress")),
#     (2, _("Complete")),
# )
#
# invitee_status_choices = (
#     (0, 'Invited'),
#     (1, 'Accepted'),
#     (2, 'Declined'),
#     (3, 'Tentative'),
# )
#
# invitee_role_categories = (
#     (1, 'chair'),
#     (2, 'client lead'),
#     (3, 'steering committee member'),
#     (4, 'science lead'),
#     (5, 'csas coordinator'),
#     (6, 'science advisor'),
# )
#
# cost_category_choices = (
#     (1, 'Translation'),
#     (2, 'Travel'),
#     (3, 'Hospitality'),
#     (4, 'Space rental'),
#     (5, 'Simultaneous translation'),
#     (9, 'Other'),
# )
