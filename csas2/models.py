from uuid import uuid4

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import date, slugify, pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from markdown import markdown

from csas2 import model_choices
from lib.functions.custom_functions import fiscal_year
from lib.templatetags.custom_filters import percentage
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language, Person, Section, \
    SimpleLookupWithUUID


def request_directory_path(instance, filename):
    return 'csas/request_{0}/{1}'.format(instance.csas_request.id, filename)


class CSASRequest(MetadataFields):
    ''' csas request '''
    is_carry_over = models.BooleanField(default=False, choices=model_choices.yes_no_choices,
                                        verbose_name=_("Is this request a carry-over from a previous year?"))
    language = models.IntegerField(default=1, verbose_name=_("language of request"), choices=model_choices.language_choices)
    title = models.CharField(max_length=1000, verbose_name=_("title"))
    translated_title = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("translated title"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_coordinator_requests", verbose_name=_("Regional CSAS coordinator"),
                                    blank=True, null=True)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_client_requests", verbose_name=_("DFO client"), blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="csas_requests", verbose_name=_("section"), blank=True, null=True)
    is_multiregional = models.BooleanField(default=False,
                                           verbose_name=_("Does this request involve more than one region (zonal) or more than one client sector?"))
    multiregional_text = models.TextField(null=True, blank=True, verbose_name=_("Please provide the contact name, sector, and region for all involved."))

    issue = models.TextField(verbose_name=_("Issue requiring science information and/or advice"), blank=True, null=True,
                             help_text=_("Should be phrased as a question to be answered by Science"))
    had_assistance = models.BooleanField(default=False, verbose_name=_(
        "Have you had assistance from Science in developing the question/request?"), help_text=_("E.g. with CSAS and/or DFO science staff."))
    assistance_text = models.TextField(null=True, blank=True, verbose_name=_(" Please provide details about the assistance received"))

    rationale = models.TextField(verbose_name=_("Rationale or context for the request"), blank=True, null=True,
                                 help_text=_("What will the information/advice be used for? Who will be the end user(s)? Will it impact other DFO "
                                             "programs or regions?"))
    risk_text = models.TextField(null=True, blank=True, verbose_name=_("What is the expected consequence if science advice is not provided?"))
    advice_needed_by = models.DateTimeField(verbose_name=_("Latest possible date to receive Science advice"))
    rationale_for_timeline = models.TextField(null=True, blank=True, verbose_name=_("Rationale for deadline?"),
                                              help_text=_("e.g., COSEWIC or consultation meetings, Environmental Assessments, legal or regulatory "
                                                          "requirement, Treaty obligation, international commitments, etc)."
                                                          "Please elaborate and provide anticipatory dates"))
    has_funding = models.BooleanField(default=False, verbose_name=_("Do you have funds to cover any extra costs associated with this request?"),
                                      help_text=_("i.e., special analysis, meeting costs, translation)?"), )
    funding_text = models.TextField(null=True, blank=True, verbose_name=_("Please describe"))
    prioritization = models.IntegerField(blank=True, null=True, verbose_name=_("How would you classify the prioritization of this request?"),
                                         choices=model_choices.prioritization_choices)
    prioritization_text = models.TextField(blank=True, null=True, verbose_name=_("What is the rationale behind the prioritization?"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))

    # non-editable fields
    status = models.IntegerField(default=1, verbose_name=_("status"), choices=model_choices.request_status_choices, editable=False)
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("submission date"), editable=False)
    old_id = models.IntegerField(blank=True, null=True, editable=False)
    uuid = models.UUIDField(editable=False, unique=True, blank=True, null=True, default=uuid4, verbose_name=_("unique identifier"))

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="csas_requests",
                                    verbose_name=_("fiscal year"), editable=False)
    ref_number = models.CharField(blank=True, null=True, editable=False, verbose_name=_("reference number"), max_length=255)

    class Meta:
        ordering = ("fiscal_year", "title")
        verbose_name_plural = _("CSAS Requests")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if hasattr(self, "review"):
            self.ref_number = self.review.ref_number
            if self.review.advice_date:
                self.fiscal_year_id = fiscal_year(self.review.advice_date, sap_style=True)
        else:
            self.fiscal_year_id = fiscal_year(self.advice_needed_by, sap_style=True)

        # if there is a process, the request status will follow the process status
        if self.id and self.processes.exists():
            # if all processes linked to the request are complete, this request should also be complete
            if self.processes.filter(status=2).count() == self.processes.all().count():
                self.status = 4
            else:
                self.status = 11
        else:
            # look at the review to help determine the status
            self.status = 1  # draft
            if self.submission_date:
                self.status = 2  # submitted
            if hasattr(self, "review") and self.review.id:
                self.status = 3  # under review
                if self.review.decision:
                    self.status = self.review.decision + 10

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
    def risk_text_html(self):
        if self.risk_text:
            return mark_safe(markdown(self.risk_text))

    @property
    def multiregional_display(self):
        if self.is_multiregional:
            text = self.multiregional_text if self.multiregional_text else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")

    @property
    def status_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_status_display())}">{self.get_status_display()}</span>')

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

    @property
    def prioritization_display(self):
        if self.prioritization:
            text = self.prioritization_text if self.prioritization_text else gettext("no further detail provided.")
            return "{} - {}".format(self.get_prioritization_display(), text)
        return gettext("---")

    @property
    def branch(self):
        return self.section.division.branch.tname

    @property
    def region(self):
        return self.section.division.branch.region.tname


