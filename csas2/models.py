from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date
from django.utils.translation import gettext_lazy as _, gettext

from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language, Person


# We will be using the following models from shared models:
# citations
# person
# organization
# DFO ORGS (region, section etc.)


class Process(SimpleLookup, MetadataFields):
    ''' csas process '''

    # TODO: MAKE ME A CHOICE FIELD
    type = models.IntegerField(blank=True, null=True, verbose_name=_("Request Type"))
    assigned_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Assigned Request Number"))
    in_year_request = models.BooleanField(null=True, blank=True, verbose_name=_("In-Year Request"))

    # todo: not possible to have multiple regions ? (DJF)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("Region"))

    # todo: can we use Branch and Sector shared models? Masterlist has a model called sector. It is very problematic.
    # directorate_branch = models.ManyToManyField(BraBranch, blank=True, verbose_name=_("Directorate Branch"))
    # client_sector = models.IntegerField(blank=True, null=True, verbose_name=_("Client Sector"))

    # TODO: is this not already in the person table?
    client_title = models.CharField(max_length=255, verbose_name=_("Client Title"))

    # todo: is this not implied by which regions are involved? can this be a prop?
    zonal = models.BooleanField(null=True, blank=True, verbose_name=_("Zonal"))
    zonal_text = models.TextField(null=True, blank=True, verbose_name=_("Zonal Text"))

    issue = models.TextField(verbose_name=_("Issue"),
                             help_text=_("Issue requiring science information and/or advice. Posted as a question "
                                         "to be answered by Science."))
    consequence_text = models.TextField(null=True, blank=True, verbose_name=_("Consequence Text"))

    assistance = models.BooleanField(null=True, blank=True, verbose_name=_("Assistance"))
    assistance_text = models.TextField(null=True, blank=True, verbose_name=_("Assistance Text"))

    # TODO: MAKE ME A CHOICE FIELD
    priority = models.IntegerField(blank=True, null=True, verbose_name=_("Priority"))
    rationale = models.TextField(verbose_name=_("Rationale for Request"),
                                 help_text=_("Rationale or context for the request: What will the information/advice "
                                             "be used for? Who will be the end user(s)? Will it impact other DFO "
                                             "programs or regions?"))

    # TODO: MAKE ME A CHOICE FIELD
    proposed_timing = models.IntegerField(blank=True, null=True, verbose_name=_("Proposed Timing"),
                                        help_text=_("Latest possible date to receive Science Advice."))
    rationale_for_timing = models.TextField(verbose_name=_("Rationale for Timing"), help_text=_("Explain rationale for proposed timing."))

    funding = models.BooleanField(help_text=_("Do you have funds to cover extra costs associated with this request?"))
    funding_notes = models.TextField(max_length=512, verbose_name=_("Funding Notes"))

    science_discussion = models.BooleanField(verbose_name=_("Science Discussion"),
                                             help_text=_("Have you talked to Science about this request?"))
    science_discussion_notes = models.CharField(max_length=100, verbose_name=_("Science Discussion Notes"),
                                                help_text=_("If you have talked to Science about this request, "
                                                            "to whom have you talked?"))

    # section for links to people
    clients = models.ManyToManyField(Person, blank=True, related_name="client_name", verbose_name=_("Client Name"))
    managers = models.ManyToManyField(Person, blank=True, related_name="manager_name", verbose_name=_("Manager Name"))
    coordinators = models.ManyToManyField(Person, blank=True, related_name="coordinator_name", verbose_name=_("Coordinator Name"))
    # todo: needs clarification. Are we talking about sector heads? if so, could these data be stored in a different table? I suspect this is a redundant field
    directors = models.ManyToManyField(Person, blank=True, related_name="director_name", verbose_name=_("Director Name"))

    submission_date = models.DateField(null=True, blank=True, verbose_name=_("Submission Date"), help_text=_("Format: YYYY-MM-DD."))
    adviser_submission = models.DateField(null=True, blank=True, verbose_name=_("Client Adviser Submission Date"), help_text=_("Format: YYYY-MM-DD."))
    rd_submission = models.DateField(null=True, blank=True, verbose_name=_("Client RD Submission Date"), help_text=_("Format: YYYY-MM-DD."))
    received_date = models.DateField(null=True, blank=True, verbose_name=_("Received Date"), help_text=_("Format: YYYY-MM-DD."))
    signature = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Signature"))

    # TODO: MAKE ME A CHOICE FIELD
    status = models.IntegerField(blank=True, null=True, verbose_name=_("Status"))
    # TODO: what language? can we not just have title_en, title_fr ...
    trans_title = models.CharField(max_length=255, verbose_name=_("Translated Title"))

    # TODO: MAKE ME A CHOICE FIELD
    decision = models.IntegerField(blank=True, null=True, verbose_name=_("Decision"))

    # TODO: MAKE ME A CHOICE FIELD - This is also a weird dropdown...
    decision_exp = models.IntegerField(blank=True, null=True, verbose_name=_("Decision Explanation"))
    rationale_for_decision = models.TextField(null=True, blank=True, verbose_name=_("Rationale for Decision"))
    decision_date = models.DateField(null=True, blank=True, verbose_name=_("Decision Date"), help_text=_("Format: YYYY-MM-DD."))

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ['-id']


class Meeting(SimpleLookup, MetadataFields):
    ''' meeting that is taking place under the umbrella of a csas process'''
    type_choices = (
        (1, _("CSAS Regional Advisory Process (RAP)")),
        (2, _("CSAS Science Management Meeting")),
        (3, _("CSAS Steering Committee Meeting")),
        (9, _("other")),
    )

    process = models.ForeignKey(Process, related_name='meetings', on_delete=models.CASCADE, verbose_name=_("process"), editable=False)
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
    event = models.ForeignKey(Meeting, related_name='resources', on_delete=models.CASCADE)

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
