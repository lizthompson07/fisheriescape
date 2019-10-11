from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from lib.templatetags.custom_filters import nz
from lib.functions.custom_functions import fiscal_year

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


class Event(models.Model):
    # choices for approval_status
    PENDING = 1
    APPROVED = 2
    DENIED = 3

    APPROVAL_STATUS_CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (DENIED, _("Denied")),
    )

    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, verbose_name=_("fiscal year"),
                                    default=fiscal_year(sap_style=True), blank=True, null=True)
    # traveller info
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="user_trips",
                             verbose_name=_("connected user"))
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("DFO section"),
                                limit_choices_to={'division__branch': 1})
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    address = models.CharField(max_length=1000, verbose_name=_("address"), default="343 Université Avenue, Moncton, NB, E1C 9B6")
    phone = models.CharField(max_length=1000, verbose_name=_("phone"))
    email = models.EmailField(verbose_name=_("email"))
    public_servant = models.BooleanField(default=True, choices=YES_NO_CHOICES)
    company_name = models.CharField(max_length=255, verbose_name=_("company name (leave blank if DFO)"), blank=True, null=True)
    trip_title = models.CharField(max_length=1000, verbose_name=_("trip title"))
    departure_location = models.CharField(max_length=1000, verbose_name=_("departure location"), blank=True, null=True)
    destination = models.CharField(max_length=1000, verbose_name=_("destination location"), blank=True, null=True)
    start_date = models.DateTimeField(verbose_name=_("start date of travel"))
    end_date = models.DateTimeField(verbose_name=_("end date of travel"))
    event = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name=_("is this a registered event"))
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role of participant"))
    reason = models.ForeignKey(Reason, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("reason for travel"))
    purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("purpose of travel"))

    # purpose
    role_of_participant = models.TextField(blank=True, null=True, verbose_name=_(
        "role of participant (More expansive than just saying he/she “present a paper” for example.  This should describe how does his/her role at the event relate to his/her role at DFO)"))
    objective_of_event = models.TextField(blank=True, null=True, verbose_name=_(
        "objective of the event (Brief description of what the event is about.  Not objective of the Participants in going to the event.)"))
    benefit_to_dfo = models.TextField(blank=True, null=True, verbose_name=_(
        "benefit to DFO (What does DFO get out of this? Saves money, better programs, etc…)"))
    multiple_conferences_rationale = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for individual attending multiple conferences"))
    multiple_attendee_rationale = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for multiple attendees at this event"))
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
    recommender_1 = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="recommender_1_trips",
                                      verbose_name=_("Recommender 1"), blank=True, null=True)
    recommender_2 = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="recommender_2_trips",
                                      verbose_name=_("Recommender 2"), blank=True, null=True)
    recommender_3 = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="recommender_3_trips",
                                      verbose_name=_("Recommender 3"), blank=True, null=True)
    approver = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="approver_trips",
                                 verbose_name=_("Approver"), blank=True, null=True)

    recommender_1_approval_status = models.IntegerField(verbose_name=_("recommender 1 approval status"), default=1,
                                                        choices=APPROVAL_STATUS_CHOICES)
    recommender_2_approval_status = models.IntegerField(verbose_name=_("recommender 2 approval status"), default=1,
                                                        choices=APPROVAL_STATUS_CHOICES)
    recommender_3_approval_status = models.IntegerField(verbose_name=_("recommender 3 approval status"), default=1,
                                                        choices=APPROVAL_STATUS_CHOICES)
    approver_approval_status = models.IntegerField(verbose_name=_("expenditure initiation approval status"), default=1,
                                                   choices=APPROVAL_STATUS_CHOICES)

    recommender_1_approval_date = models.DateTimeField(verbose_name=_("recommender 1 approval date"), blank=True, null=True)
    recommender_2_approval_date = models.DateTimeField(verbose_name=_("recommender 2 approval date"), blank=True, null=True)
    recommender_3_approval_date = models.DateTimeField(verbose_name=_("recommender 3 approval date"), blank=True, null=True)
    approver_approval_date = models.DateTimeField(verbose_name=_("expenditure initiation approval date"), blank=True, null=True)
    waiting_on = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="waiting_on_trips", verbose_name=_("Waiting on"),
                                   blank=True, null=True)

    def __str__(self):
        return "{}".format(self.trip_title)

    class Meta:
        ordering = ["start_date", "last_name"]

    def get_absolute_url(self):
        return reverse('travel:event_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        # total cost
        self.total_cost = nz(self.air, 0) + nz(self.rail, 0) + nz(self.rental_motor_vehicle, 0) + nz(self.personal_motor_vehicle, 0) + nz(
            self.taxi, 0) + nz(self.other_transport, 0) + nz(self.accommodations, 0) + nz(self.meals, 0) + nz(self.incidentals, 0) + nz(
            self.other, 0) + nz(self.registration, 0)
        self.fiscal_year_id = fiscal_year(date=self.start_date, sap_style=True)
        self.approval_seeker()
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
            my_str += "\nObjective of Event: {}".format(self.objective_of_event)
        if self.benefit_to_dfo:
            my_str += "\nBenefit to DFO: {}".format(self.benefit_to_dfo)
        if self.multiple_conferences_rationale:
            my_str += "\nRationale for attending multiple conferences: {}".format(self.multiple_conferences_rationale)
        if self.multiple_attendee_rationale:
            my_str += "\nRationale for multiple attendees: {}".format(self.multiple_attendee_rationale)
        if self.funding_source:
            my_str += "\nFunding source: {}".format(self.multiple_attendee_rationale)

        return my_str

    def get_status_str(self, approver):
        if getattr(self, approver):
            if getattr(self, approver + "_approval_status"):
                status = "{}".format(
                    getattr(self, "get_" + approver + "_approval_status_display")(),
                )
            else:
                status = "{} {} {}".format(
                    getattr(self, "get_" + approver + "_approval_status_display")(),
                    _("on"),
                    getattr(self, "get_" + approver + "_approval_date").strftime("%Y-%m-%d"),
                )

            my_str = "{} ({})".format(
                getattr(self, approver),
                status,
            )
        else:
            my_str = "n/a"
        return my_str

    @property
    def recommender_1_status(self):
        return self.get_status_str("recommender_1")

    @property
    def recommender_2_status(self):
        return self.get_status_str("recommender_2")

    @property
    def recommender_3_status(self):
        return self.get_status_str("recommender_3")

    @property
    def approver_status(self):
        return self.get_status_str("approver")

    def approval_seeker(self):
        from . import emails

        # check to see if recommender 1 has reviewed the trip
        my_email = None
        if not self.recommender_1_approval_date:
            # we need to get approval and need to set recommender 1 as who we are waiting on
            self.waiting_on = self.recommender_1
            # build email to recommender 1
            my_email = emails.ApprovalAwaitingEmail(self, "recommender_1")

        else:
            if self.recommender_2 and not self.recommender_2_approval_date:
                # we need to get approval and need to set recommender 2 as who we are waiting on
                self.waiting_on = self.recommender_2
                # build email to recommender 2
                my_email = emails.ApprovalAwaitingEmail(self, "recommender_2")

            else:
                if self.recommender_3 and not self.recommender_3_approval_date:
                    # we need to get approval and need to set recommender 3 as who we are waiting on
                    self.waiting_on = self.recommender_3
                    # build email to recommender 3
                    my_email = emails.ApprovalAwaitingEmail(self, "recommender_3")
                else:
                    if self.approver and not self.approver_approval_date:
                        # we need to get approval and need to set approver as who we are waiting on
                        self.waiting_on = self.approver
                        # send email to approver
                        # for now we will not do this.
                    else:
                        self.waiting_on = None

        if my_email:
            # send the email object
            if settings.PRODUCTION_SERVER:
                send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
                          recipient_list=my_email.to_list, fail_silently=False, )
            else:
                print(my_email)
