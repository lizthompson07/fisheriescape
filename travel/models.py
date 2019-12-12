import os

import textile
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Sum
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext

from lib.templatetags.verbose_names import get_verbose_label
from shared_models import models as shared_models
from lib.templatetags.custom_filters import nz, currency
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
        (APPROVAL, "Reviewer status"),
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
    is_adm_approval_required = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name=_(
        "does attendance to this require ADM approval?"))
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location (city, province, country)"))
    lead = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, verbose_name=_("Which region is taking the lead?"),
                             related_name="meeting_leads", blank=True, null=True)
    has_event_template = models.NullBooleanField(default=False, verbose_name=_(
        "Is there an event template being completed for this conference or meeting?"))
    number = models.IntegerField(blank=True, null=True, verbose_name=_("event number"))
    start_date = models.DateTimeField(verbose_name=_("start date of event"))
    end_date = models.DateTimeField(verbose_name=_("end date of event"))
    meeting_url = models.URLField(verbose_name=_("meeting URL"), blank=True, null=True)
    abstract_deadline = models.DateTimeField(verbose_name=_("abstract submission deadline"), blank=True, null=True)
    registration_deadline = models.DateTimeField(verbose_name=_("registration deadline"), blank=True, null=True)
    notes = models.TextField(blank=True, null=True, verbose_name=_("general notes"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            my_str = "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.name)
        return "{}, {} ({} {} {})".format(my_str, self.location, self.start_date.strftime("%d-%b-%Y"), _("to"),
                                          self.end_date.strftime("%d-%b-%Y"))

    class Meta:
        ordering = ['number', ]

    def get_absolute_url(self):
        return reverse('travel:conf_detail', kwargs={'pk': self.id})

    @property
    def bta_traveller_list(self):
        # create a list of all TMS users going
        legit_traveller_list = self.traveller_list
        travellers = []
        for trip in self.trips.filter(~Q(status_id=10)):
            # lets look at the list of BTA travels and add them all
            for bta_user in trip.bta_attendees.all():
                # if this user for some reason turns up to be a real traveller on this trip
                # (i.e. the assertion that they are a BTA traveller is wrong, they should not be added)
                if bta_user not in legit_traveller_list:
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
        my_list.extend(["{} {} ({})".format(trip.first_name, trip.last_name, _("no DM Apps user connected")) for trip in
                        self.trips.filter(~Q(status_id=10)).filter(is_group_trip=False) if not trip.user])

        # group travellers
        my_list.extend(
            [trip.user for trip in Trip.objects.filter(parent_trip__conference=self).filter(~Q(status_id=10)) if trip.user])
        my_list.extend(["{} {} ({})".format(trip.first_name, trip.last_name, _("no DM Apps user connected")) for trip in
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

    @property
    def total_cost(self):
        # from travel.models import Event
        # must factor in group and non-group...

        # start simple... non-group
        my_list = [trip.total_trip_cost for trip in self.trips.filter(~Q(status_id=10)).filter(is_group_trip=False)]
        # group travellers
        my_list.extend(
            [trip.total_trip_cost for trip in Trip.objects.filter(parent_trip__conference=self).filter(~Q(status_id=10))])

        return sum(my_list)

    @property
    def tname(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            my_str = "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.name)
        return my_str

    @property
    def conf_fiscal_year(self):
        return shared_models.FiscalYear.objects.get(pk=fiscal_year(next=False, date=self.start_date, sap_style=True))

    @property
    def get_summary_dict(self):
        """
        This method is used to return a dictionary of users attending a conference/meeting, as well as the number of
        conferences or international meetings they have attended.
        """
        my_dict = {}

        # get a trip list that will be used to get a list of users (sigh...)
        # my_trip_list = self.children_trips.all() if self.is_group_trip else Trip.objects.filter(pk=self.id)

        # get the fiscal year of the conference
        fy = self.conf_fiscal_year

        for traveller in self.total_traveller_list:
            total_list = []
            fy_list = []

            # if this is not a real User instance, there is nothing to do.
            try:

                # there are two things we have to do to get this list...
                # 1) get all non group travel
                qs = traveller.user_trips.filter(conference__is_adm_approval_required=True).filter(is_group_trip=False)
                total_list.extend([trip for trip in qs])
                fy_list.extend([trip for trip in qs.filter(fiscal_year=fy)])

                # 2) get all group travel - the trick part is that we have to grab the parent trip
                qs = traveller.user_trips.filter(parent_trip__conference__is_adm_approval_required=True)
                total_list.extend([trip.parent_trip for trip in qs])
                fy_list.extend([trip.parent_trip for trip in qs.filter(fiscal_year=fy)])

                my_dict[traveller] = {}
                my_dict[traveller]["total_list"] = list(set(total_list))
                my_dict[traveller]["fy_list"] = list(set(fy_list))

            except AttributeError:
                # This is the easy part
                my_dict[traveller] = {}
                my_dict[traveller]["total_list"] = "---"
                my_dict[traveller]["fy_list"] = "---"
        return my_dict


class Trip(models.Model):
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, verbose_name=_("fiscal year"),
                                    default=fiscal_year(sap_style=True), blank=True, null=True, related_name="trips")
    is_group_trip = models.BooleanField(default=False,
                                        verbose_name=_("Is this a group trip (i.e., is this a request for multiple individuals)?"))
    purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("purpose of travel"))
    reason = models.ForeignKey(Reason, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("reason for travel"))
    conference = models.ForeignKey(Conference, on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_("conference / meeting"), related_name="trips")

    # traveller info
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="user_trips",
                             verbose_name=_("user"))
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, verbose_name=_("DFO section"))
    first_name = models.CharField(max_length=100, verbose_name=_("first name"), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("last name"), blank=True, null=True)
    address = models.CharField(max_length=1000, verbose_name=_("address"),
                               blank=True, null=True)
    phone = models.CharField(max_length=1000, verbose_name=_("phone"), blank=True, null=True)
    email = models.EmailField(verbose_name=_("email"), blank=True, null=True)
    is_public_servant = models.BooleanField(default=True, choices=YES_NO_CHOICES, verbose_name=_("Is the traveller a public servant?"))
    is_research_scientist = models.BooleanField(default=False, choices=YES_NO_CHOICES,
                                                verbose_name=_("Is the traveller a research scientist (RES)?"))
    company_name = models.CharField(max_length=255, verbose_name=_("company name"), blank=True, null=True)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, verbose_name=_("DFO region"), related_name="trips",
                               null=True, blank=True)
    # trip_title = models.CharField(max_length=1000, verbose_name=_("trip title"))
    departure_location = models.CharField(max_length=1000, verbose_name=_("departure location (city, province, country)"), blank=True,
                                          null=True)
    destination = models.CharField(max_length=1000, verbose_name=_("destination location (city, province, country)"), blank=True,
                                   null=True)
    start_date = models.DateTimeField(verbose_name=_("start date of travel"), null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_("end date of travel"), null=True, blank=True)

    #############
    # these two fields should be deleted eventually if the event planning peice happens through this app...
    # has_event_template = models.NullBooleanField(default=False,
    #                                              verbose_name=_(
    #                                                  "Is there an event template being completed for this conference or meeting?"))
    # event_lead = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, verbose_name=_("Regional event lead"),
    #                                related_name="trip_events", blank=True, null=True)
    ################
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role of traveller"))

    # purpose
    role_of_participant = models.TextField(blank=True, null=True, verbose_name=_("role description"))
    objective_of_event = models.TextField(blank=True, null=True, verbose_name=_("objective of the trip"))
    benefit_to_dfo = models.TextField(blank=True, null=True, verbose_name=_("benefit to DFO"))
    multiple_conferences_rationale = models.TextField(blank=True, null=True,
                                                      verbose_name=_("rationale for individual attending multiple conferences"))
    bta_attendees = models.ManyToManyField(AuthUser, blank=True, verbose_name=_("Other attendees covered under BTA"))
    multiple_attendee_rationale = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for multiple travelers"))
    late_justification = models.TextField(blank=True, null=True, verbose_name=_("Justification for late submissions"))
    funding_source = models.TextField(blank=True, null=True, verbose_name=_("funding source"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("optional notes"))

    # costs
    air = models.FloatField(blank=True, null=True, verbose_name=_("air fare"))
    rail = models.FloatField(blank=True, null=True, verbose_name=_("rail"))
    rental_motor_vehicle = models.FloatField(blank=True, null=True, verbose_name=_("rental motor vehicles"))
    personal_motor_vehicle = models.FloatField(blank=True, null=True, verbose_name=_("personal motor vehicles"))
    taxi = models.FloatField(blank=True, null=True, verbose_name=_("taxi"))
    other_transport = models.FloatField(blank=True, null=True, verbose_name=_("other transport"))
    accommodations = models.FloatField(blank=True, null=True, verbose_name=_("accommodation"))
    # meals = models.FloatField(blank=True, null=True, verbose_name=_("meals"))
    no_breakfasts = models.IntegerField(blank=True, null=True, verbose_name=_("number of breakfasts"))
    breakfasts_rate = models.FloatField(blank=True, null=True, verbose_name=_("breakfast rate (CAD/day)"), default=20.35)
    breakfasts = models.FloatField(blank=True, null=True, verbose_name=_("breakfasts"))
    no_lunches = models.IntegerField(blank=True, null=True, verbose_name=_("number of lunches"))
    lunches_rate = models.FloatField(blank=True, null=True, verbose_name=_("lunch rate (CAD/day)"), default=20.60)
    lunches = models.FloatField(blank=True, null=True, verbose_name=_("lunches"))
    no_suppers = models.IntegerField(blank=True, null=True, verbose_name=_("number of suppers"))
    suppers_rate = models.FloatField(blank=True, null=True, verbose_name=_("supper rate (CAD/day)"), default=50.55)
    suppers = models.FloatField(blank=True, null=True, verbose_name=_("suppers"))
    no_incidentals = models.IntegerField(blank=True, null=True, verbose_name=_("number of incidentals"))
    incidentals_rate = models.FloatField(blank=True, null=True, verbose_name=_("incidental rate (CAD/day)"), default=17.30)
    incidentals = models.FloatField(blank=True, null=True, verbose_name=_("incidentals"))
    registration = models.FloatField(blank=True, null=True, verbose_name=_("registration"))
    other = models.FloatField(blank=True, null=True, verbose_name=_("other"))
    total_cost = models.FloatField(blank=True, null=True, verbose_name=_("total trip cost (DFO)"))
    non_dfo_costs = models.FloatField(blank=True, null=True, verbose_name=_("Estimated non-DFO costs (CAD)"))
    non_dfo_org = models.CharField(max_length=1000, verbose_name=_("Full name(s) of organization paying non-DFO costs"), blank=True,
                                   null=True)

    submitted = models.DateTimeField(verbose_name=_("date sumbitted"), blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="trips",
                               limit_choices_to={"used_for": 2}, verbose_name=_("trip status"), default=8)
    parent_trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="children_trips", blank=True, null=True)

    @property
    def trip_title(self):
        group_status = " - {}".format(gettext("Group Request")) if self.is_group_trip else ""

        my_str = "{} {}{}".format(
            self.first_name,
            self.last_name,
            group_status,
        )
        if self.conference:
            my_str += " - {}".format(self.conference.tname)
        if self.destination:
            my_str += " - {}".format(self.destination)
        return my_str

    def __str__(self):
        return "{}".format(self.trip_title)

    class Meta:
        ordering = ["-start_date", "last_name"]
        unique_together = [("user", "parent_trip"), ]

    def get_absolute_url(self):
        return reverse('travel:trip_detail', kwargs={'pk': self.id})

    @property
    def meals(self):
        return nz(self.breakfasts, 0) + nz(self.lunches, 0) + nz(self.suppers, 0)

    def save(self, *args, **kwargs):
        # total the meals and incidentals
        self.breakfasts = nz(self.no_breakfasts, 0) * nz(self.breakfasts_rate, 0)
        self.lunches = nz(self.no_lunches, 0) * nz(self.lunches_rate, 0)
        self.suppers = nz(self.no_suppers, 0) * nz(self.suppers_rate, 0)
        self.incidentals = nz(self.no_incidentals, 0) * nz(self.incidentals_rate, 0)

        # total cost
        self.total_cost = nz(self.air, 0) + nz(self.rail, 0) + nz(self.rental_motor_vehicle, 0) + nz(self.personal_motor_vehicle, 0) + nz(
            self.taxi, 0) + nz(self.other_transport, 0) + nz(self.accommodations, 0) + nz(self.incidentals, 0) + nz(
            self.other, 0) + nz(self.registration, 0) + nz(self.breakfasts, 0) + nz(self.lunches, 0) + nz(self.suppers, 0)
        if self.start_date:
            self.fiscal_year_id = fiscal_year(date=self.start_date, sap_style=True)

        # if the start and end dates are null, but there is a conference, use those.. to populate
        if self.conference and not self.start_date:
            print("adding start date from conference")
            self.start_date = self.conference.start_date
        if self.conference and not self.end_date:
            print("adding end date from conference")
            self.end_date = self.conference.end_date

        # ensure the process order makes sense
        count = 1
        for reviewer in self.reviewers.all():  # use the default sorting
            reviewer.order = count
            reviewer.save()
            count += 1

        return super().save(*args, **kwargs)

    @property
    def reviewer_order_message(self):
        last_reviewer = None
        for reviewer in self.reviewers.all():
            # basically, each subsequent reviewer should have a role that is further down in order than the previous
            if last_reviewer:
                if last_reviewer.role.order > reviewer.role.order:
                    return "WARNING: The roles of the reviewers are out of order!"
            last_reviewer = reviewer

    @property
    def cost_breakdown(self):
        cost_list = [
            "air",
            "rail",
            "rental_motor_vehicle",
            "personal_motor_vehicle",
            "taxi",
            "other_transport",
            "accommodations",
            "breakfasts",
            "lunches",
            "suppers",
            "incidentals",
            "registration",
            "other",
        ]
        my_str = ""
        for cost in cost_list:
            if getattr(self, cost):
                if cost in ("breakfasts", "lunches", "suppers", "incidentals"):
                    my_str += "{}: ${:,.2f} ({} x {:,.2f}); ".format(
                        self._meta.get_field(cost).verbose_name,
                        nz(getattr(self, cost),0),
                        nz(getattr(self, "no_" + cost),0),
                        nz(getattr(self, cost + "_rate"),0),
                    )
                else:
                    my_str += "{}: ${:,.2f}; ".format(self._meta.get_field(cost).verbose_name, getattr(self, cost))
        return my_str

    @property
    def cost_table(self):
        cost_list = [
            "air",
            "rail",
            "rental_motor_vehicle",
            "personal_motor_vehicle",
            "taxi",
            "other_transport",
            "accommodations",
            "breakfasts",
            "lunches",
            "suppers",
            "incidentals",
            "registration",
            "other",
        ]

        # style #1 - costs as headers
        # my_str = "<table class='table table-sm table-bordered plainjane'><tr>"
        # for cost in cost_list:
        #     my_str += "<th class='plainjane'>{}</th>".format(get_verbose_label(self, cost))
        # my_str += "</tr><tr>"
        # for cost in cost_list:
        #     my_str += "<td class='plainjane'>{}</td>".format(nz(currency(getattr(self, cost)),"---"))
        # my_str += "</tr></table>"

        # style # 2 - 2 columns
        my_str = "<table class='plainjane' style='width: 40%'>"
        my_str += "<tr class='plainjane'><th class='plainjane'>{}</th><th class='plainjane'>{}</td></tr>".format(
            _("Cost category"), _("Amount (CAD)"))
        for cost in cost_list:
            if cost in ("breakfasts", "lunches", "suppers", "incidentals"):
                my_str += "<tr><td class='plainjane'>{}</td><td class='plainjane'>{} ({} &times; {})</td></tr>".format(
                    get_verbose_label(self, cost),
                    nz(currency(getattr(self, cost)), "---"),
                    nz(getattr(self, "no_"+cost), "---"),
                    nz(currency(getattr(self, cost + "_rate")), "---"),
                )
            else:
                my_str += "<tr><td class='plainjane'>{}</td><td class='plainjane'>{}</td></tr>".format(
                    get_verbose_label(self, cost), nz(currency(getattr(self, cost)), "---"))

        my_str += "<tr><th class='plainjane'>{}</th><th class='plainjane'>{}</td></tr>".format(
            _("TOTAL"), nz(currency(self.total_trip_cost), "---"))
        my_str += "</table>"
        return mark_safe(my_str)

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
            my_str += "<br><em>Funding source:</em> {}".format(self.funding_source)

        return my_str

    @property
    def purpose_long_text(self):
        """
        For CFTS report
        """
        my_str = "{}: {}".format("OBJECTIVE OF EVENT", nz(self.objective_of_event, "n/a"))

        my_str += "\n\n{}: {}".format("BENEFIT TO DFO", nz(self.benefit_to_dfo, "n/a"))

        my_str += "\n\n{}: {}".format(
            "Rationale for attending multiple conferences".upper(), nz(self.multiple_conferences_rationale, "n/a"))

        my_str += "\n\n{}: {}".format(
            "Rationale for multiple attendees".upper(),
            nz(self.multiple_attendee_rationale, "n/a"))
        return my_str

    @property
    def current_reviewer(self):
        """Send back the first reviewer whose status is 'pending' """
        return self.reviewers.filter(status_id=1).first()

    @property
    def status_string(self):
        my_status = self.status
        #  if the status is not 'draft' or 'approved' AND there is a current_reviewer
        status_str = "{}".format(my_status)
        if my_status.id not in [11, 8, ] and self.current_reviewer:
            status_str += " {} {}".format(_("by"), self.current_reviewer.user)
        return status_str

    @property
    def adm(self):
        return self.reviewers.filter(role_id=5).first()

    @property
    def rdg(self):
        return self.reviewers.filter(role_id=6).first()

    @property
    def recommenders(self):
        return self.reviewers.filter(role_id=2)


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
        ordering = ["order", "id"]


