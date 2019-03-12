from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from projects import models as projects_models
from lib.templatetags.custom_filters import nz
from lib.functions.fiscal_year import fiscal_year

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
    fiscal_year = models.ForeignKey(projects_models.FiscalYear, on_delete=models.DO_NOTHING, verbose_name=_("fiscal year"),
                                    default=fiscal_year(sap_style=True))
    # traveller info
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("connected user"))
    section = models.ForeignKey(projects_models.Section, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("DFO section"))
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    address = models.CharField(max_length=1000, verbose_name=_("address"), default="343 Université Avenue, Moncton, NB, E1C 9B6")
    phone = models.CharField(max_length=1000, verbose_name=_("phone"))
    email = models.EmailField(verbose_name=_("email"))
    public_servant = models.BooleanField(default=True, choices=YES_NO_CHOICES)
    company_name = models.CharField(max_length=255, verbose_name=_("company name"), blank=True, null=True)
    trip_title = models.CharField(max_length=1000, verbose_name=_("trip title"))
    location = models.CharField(max_length=1000, verbose_name=_("location (e.g., city, province, country)"))
    conf_start_date = models.DateTimeField(verbose_name=_("start date of conference"))
    conf_end_date = models.DateTimeField(verbose_name=_("end date of conference"))
    event = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name=_("is this a registered event"))
    plan_number = models.CharField(max_length=255, verbose_name=_("plan number"), blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role of participant"))
    reason = models.ForeignKey(Reason, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("reason for travel"))
    purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("rurpose of travel"))

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
    other = models.FloatField(blank=True, null=True, verbose_name=_("other costs"))

    total_cost = models.FloatField(blank=True, null=True, verbose_name=_("total trip cost"))

    def __str__(self):
        return "{}".format(self.trip_title)

    class Meta:
        ordering = ["-conf_start_date", "last_name"]

    def get_absolute_url(self):
        return reverse('travel:event_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        # total cost
        self.total_cost = nz(self.air, 0) + nz(self.rail, 0) + nz(self.rental_motor_vehicle, 0) + nz(self.personal_motor_vehicle, 0) + nz(
            self.taxi, 0) + nz(self.other_transport, 0) + nz(self.accommodations, 0) + nz(self.meals, 0) + nz(self.incidentals, 0) + nz(
            self.other, 0)
        return super().save(*args, **kwargs)

    @property
    def cost_breakdown(self):
        my_str = ""
        if self.air:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("air").verbose_name, self.air)
        if self.rail:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("rail").verbose_name, self.rail)
        if self.rental_motor_vehicle:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("rental_motor_vehicle").verbose_name, self.rental_motor_vehicle)
        if self.personal_motor_vehicle:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("personal_motor_vehicle").verbose_name, self.personal_motor_vehicle)
        if self.taxi:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("taxi").verbose_name, self.taxi)
        if self.other_transport:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("other_transport").verbose_name, self.other_transport)
        if self.accommodations:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("accommodations").verbose_name, self.accommodations)
        if self.meals:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("meals").verbose_name, self.meals)
        if self.incidentals:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("incidentals").verbose_name, self.incidentals)
        if self.other:
            my_str += "{}=${:,.2f};".format(self._meta.get_field("other").verbose_name, self.other)
        return my_str

    @property
    def purpose_long(self):
        my_str = ""
        if self.role_of_participant:
            my_str += "{}".format(self.role_of_participant)
        if self.objective_of_event:
            my_str += "<br><br>{}".format(self.objective_of_event)
        if self.benefit_to_dfo:
            my_str += "<br><br>{}".format(self.benefit_to_dfo)
        if self.multiple_conferences_rationale:
            my_str += "<br><br>{}".format(self.multiple_conferences_rationale)
        if self.multiple_attendee_rationale:
            my_str += "<br><br>{}".format(self.multiple_attendee_rationale)
        return my_str