class CSASRequestReview(MetadataFields):
    csas_request = models.OneToOneField(CSASRequest, on_delete=models.CASCADE, related_name="review")
    ref_number = models.CharField(max_length=50, verbose_name=_("reference number (optional)"), blank=True, null=True)
    prioritization = models.IntegerField(blank=True, null=True, verbose_name=_("prioritization"), choices=model_choices.prioritization_choices)
    prioritization_text = models.TextField(blank=True, null=True, verbose_name=_("prioritization notes"))
    decision = models.IntegerField(blank=True, null=True, verbose_name=_("decision"), choices=model_choices.request_decision_choices)
    decision_text = models.TextField(blank=True, null=True, verbose_name=_("Decision explanation"))
    decision_date = models.DateTimeField(null=True, blank=True, verbose_name=_("decision date"))
    advice_date = models.DateTimeField(verbose_name=_("date to provide Science advice"), blank=True, null=True)
    is_deferred = models.BooleanField(default=False, verbose_name=_("was the original request date deferred?"))
    deferred_text = models.TextField(null=True, blank=True, verbose_name=_("Please provide rationale for the deferred date"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("administrative notes"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(gettext("Review for CSAS Request #"), self.csas_request.id)

    @property
    def decision_display(self):
        if self.decision:
            text = self.decision_text if self.decision_text else gettext("no further detail provided.")
            return "{} - {} ({})".format(self.get_decision_display(), text, date(self.decision_date))
        return gettext("---")

    @property
    def prioritization_display(self):
        if self.prioritization:
            text = self.prioritization_text if self.prioritization_text else gettext("no further detail provided.")
            return "{} - {}".format(self.get_prioritization_display(), text)
        return gettext("---")

    @property
    def deferred_display(self):
        if self.is_deferred:
            text = self.deferred_text if self.deferred_text else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")


class CSASRequestFile(models.Model):
    csas_request = models.ForeignKey(CSASRequest, related_name="files", on_delete=models.CASCADE, editable=False)
    caption = models.CharField(max_length=255)
    file = models.FileField(upload_to=request_directory_path)
    date_created = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.caption


class Process(SimpleLookupWithUUID, MetadataFields):
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (fr)"))
    status = models.IntegerField(choices=model_choices.process_status_choices, verbose_name=_("status"), default=1)
    scope = models.IntegerField(verbose_name=_("scope"), choices=model_choices.process_scope_choices)
    type = models.IntegerField(verbose_name=_("type"), choices=model_choices.process_type_choices)
    lead_region = models.ForeignKey(Region, blank=True, on_delete=models.DO_NOTHING, related_name="process_lead_regions", verbose_name=_("lead region"))
    other_regions = models.ManyToManyField(Region, blank=True, verbose_name=_("other regions"))
    csas_requests = models.ManyToManyField(CSASRequest, blank=True, related_name="processes", verbose_name=_("Connected CSAS requests"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_coordinator_processes", verbose_name=_("Lead coordinator"))
    advisors = models.ManyToManyField(User, blank=True, verbose_name=_("DFO Science advisors"))
    context = models.TextField(blank=True, null=True, verbose_name=_("context"))
    objectives = models.TextField(blank=True, null=True, verbose_name=_("objectives"))
    expected_publications = models.TextField(blank=True, null=True, verbose_name=_("expected publications"))

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="processes",
                                    verbose_name=_("fiscal year"), editable=False)

    class Meta:
        ordering = ["fiscal_year", _("name")]

    def save(self, *args, **kwargs):
        # if this is a new record, populate fy based on current time
        if not self.fiscal_year:
            self.fiscal_year_id = fiscal_year(timezone.now(), sap_style=True)
        # if there is a meeting, look to the latest meeting to determine fy
        elif self.meetings.exists():
            self.fiscal_year_id = fiscal_year(self.meetings.order_by("start_date").last().start_date, sap_style=True)
        # otherwise, look to the creation date
        else:
            self.fiscal_year_id = fiscal_year(self.created_at, sap_style=True)

        super().save(*args, **kwargs)

    @property
    def status_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_status_display())}">{self.get_status_display()}</span>')

    def get_absolute_url(self):
        return reverse("csas2:process_detail", args=[self.pk])

    @property
    def context_html(self):
        if self.context:
            return mark_safe(markdown(self.context))

    @property
    def objectives_html(self):
        if self.objectives:
            return mark_safe(markdown(self.objectives))

    @property
    def expected_publications_html(self):
        if self.expected_publications:
            return mark_safe(markdown(self.expected_publications))

    @property
    def scope_type(self):
        return f"{self.get_scope_display()} {self.get_type_display()}"


class GenericCost(models.Model):
    cost_category = models.IntegerField(choices=model_choices.cost_category_choices, verbose_name=_("cost category"))
    description = models.CharField(max_length=1000, blank=True, null=True)
    funding_source = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"))

    def save(self, *args, **kwargs):
        if not self.amount: self.amount = 0
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class GenericNote(MetadataFields):
    type = models.IntegerField(choices=model_choices.note_type_choices, verbose_name=_("type"))
    note = models.TextField(verbose_name=_("note"))
    is_complete = models.BooleanField(default=False, verbose_name=_("complete?"))

    class Meta:
        abstract = True
        ordering = ["is_complete", "-updated_at", ]


class Meeting(MetadataFields):
    ''' meeting that is taking place under the umbrella of a csas process'''
    process = models.ForeignKey(Process, related_name='meetings', on_delete=models.CASCADE, verbose_name=_("process"), editable=False)
    type = models.IntegerField(choices=model_choices.meeting_type_choices, verbose_name=_("type of meeting"))
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"), help_text=_("City, State/Province, Country"))
    start_date = models.DateTimeField(verbose_name=_("initial activity date"))
    end_date = models.DateTimeField(verbose_name=_("anticipated end date"))
    # rsvp_email = models.EmailField(verbose_name=_("RSVP email address (on invitation)"))
    hide_from_list = models.BooleanField(default=False, verbose_name=_("This record should be hidden from the main search page"), )

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"), related_name="meetings",
                                    editable=False)

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.start_date, sap_style=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_type_display() + f" ({self.start_date.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['start_date', ]

    def get_absolute_url(self):
        return reverse("csas2:meeting_detail", args=[self.pk])

    @property
    def attendees(self):
        return Attendance.objects.filter(invitee__meeting=self).order_by("invitee").values("invitee").distinct()

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

    @property
    def total_cost(self):
        return self.costs.aggregate(dsum=Sum("amount"))["dsum"]


class MeetingNote(GenericNote):
    ''' a note pertaining to a meeting'''
    meeting = models.ForeignKey(Meeting, related_name='notes', on_delete=models.CASCADE)


class MeetingResource(SimpleLookup, MetadataFields):
    ''' a file attached to to meeting'''
    meeting = models.ForeignKey(Meeting, related_name='resources', on_delete=models.CASCADE)
    url_en = models.URLField(verbose_name=_("url (English)"), blank=True, null=True, max_length=2000)
    url_fr = models.URLField(verbose_name=_("url (French)"), blank=True, null=True, max_length=2000)

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


class MeetingCost(GenericCost):
    meeting = models.ForeignKey(Meeting, related_name='costs', on_delete=models.CASCADE)


class InviteeRole(SimpleLookup):
    pass

class Invitee(models.Model):
    ''' a person that was invited to a meeting'''
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="meeting_invites")
    roles = models.ManyToManyField(InviteeRole, verbose_name=_("Function(s)"))
    # role = models.IntegerField(choices=model_choices.invitee_role_choices, verbose_name=_("Function"), default=1)
    status = models.IntegerField(choices=model_choices.invitee_status_choices, verbose_name=_("status"), default=0)
    invitation_sent_date = models.DateTimeField(verbose_name=_("date invitation was sent"), editable=False, blank=True, null=True)
    resources_received = models.ManyToManyField("MeetingResource", editable=False)

    class Meta:
        ordering = ['person__first_name', "person__last_name"]
        unique_together = (("meeting", "person"),)

    @property
    def attendance_fraction(self):
        return self.attendance.count() / self.meeting.length_days

    @property
    def attendance_display(self):
        if not self.attendance.exists():
            return "---"
        else:
            days = self.attendance.count()
            return "{} {}{} ({})".format(days, gettext("day"), pluralize(days), percentage(self.attendance_fraction, 0))