class Reviewer(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="reviewers")
    order = models.IntegerField(null=True, verbose_name=_("process order"))
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="reviewers", verbose_name=_("DM Apps user"))
    role = models.ForeignKey(ReviewerRole, on_delete=models.DO_NOTHING, verbose_name=_("role"))
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, limit_choices_to={"used_for": 1},
                               verbose_name=_("review status"), default=4)
    status_date = models.DateTimeField(verbose_name=_("status date"), blank=True, null=True)
    comments = models.TextField(null=True, verbose_name=_("Comments"))

    class Meta:
        unique_together = ['trip', 'user', 'role', ]
        ordering = ['trip', 'order', ]

    @property
    def comments_html(self):
        if self.comments:
            return textile.textile(self.comments)

    def save(self, *args, **kwargs):
        self.status_date = timezone.now()
        return super().save(*args, **kwargs)

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


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'travel/trip_{0}/{1}'.format(instance.trip.id, filename)


class File(models.Model):
    trip = models.ForeignKey(Trip, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("caption"))
    file = models.FileField(upload_to=file_directory_path, null=True, verbose_name=_("file attachment"))
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['trip', 'date_created']

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class HelpText(models.Model):
    field_name = models.CharField(max_length=255)
    eng_text = models.TextField(verbose_name=_("English text"))
    fra_text = models.TextField(blank=True, null=True, verbose_name=_("French text"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("eng_text"))):
            return "{}".format(getattr(self, str(_("eng_text"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.eng_text)

    class Meta:
        ordering = ['field_name', ]
