from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from lib.templatetags.custom_filters import nz
from lib.functions.custom_functions import fiscal_year, listrify

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class Role(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name (eng)"), blank=True, null=True)
    nom = models.CharField(max_length=100, verbose_name=_("name (fre)"), blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ["name", ]


class Reason(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name (eng)"), blank=True, null=True)
    nom = models.CharField(max_length=100, verbose_name=_("name (fre)"), blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ["name", ]


class Purpose(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name (eng)"), blank=True, null=True)
    nom = models.CharField(max_length=100, verbose_name=_("name (fre)"), blank=True, null=True)
    description_eng = models.CharField(max_length=1000, verbose_name=_("description (eng)"), blank=True, null=True)
    description_fre = models.CharField(max_length=1000, verbose_name=_("description (fre)"), blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ["name", ]


class Status(models.Model):
    # choices for used_for
    APPROVAL = 1
    TRIPS = 2
    USED_FOR_CHOICES = (
        (APPROVAL, "Approval status"),
        (TRIPS, "Trip status"),
    )

    used_for = models.IntegerField(choices=USED_FOR_CHOICES)
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['used_for', 'order', 'name', ]


class Conference(models.Model):
    name = models.CharField(max_length=255, unique=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True, verbose_name=_("event number"))
    start_date = models.DateTimeField(verbose_name=_("start date of event"))
    end_date = models.DateTimeField(verbose_name=_("end date of event"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['number', ]

    def get_absolute_url(self):
        return reverse('travel:conf_detail', kwargs={'pk': self.id})

    @property
    def bta_traveller_list(self):
        # create a list of all TMS users going
        travellers = []
        for trip in self.trips.filter(~Q(status_id=10)):
            # lets look at the list of BTA travels and add them all
            for bta_user in trip.bta_attendees.all():
                travellers.append(bta_user)
        # return a set of all users
        return list(set(travellers))

    @property
    def traveller_list(self):
        # from travel.models import Event
        # must factor in group and non-group...

        # start simple... non-group
        my_list = [trip.user for trip in self.trips.filter(~Q(status_id=10)).filter(is_group_trip=False) if trip.user]
        # now those without names...
        my_list.extend(["{} {} (not connected to a user)".format(trip.first_name, trip.last_name) for trip in
                        self.trips.filter(~Q(status_id=10)).filter(is_group_trip=False) if not trip.user])

        # group travellers
        my_list.extend(
            [trip.user for trip in Trip.objects.filter(parent_trip__confernce=self).filter(~Q(status_id=10)) if trip.user])
        my_list.extend(["{} {} (not connected to a user)".format(trip.first_name, trip.last_name) for trip in
                        Trip.objects.filter(parent_trip__conference=self).filter(~Q(status_id=10)) if not trip.user])

        return set(my_list)

    @property
    def total_traveller_list(self):
        travellers = self.bta_traveller_list
        travellers.extend(self.traveller_list)
        return list(set(travellers))

    @property
    def travellers(self):
        return listrify(self.total_traveller_list)


class Trip(models.Model):
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, verbose_name=_("fiscal year"),
                                    default=fiscal_year(sap_style=True), blank=True, null=True, related_name="trips")
    is_group_trip = models.BooleanField(default=False,
                                        verbose_name=_("Is this a group trip (i.e., is this a request for multiple individuals)?"))
    # traveller info
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="user_trips",
                             verbose_name=_("user"))
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("DFO section"),
                                limit_choices_to={'division__branch': 1})
    first_name = models.CharField(max_length=100, verbose_name=_("first name"), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("last name"), blank=True, null=True)
    address = models.CharField(max_length=1000, verbose_name=_("address"), default="343 Université Avenue, Moncton, NB, E1C 9B6",
                               blank=True, null=True)
    phone = models.CharField(max_length=1000, verbose_name=_("phone"), blank=True, null=True)
    email = models.EmailField(verbose_name=_("email"), blank=True, null=True)
    public_servant = models.BooleanField(default=True, choices=YES_NO_CHOICES)
    company_name = models.CharField(max_length=255, verbose_name=_("company name (leave blank if DFO)"), blank=True, null=True)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, verbose_name=_("DFO region"), related_name="trips",
                               blank=True, null=True, default=1)
    trip_title = models.CharField(max_length=1000, verbose_name=_("trip title"))
    departure_location = models.CharField(max_length=1000, verbose_name=_("departure location"), blank=True, null=True)
    destination = models.CharField(max_length=1000, verbose_name=_("destination location"), blank=True, null=True)
    start_date = models.DateTimeField(verbose_name=_("start date of travel"), blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_("end date of travel"), blank=True, null=True)
    reason = models.ForeignKey(Reason, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("reason for travel"))
    purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("purpose of travel"))
    is_international = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name=_(
        "is this travel international, or are international travellers part of this trip request?"))
    is_conference = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name=_("is this a conference?"))
    conference = models.ForeignKey(Conference, on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_("conference"), related_name="trips")
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role of participant"))

    # purpose
    role_of_participant = models.TextField(blank=True, null=True, verbose_name=_(
        "role of participant (More expansive than just saying he/she “present a paper” for example.  "
        "This should describe how does his/her role at the event relate to his/her role at DFO)"))
    objective_of_event = models.TextField(blank=True, null=True, verbose_name=_(
        "objective of the event (Brief description of what the event is about.  Not objective of the Participants in going to the event.)"))
    benefit_to_dfo = models.TextField(blank=True, null=True, verbose_name=_(
        "benefit to DFO (What does DFO get out of this? Saves money, better programs, etc…)"))
    multiple_conferences_rationale = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for individual attending multiple conferences"))
    multiple_attendee_rationale = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for multiple attendees at this event"))
    late_justification = models.TextField(blank=True, null=True, verbose_name=_("Justification for late submissions"))
    funding_source = models.TextField(blank=True, null=True, verbose_name=_("funding source"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("optional notes (will not be included in travel plan)"))

    # costs
    air = models.FloatField(blank=True, null=True, verbose_name=_("air fare costs"))
    rail = models.FloatField(blank=True, null=True, verbose_name=_("rail costs"))
    rental_motor_vehicle = models.FloatField(blank=True, null=True, verbose_name=_("rental motor vehicles costs"))
    personal_motor_vehicle = models.FloatField(blank=True, null=True, verbose_name=_("personal motor vehicles costs"))
    taxi = models.FloatField(blank=True, null=True, verbose_name=_("taxi costs"))
    other_transport = models.FloatField(blank=True, null=True, verbose_name=_("other transport costs"))
    accommodations = models.FloatField(blank=True, null=True, verbose_name=_("accommodation costs"))
    meals = models.FloatField(blank=True, null=True, verbose_name=_("meal costs"))
    incidentals = models.FloatField(blank=True, null=True, verbose_name=_("incidental costs"))
    registration = models.FloatField(blank=True, null=True, verbose_name=_("registration"))
    other = models.FloatField(blank=True, null=True, verbose_name=_("other costs"))
    total_cost = models.FloatField(blank=True, null=True, verbose_name=_("total trip cost"))

    bta_attendees = models.ManyToManyField(AuthUser, blank=True, verbose_name=_("Other attendees covered under BTA"))

    submitted = models.DateTimeField(verbose_name=_("date sumbitted"), blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="trips",
                               limit_choices_to={"used_for": 2}, verbose_name=_("Trip approval status"),
                               blank=True, null=True)
    parent_trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="children_trips", blank=True, null=True)

    def __str__(self):
        return "{}".format(self.trip_title)

    class Meta:
        ordering = ["-start_date", "last_name"]
        unique_together = [("user", "parent_trip"), ]

    def get_absolute_url(self):
        return reverse('travel:trip_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        # total cost
        self.total_cost = nz(self.air, 0) + nz(self.rail, 0) + nz(self.rental_motor_vehicle, 0) + nz(self.personal_motor_vehicle, 0) + nz(
            self.taxi, 0) + nz(self.other_transport, 0) + nz(self.accommodations, 0) + nz(self.meals, 0) + nz(self.incidentals, 0) + nz(
            self.other, 0) + nz(self.registration, 0)
        if self.start_date:
            self.fiscal_year_id = fiscal_year(date=self.start_date, sap_style=True)

        # run the approval seeker function
        # self.approval_seeker()
        # self.set_trip_status()
        return super().save(*args, **kwargs)

    @property
    def cost_breakdown(self):
        my_str = ""
        if self.air:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("air").verbose_name, self.air)
        if self.rail:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("rail").verbose_name, self.rail)
        if self.rental_motor_vehicle:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("rental_motor_vehicle").verbose_name, self.rental_motor_vehicle)
        if self.personal_motor_vehicle:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("personal_motor_vehicle").verbose_name, self.personal_motor_vehicle)
        if self.taxi:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("taxi").verbose_name, self.taxi)
        if self.other_transport:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("other_transport").verbose_name, self.other_transport)
        if self.accommodations:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("accommodations").verbose_name, self.accommodations)
        if self.meals:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("meals").verbose_name, self.meals)
        if self.incidentals:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("incidentals").verbose_name, self.incidentals)
        if self.registration:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("registration").verbose_name, self.registration)
        if self.other:
            my_str += "{}: ${:,.2f}; ".format(self._meta.get_field("other").verbose_name, self.other)
        return my_str

    @property
    def total_trip_cost(self):
        if self.is_group_trip:
            object_list = self.children_trips.all()
            return object_list.values("total_cost").order_by("total_cost").aggregate(dsum=Sum("total_cost"))['dsum']
        else:
            return self.total_cost

    @property
    def purpose_long(self):
        my_str = ""
        if self.role_of_participant:
            my_str += "<em>Role of Participant:</em> {}".format(self.role_of_participant)
        if self.objective_of_event:
            my_str += "<br><em>Objective of Event:</em> {}".format(self.objective_of_event)
        if self.benefit_to_dfo:
            my_str += "<br><em>Benefit to DFO:</em> {}".format(self.benefit_to_dfo)
        if self.multiple_conferences_rationale:
            my_str += "<br><em>Rationale for attending multiple conferences:</em> {}".format(self.multiple_conferences_rationale)
        if self.multiple_attendee_rationale:
            my_str += "<br><em>Rationale for multiple attendees:</em> {}".format(self.multiple_attendee_rationale)
        if self.funding_source:
            my_str += "<br><em>Funding source:</em> {}".format(self.multiple_attendee_rationale)

        return my_str

    @property
    def purpose_long_text(self):
        my_str = ""
        if self.role_of_participant:
            my_str += "Role of Participant: {}".format(self.role_of_participant)
        if self.objective_of_event:
            my_str += "\n\nObjective of Event: {}".format(self.objective_of_event) if len(my_str) > 0 else "Objective of Event: {}".format(
                self.objective_of_event)
        if self.benefit_to_dfo:
            my_str += "\n\nBenefit to DFO: {}".format(self.benefit_to_dfo)
        if self.multiple_conferences_rationale:
            my_str += "\n\nRationale for attending multiple conferences: {}".format(self.multiple_conferences_rationale)
        if self.multiple_attendee_rationale:
            my_str += "\n\nRationale for multiple attendees: {}".format(self.multiple_attendee_rationale)
        if self.funding_source:
            my_str += "\n\nFunding source: {}".format(self.multiple_attendee_rationale)

        return my_str

    # def approval_seeker(self):
    #     """ This method if meant to seek approvals via email, set waiting_ons and set project status"""
    #     from . import emails
    #
    #     # if someone denied it at any point, the trip is 'denied'
    #     if self.recommender_1_approval_status_id == 3 or \
    #             self.recommender_2_approval_status_id == 3 or \
    #             self.recommender_3_approval_status_id == 3 or \
    #             self.adm_approval_status_id == 3 or \
    #             self.rdg_approval_status_id == 3:
    #         self.status_id = 10  # DENIED
    #         # The statuses of recommenders and approvers are handled by the form_valid method of the ApprovalUpdateView
    #
    #     # otherwise, if the project is submitted
    #     elif self.submitted:
    #         # make sure the statuses are changed from 4 to 1
    #         if self.recommender_1_approval_status_id == 4:
    #             self.recommender_1_approval_status_id = 1
    #         if self.recommender_2_approval_status_id == 4:
    #             self.recommender_2_approval_status_id = 1
    #         if self.recommender_3_approval_status_id == 4:
    #             self.recommender_3_approval_status_id = 1
    #         if self.adm_approval_status_id == 4:
    #             self.adm_approval_status_id = 1
    #         if self.rdg_approval_status_id == 4:
    #             self.rdg_approval_status_id = 1
    #
    #         # check to see if recommender 1 has reviewed the trip
    #         my_email = None
    #
    #         if self.recommender_1 and not self.recommender_1_approval_date:
    #             # we need to get approval and need to set recommender 1 as who we are waiting on
    #             self.waiting_on = self.recommender_1
    #             # project status will be "pending recommendation"
    #             self.status_id = 12
    #             # build email to recommender 1
    #             my_email = emails.ApprovalAwaitingEmail(self, "recommender_1")
    #         elif self.recommender_2 and not self.recommender_2_approval_date:
    #             # we need to get approval and need to set recommender 2 as who we are waiting on
    #             self.waiting_on = self.recommender_2
    #             # project status will be "pending recommendation"
    #             self.status_id = 12
    #             # build email to recommender 2
    #             my_email = emails.ApprovalAwaitingEmail(self, "recommender_2")
    #
    #         elif self.recommender_3 and not self.recommender_3_approval_date:
    #             # we need to get approval and need to set recommender 3 as who we are waiting on
    #             self.waiting_on = self.recommender_3
    #             # project status will be "pending recommendation"
    #             self.status_id = 12
    #             # build email to recommender 3
    #             my_email = emails.ApprovalAwaitingEmail(self, "recommender_3")
    #         elif self.adm and not self.adm_approval_date:
    #             # we need to get approval and need to set approver as who we are waiting on
    #             self.waiting_on = self.adm
    #             # project status will be "pending adm approval"
    #             self.status_id = 14
    #             # send email to TMS admin
    #             my_email = emails.AdminApprovalAwaitingEmail(self, "adm")
    #         elif self.rdg and not self.rdg_approval_date:
    #             # we need to get approval and need to set approver as who we are waiting on
    #             self.waiting_on = self.rdg
    #             # project status will be "pending rdg approval"
    #             self.status_id = 15
    #             # send email to TMS admin
    #             my_email = emails.AdminApprovalAwaitingEmail(self, "rdg")
    #         else:
    #             # project has been fully approved?
    #             self.status_id = 11
    #             self.waiting_on = None
    #
    #         if my_email:
    #             # send the email object
    #             if settings.PRODUCTION_SERVER:
    #                 send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
    #                           recipient_list=my_email.to_list, fail_silently=False, )
    #             else:
    #                 print(my_email)
    #     else:
    #         self.recommender_1_approval_status_id = 4
    #         self.recommender_2_approval_status_id = 4
    #         self.recommender_3_approval_status_id = 4
    #         self.rdg_approval_status_id = 4
    #         self.adm_approval_status_id = 4
    #         self.recommender_1_approval_date = None
    #         self.recommender_2_approval_date = None
    #         self.recommender_3_approval_date = None
    #         self.rdg_approval_date = None
    #         self.adm_approval_date = None
    #         self.waiting_on = None
    #         self.status_id = 8


