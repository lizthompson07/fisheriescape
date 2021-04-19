from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from markdown import markdown

from csas2 import model_choices
from lib.functions.custom_functions import fiscal_year
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language, Person, Section, \
    SimpleLookupWithUUID


def file_directory_path(instance, filename):
    return 'csas/request_{0}/{1}'.format(instance.request.id, filename)


class CSASRequest(SimpleLookupWithUUID, MetadataFields):
    ''' csas request '''
    type = models.IntegerField(default=1, verbose_name=_("type"), choices=model_choices.request_type_choices)
    language = models.IntegerField(default=1, verbose_name=_("language of request"), choices=model_choices.language_choices)
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("tittle (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("tittle (fr)"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_coordinator_requests", verbose_name=_("Regional CSAS coordinator"))
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_client_requests", verbose_name=_("DFO client"))
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="csas_requests", verbose_name=_("section"))

    is_multiregional = models.BooleanField(default=False,
                                           verbose_name=_("Does this request involve more than one region (zonal) or more than one client sector?"))
    multiregional_text = models.TextField(null=True, blank=True, verbose_name=_("Please provide the contact name, sector, and region for all involved."))

    issue = models.TextField(verbose_name=_("Issue requiring science information and/or advice"),
                             help_text=_("Should be phrased as a question to be answered by Science"))
    had_assistance = models.BooleanField(default=False, verbose_name=_(
        "Have you had assistance from Science in developing the question/request?"), help_text=_("E.g. with CSAS and/or DFO science staff."))
    assistance_text = models.TextField(null=True, blank=True, verbose_name=_(" Please provide details about the assistance received"))

    rationale = models.TextField(verbose_name=_("Rationale or context for the request"),
                                 help_text=_("What will the information/advice be used for? Who will be the end user(s)? Will it impact other DFO "
                                             "programs or regions?"))
    risk_text = models.TextField(null=True, blank=True, verbose_name=_("What is the expected consequence if science advice is not provided?"))
    advice_needed_by = models.DateTimeField(verbose_name=_("Latest Possible Date to Receive Science Advice"))
    rationale_for_timeline = models.TextField(null=True, blank=True, verbose_name=_("Rationale for deadline?"),
                                              help_text=_("e.g., COSEWIC or consultation meetings, Environmental Assessments, legal or regulatory "
                                                          "requirement, Treaty obligation, international commitments, etc)."
                                                          "Please elaborate and provide anticipatory dates"))
    has_funding = models.BooleanField(default=False, verbose_name=_("Do you have funds to cover any extra costs associated with this request?"),
                                      help_text=_("i.e., special analysis, meeting costs, translation)?"), )
    funding_text = models.TextField(null=True, blank=True, verbose_name=_("Please describe"))
    file_attachment = models.FileField(upload_to=file_directory_path, null=True, blank=True, verbose_name=_("signed request form"))

    # non-editable fields
    status = models.IntegerField(default=1, verbose_name=_("status"), editable=False)
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("submission date"), editable=False)
    old_id = models.IntegerField(blank=True, null=True, editable=False)

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="csas_requests",
                                    verbose_name=_("fiscal year"), editable=False)

    class Meta:
        ordering = ("fiscal_year", _("name"))

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.advice_needed_by, sap_style=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("csas2:request_detail", args=[self.id])

    @property
    def issue_html(self):
        if self.issue:
            return mark_safe(markdown(self.issue))

    @property
    def rationale_html(self):
        if self.rationale:
            return mark_safe(markdown(self.rationale))

    @property
    def multiregional_display(self):
        if self.is_multiregional:
            text = self.multiregional_text if self.multiregional_text else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")

    @property
    def assistance_display(self):
        if self.had_assistance:
            text = self.assistance_text if self.assistance_text else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")

    @property
    def funding_display(self):
        if self.has_funding:
            text = self.funding_text if self.funding_text else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")


class CSASRequestReview(MetadataFields):
    csas_request = models.OneToOneField(CSASRequest, on_delete=models.CASCADE, editable=False, related_name="review")
    notes = models.TextField(blank=True, null=True, verbose_name=_("coordinator notes"))
    decision = models.IntegerField(blank=True, null=True, verbose_name=_("decision"), choices=model_choices.request_decision_choices)
    decision_text = models.TextField(blank=True, null=True, verbose_name=_("Decision Explanation"))
    decision_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Date a decision was made"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(gettext("Review for CSAS Request #"), self.csas_request.id)

    @property
    def decision_display(self):
        if self.decision:
            text = self.decision_text if self.decision_text else gettext("no further explanation provided.")
            return "{} - {}".format(self.get_decision_display(), text)
        return gettext("---")

    @property
    def decision_explanation_html(self):
        if self.decision_explanation:
            return mark_safe(markdown(self.decision_explanation))