class Attendance(models.Model):
    '''we will need to track on which days an invitee actually showed up'''
    invitee = models.ForeignKey(Invitee, on_delete=models.CASCADE, related_name="attendance", verbose_name=_("attendee"))
    date = models.DateTimeField(verbose_name=_("date"))

    class Meta:
        ordering = ['date']
        unique_together = (("invitee", "date"),)


class Series(SimpleLookup):
    pass


class Document(MetadataFields):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="documents", editable=False)
    type = models.IntegerField(choices=model_choices.document_type_choices, verbose_name=_("type"))
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name=_("series"))
    title_en = models.CharField(max_length=255, verbose_name=_("title (English)"), blank=True, null=True)
    title_fr = models.CharField(max_length=255, verbose_name=_("title (French)"), blank=True, null=True)
    title_in = models.CharField(max_length=255, verbose_name=_("title (Inuktitut)"), blank=True, null=True)
    year = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)], verbose_name=_("Publication Year"))
    pub_number = models.CharField(max_length=25, verbose_name=_("publication number"), blank=True, null=True)
    pages = models.IntegerField(null=True, blank=True, verbose_name=_("pages"))
    url_en = models.URLField(verbose_name=_("document url (English)"), blank=True, null=True, max_length=2000)
    url_fr = models.URLField(verbose_name=_("document url (French)"), blank=True, null=True, max_length=2000)
    hide_from_list = models.BooleanField(default=False, verbose_name=_("This record should be hidden from the main search page"), )

    # non-editable
    meetings = models.ManyToManyField(Meeting, blank=True, related_name="documents", verbose_name=_("csas meeting linkages"), editable=False)
    people = models.ManyToManyField(Person, verbose_name=_("authors"), editable=False, through="Author")
    status = models.IntegerField(default=1, verbose_name=_("status"), choices=model_choices.document_status_choices, editable=False)
    old_id = models.IntegerField(blank=True, null=True, editable=False)

    def get_absolute_url(self):
        return reverse("csas2:document_detail", args=[self.pk])

    @property
    def ttitle(self):
        # check to see if a french value is given
        if getattr(self, str(_("title_en"))):
            my_str = "{}".format(getattr(self, str(_("title_en"))))
        else:
            my_str = self.title_en
        return my_str

    def __str__(self):
        return self.ttitle

    @property
    def total_cost(self):
        return self.costs.aggregate(dsum=Sum("amount"))["dsum"]


