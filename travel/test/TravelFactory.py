import factory
from django.contrib.auth.models import User
from faker import Faker

from shared_models.test.SharedModelsFactory import SectionFactory
from .. import models
from shared_models import models as shared_models

faker = Faker()


class TripFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Conference

    name = faker.word()
    start_date = faker.date_time()
    end_date = faker.date_time()


class TripRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TripRequest

    section = SectionFactory()

#     eqt_id = eqt_id if eqt_id else faker.random_int(1, 4)
#     #     eqt = models.EqtEquipmentTypeCode.objects.get(eqt_id=eqt_id)
#     #
#     #
#     is_research_scientist = models.BooleanField(default=False, choices=YES_NO_CHOICES,
#                                                 verbose_name=_("Is the traveller a research scientist (RES)?"))
#     first_name = models.CharField(max_length=100, verbose_name=_("first name"), blank=True, null=True)
#     last_name = models.CharField(max_length=100, verbose_name=_("last name"), blank=True, null=True)
#     address = models.CharField(max_length=1000, verbose_name=_("address"),
#                                blank=True, null=True)
#     phone = models.CharField(max_length=1000, verbose_name=_("phone"), blank=True, null=True)
#     email = models.EmailField(verbose_name=_("email"), blank=True, null=True)
#     company_name = models.CharField(max_length=255, verbose_name=_("company name"), blank=True, null=True)
#
#     # Trip Details
#     is_group_request = models.BooleanField(default=False,
#                                            verbose_name=_("Is this a group request (i.e., a request for multiple individuals)?"))
#     purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("purpose of travel"))
#     reason = models.ForeignKey(Reason, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("reason for travel"))
#     trip = models.ForeignKey(Conference, on_delete=models.DO_NOTHING, null=True, verbose_name=_("trip"), related_name="trip_requests")
#
#     departure_location = models.CharField(max_length=1000, verbose_name=_("departure location (city, province, country)"), blank=True,
#                                           null=True)
#     destination = models.CharField(max_length=1000, verbose_name=_("destination location (city, province, country)"), blank=True,
#                                    null=True)
#     start_date = models.DateTimeField(verbose_name=_("start date of travel"), null=True, blank=True)
#     end_date = models.DateTimeField(verbose_name=_("end date of travel"), null=True, blank=True)
#
#     #############
#     # these two fields should be deleted eventually if the event planning peice happens through this app...
#     # has_event_template = models.NullBooleanField(default=False,
#     #                                              verbose_name=_(
#     #                                                  "Is there an event template being completed for this trip or meeting?"))
#     # event_lead = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, verbose_name=_("Regional event lead"),
#     #                                related_name="trip_events", blank=True, null=True)
#     ################
#     role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role of traveller"))
#
#     # purpose
#     role_of_participant = models.TextField(blank=True, null=True, verbose_name=_("role description"))
#     objective_of_event = models.TextField(blank=True, null=True, verbose_name=_("objective of the trip"))
#     benefit_to_dfo = models.TextField(blank=True, null=True, verbose_name=_("benefit to DFO"))
#     multiple_conferences_rationale = models.TextField(blank=True, null=True,
#                                                       verbose_name=_("rationale for individual attending multiple conferences"))
#     bta_attendees = models.ManyToManyField(AuthUser, blank=True, verbose_name=_("Other attendees covered under BTA"))
#     multiple_attendee_rationale = models.TextField(blank=True, null=True, verbose_name=_(
#         "rationale for multiple travelers"))
#     late_justification = models.TextField(blank=True, null=True, verbose_name=_("Justification for late submissions"))
#     funding_source = models.TextField(blank=True, null=True, verbose_name=_("funding source"))
#     notes = models.TextField(blank=True, null=True, verbose_name=_("optional notes"))
#     # total_cost = models.FloatField(blank=True, null=True, verbose_name=_("total cost (DFO)"))
#     non_dfo_costs = models.FloatField(blank=True, null=True, verbose_name=_("Amount of non-DFO funding (CAD)"))
#     non_dfo_org = models.CharField(max_length=1000, verbose_name=_("full name(s) of organization providing non-DFO funding"), blank=True,
#                                    null=True)
#
#     submitted = models.DateTimeField(verbose_name=_("date submitted"), blank=True, null=True)
#     original_submission_date = models.DateTimeField(verbose_name=_("original submission date"), blank=True, null=True)
#     status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="trip_requests",
#                                limit_choices_to={"used_for": 2}, verbose_name=_("trip status"), default=8)
#     parent_request = models.ForeignKey("TripRequest", on_delete=models.CASCADE, related_name="children_requests", blank=True, null=True)
#     admin_notes = models.TextField(blank=True, null=True, verbose_name=_("Administrative notes"))
#     exclude_from_travel_plan = models.BooleanField(default=False, verbose_name=_("Exclude this traveller from the travel plan?"))

# # if providing an eqt_type use the WhalesdbFactory._eqt_type_codes array
# @staticmethod
# def get_valid_data(eqt_id=None):
#
#     eqt_id = eqt_id if eqt_id else faker.random_int(1, 4)
#     eqt = models.EqtEquipmentTypeCode.objects.get(eqt_id=eqt_id)
#
#     valid_data = {
#         'eqt': eqt.pk,
#         'emm_make': faker.word(),
#         'emm_model': faker.word(),
#         'emm_depth_rating': faker.random_int(10, 10000),
#         'emm_description': faker.text()
#     }
#
#     return valid_data