class Process(SimpleLookupWithUUID, MetadataFields):
    csas_requests = models.ManyToManyField(CSASRequest, blank=False)
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("tittle (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("tittle (fr)"))


class Meeting(SimpleLookup, MetadataFields):
    ''' meeting that is taking place under the umbrella of a csas process'''
    type_choices = (
        (1, _("CSAS Regional Advisory Process (RAP)")),
        (2, _("CSAS Science Management Meeting")),
        (3, _("CSAS Steering Committee Meeting")),
        (9, _("other")),
    )

    csas_request = models.ForeignKey(CSASRequest, related_name='meetings', on_delete=models.CASCADE, verbose_name=_("process"), editable=False)
    # basic
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"))
    proponent = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("proponent"))
    type = models.IntegerField(choices=type_choices, verbose_name=_("type of event"))
    start_date = models.DateTimeField(verbose_name=_("initial activity date"), blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_("anticipated end date"), blank=True, null=True)
    rsvp_email = models.EmailField(verbose_name=_("RSVP email address (on invitation)"))

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"), related_name="meetings",
                                    editable=False)

    class Meta:
        ordering = ['-updated_at', ]

    @property
    def attendees(self):
        return Attendance.objects.filter(invitee__event=self).order_by("invitee").values("invitee").distinct()

    @property
    def length_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1

    @property
    def display_dates(self):
        start = date(self.start_date) if self.start_date else "??"
        dates = f'{start}'
        if self.end_date and self.end_date != self.start_date:
            end = date(self.end_date)
            dates += f' &rarr; {end}'
        days_display = "{} {}{}".format(self.length_days, gettext("day"), pluralize(self.length_days))
        dates += f' ({days_display})'
        return dates


class MeetingNote(MetadataFields):
    ''' a note pertaining to a meeting'''
    type_choices = (
        (1, 'To Do'),
        (2, 'Next step'),
        (3, 'General comment'),
    )
    meeting = models.ForeignKey(Meeting, related_name='notes', on_delete=models.CASCADE)
    type = models.IntegerField(choices=type_choices, verbose_name=_("type"))
    note = models.TextField(verbose_name=_("note"))
    is_complete = models.BooleanField(default=False, verbose_name=_("complete?"))

    class Meta:
        ordering = ["is_complete", "-updated_at", ]


def resource_directory_path(instance, filename):
    return 'events/{0}/{1}'.format(instance.event.id, filename)


class MeetingResource(SimpleLookup, MetadataFields):
    ''' a file attached to to meeting'''
    meeting = models.ForeignKey(Meeting, related_name='resources', on_delete=models.CASCADE)

    # for an actual file hosted on dmapps
    file_en = models.FileField(upload_to=resource_directory_path, verbose_name=_("file attachment (English)"), blank=True, null=True)
    file_fr = models.FileField(upload_to=resource_directory_path, verbose_name=_("file attachment (French)"), blank=True, null=True)

    # for a file hosted somewhere else
    url_en = models.URLField(verbose_name=_("url (English)"), blank=True, null=True)
    url_fr = models.URLField(verbose_name=_("url (French)"), blank=True, null=True)

    @property
    def tfile(self):
        # check to see if a french value is given
        if getattr(self, gettext("file_en")):
            return getattr(self, gettext("file_en"))
        # if there is no translated term, just pull from the english field
        else:
            return self.file_en

    @property
    def turl(self):
        # check to see if a french value is given
        if getattr(self, gettext("url_en")):
            return getattr(self, gettext("url_en"))
        # if there is no translated term, just pull from the english field
        else:
            return self.url_en

    class Meta:
        ordering = [_("name")]


class Invitee(models.Model):
    ''' a person that was invited to a meeting'''
    # Choices for role
    role_choices = (
        (1, 'Participant'),
        (2, 'Chair'),
        (3, 'Expert'),
        (4, 'Steering Committee Member'),
    )
    status_choices = (
        (0, 'Invited'),
        (1, 'Accepted'),
        (2, 'Declined'),
        (9, 'No response'),
    )
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="meeting_invites")
    role = models.IntegerField(choices=role_choices, verbose_name=_("Function"), default=1)
    status = models.IntegerField(choices=status_choices, verbose_name=_("status"), default=0)
    invitation_sent_date = models.DateTimeField(verbose_name=_("date invitation was sent"), editable=False, blank=True, null=True)
    resources_received = models.ManyToManyField("MeetingResource", editable=False)

    class Meta:
        ordering = ['person__first_name', "person__last_name"]
        unique_together = (("meeting", "person"),)

    @property
    def attendance_fraction(self):
        return self.attendance.count() / self.meeting.length_days


class Attendance(models.Model):
    '''we will need to track on which days an invitee actually showed up'''
    invitee = models.ForeignKey(Invitee, on_delete=models.CASCADE, related_name="attendance", verbose_name=_("attendee"))
    date = models.DateTimeField(verbose_name=_("date"))

    class Meta:
        ordering = ['date']
        unique_together = (("invitee", "date"),)


class Document(MetadataFields):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, editable=False)
    meetings = models.ManyToManyField(Meeting, blank=True)