class ReviewerRole(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name (eng)"), blank=True, null=True)
    nom = models.CharField(max_length=100, verbose_name=_("name (fre)"), blank=True, null=True)
    order = models.IntegerField()

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ["order", ]


class Reviewer(models.Model):
    # trip = models.ForeignKey(Event, on_delete=models.DO_NOTHING, related_name="reviewers")
    order = models.IntegerField(blank=True, null=True, verbose_name=_("approval order"))
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="trip_reviewers", verbose_name=_("DM Apps user"))
    role = models.ForeignKey(ReviewerRole, on_delete=models.DO_NOTHING, verbose_name=_("role"))
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, limit_choices_to={"used_for": 1},
                               verbose_name=_("review status"), default=4)
    status_date = models.DateTimeField(verbose_name=_("status date"), blank=True, null=True)

    # class Meta:
    #     unique_together = ['trip', 'user', 'role', ]
    #     ordering = ['trip', 'order', ]
    #
    # def save(self, *args, **kwargs):
    #     self.order = self.trip.reviewers.count()
    #     return super().save(*args, **kwargs)

    @property
    def status_string(self):

        if self.status.id in [1, 4, 5]:
            status = "{}".format(
                self.status
            )
        else:
            status = "{} {} {}".format(
                self.status,
                _("on"),
                self.status_date.strftime("%Y-%m-%d"),
            )

        my_str = "<span style='background-color:{}'>{} ({})</span>".format(
            self.status.color,
            self.user,
            status,
        )
        return mark_safe(my_str)