class DocumentNote(GenericNote):
    ''' a note pertaining to a meeting'''
    document = models.ForeignKey(Document, related_name='notes', on_delete=models.CASCADE)


class DocumentCost(GenericCost):
    document = models.ForeignKey(Document, related_name='costs', on_delete=models.CASCADE)


class DocumentTracking(MetadataFields):
    ''' since not all docs from meetings will be tracked, we will establish a 1-1 relationship to parse out tracking process'''
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name="tracking")
#     # administrative
#     date_due = models.DateField(null=True, blank=True, verbose_name=_("due date"))
#     date_submitted = models.DateField(null=True, blank=True, verbose_name=_("Date Submitted by Author"), )
#     submitted_by = models.ManyToManyField(ConContact, blank=True, related_name="submitted_by", verbose_name=_("Submitted By"))
#     date_appr_by_chair = models.DateField(null=True, blank=True, verbose_name=_("Date Approved by Chair"), )
#     appr_by_chair = models.ManyToManyField(ConContact, blank=True, related_name="appr_by_chair", verbose_name=_("Approved By (Chair)"))
#     data_appr_by_CSAS = models.DateField(null=True, blank=True, verbose_name=_("Date Approved by CSAS"), )
#     appr_by_CSAS = models.ManyToManyField(ConContact, blank=True, related_name="appr_by_CSAS", verbose_name=_("Approved By (CSAS Contact)"))
#     date_appr_by_dir = models.DateField(null=True, blank=True, verbose_name=_("Date Approved by Director"), )
#     appr_by_dir = models.ManyToManyField(ConContact, blank=True, related_name="appr_by_dir", verbose_name=_("Approved By Director"))
#     date_num_req = models.DateField(null=True, blank=True, verbose_name=_("Date Number Requested"), )
#     date_doc_submitted = models.DateField(null=True, blank=True, verbose_name=_("Date Document Submitted to CSAS"), )
#     date_pdf_proof = models.DateField(null=True, blank=True, verbose_name=_("Date PDF Proof Sent to Author"), )
#     appr_by = models.ManyToManyField(ConContact, blank=True, related_name="appr_by", verbose_name=_("Approved by (PDF Proof)"))
#     date_anti = models.DateField(null=True, blank=True, verbose_name=_("Date of Anticipated Posting"), )
#     date_posted = models.DateField(null=True, blank=True, verbose_name=_("Date Posted"), )
#     date_modify = models.DateField(null=True, blank=True, verbose_name=_("Date Modified"), )
#     notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))
#
#     trans_status = models.ForeignKey(PtsPublicationTransStatus, on_delete=models.DO_NOTHING, verbose_name=_("Translation Status"))
#     date_to_trans = models.DateField(null=True, blank=True, verbose_name=_("Date Sent to Translation"), )
#     client_ref_num = models.CharField(default="NA", max_length=255, verbose_name=_("Client Reference Number"))
#     target_lang = models.ForeignKey(PtlPublicationTargetLanguage, on_delete=models.DO_NOTHING, verbose_name=_("Target Language"))
#     trans_ref_num = models.CharField(default="NA", max_length=255, verbose_name=_("Translator Reference Number"))
#     urgent_req = models.ForeignKey(PurPublicationUrgentRequest, on_delete=models.DO_NOTHING, verbose_name=_("Urgent Request"))
#     date_fr_trans = models.DateField(null=True, blank=True, verbose_name=_("Date Back from Translation"), )
#     invoice_num = models.CharField(default="NA", max_length=255, verbose_name=_("Invoice Number"))
#     attach = models.CharField(default="NA", max_length=255, verbose_name=_("Attachment(s)"))
#     trans_note = models.TextField(null=True, blank=True, verbose_name=_("Translation Notes"))
#
#     p1 = models.CharField(max_length=1, blank=True, verbose_name=_(""))
#     attach_en_file = models.CharField(default="NA", max_length=255, verbose_name=_("Attachment (English) File"))
#     attach_en_size = models.CharField(default="NA", max_length=255, verbose_name=_("Attachment (English) Size"))
#     attach_fr_file = models.CharField(default="NA", max_length=255, verbose_name=_("Attachment (French) File"))
#     attach_fr_size = models.CharField(default="NA", max_length=255, verbose_name=_("Attachment (French) Size"))
#
#     url_e_file = models.URLField(_("URL (English)"), max_length=255, db_index=True, unique=True, blank=True)
#     url_f_file = models.URLField(_("URL (French)"), max_length=255, db_index=True, unique=True, blank=True)
#
#     dev_link_e_file = models.URLField(_("Dev Link (English)"), max_length=255, db_index=True, unique=True, blank=True)
#     dev_link_f_file = models.URLField(_("Dev Link (French)"), max_length=255, db_index=True, unique=True, blank=True)
#
#     ekme_gcdocs_e_file = models.CharField(default="NA", max_length=255, verbose_name=_("EKME# GCDocs (English)"))
#     ekme_gcdocs_f_file = models.CharField(default="NA", max_length=255, verbose_name=_("EKME# GCDocs (French)"))
#
#     lib_cat_e_file = models.CharField(default="NA", max_length=255, verbose_name=_("Library Catalogue # (English)"))
#     lib_cat_f_file = models.CharField(default="NA", max_length=255, verbose_name=_("Library Catalogue # (French)"))
#
#
#     # tracking
#
#     class Meta:
#         ordering = ['-id']


class Author(models.Model):
    ''' a person that was invited to a meeting'''
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="authors")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="authorship")
    is_lead = models.BooleanField(default=False, verbose_name=_("lead author?"))

    class Meta:
        ordering = ['person__first_name', "person__last_name"]
        unique_together = (("document", "person"),)
