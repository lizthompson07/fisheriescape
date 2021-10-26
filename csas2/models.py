from datetime import timedelta
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import date, slugify, pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext, get_language, activate
from markdown import markdown

from csas2 import model_choices
from csas2.utils import get_quarter
from lib.functions.custom_functions import fiscal_year, listrify
from lib.templatetags.custom_filters import percentage
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language, Person, Section, \
    SimpleLookupWithUUID

NULL_YES_NO_CHOICES = (
    (None, _("Unsure")),
    (1, _("Yes")),
    (0, _("No")),
)

YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


def request_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    file = filename.split(".")[0]
    return 'csas/request_{0}/{1}.{2}'.format(instance.csas_request.id, slugify(file), ext)


def meeting_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    file = filename.split(".")[0]
    return 'csas/meeting_{0}/{1}.{2}'.format(instance.meeting.id, slugify(file), ext)


def doc_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    file = filename.split(".")[0]
    return 'csas/document_{0}/{1}'.format(instance.id, filename)


class CSASAdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="csas_admin_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="csas_admin_user", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_national_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_national_admin", "user__first_name", ]


class GenericFile(models.Model):
    caption = models.CharField(max_length=255, verbose_name=_("caption"))
    file = models.FileField()
    date_created = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['-date_created']

    def __str__(self):
        return self.caption


class GenericCost(models.Model):
    cost_category = models.IntegerField(choices=model_choices.cost_category_choices, verbose_name=_("cost category"))
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("description"))
    funding_source = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("funding source"))
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

    @property
    def last_modified(self):
        by = self.updated_by if self.updated_by else self.created_by
        return mark_safe(f"{date(self.updated_at)} &mdash; {by}")


class CSASRequest(MetadataFields):
    ''' csas request '''
    language = models.IntegerField(default=1, verbose_name=_("language of request"), choices=model_choices.language_choices)
    title = models.CharField(max_length=1000, verbose_name=_("title"))
    translated_title = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("translated title"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_coordinator_requests", verbose_name=_("CSAS coordinator"),
                                    blank=True, null=False)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_client_requests", verbose_name=_("DFO client"), blank=True, null=False)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="csas_requests", verbose_name=_("section"), blank=True, null=False)
    is_multiregional = models.IntegerField(default=False, choices=NULL_YES_NO_CHOICES, blank=True, null=True,
                                           verbose_name=_("Could the advice provided potentially be applicable to other regions and/or sectors?"),
                                           help_text=_(
                                               "e.g., frameworks, tools, issues and/or aquatic species widely distributed throughout more than one region"))
    multiregional_text = models.TextField(null=True, blank=True, verbose_name=_("Please list other sectors and/or regions and provide brief rationale"))

    issue = models.TextField(verbose_name=_("Issue requiring science information and/or advice"), blank=True, null=True,
                             help_text=_(
                                 "Should be phrased as a question to be answered by Science. The text provided here will serve as the objectives for the terms of reference."))
    assistance_text = models.TextField(null=True, blank=True, verbose_name=_(
        "From whom in Science have you had assistance in developing the question/request (CSAS and/or DFO science staff)"))

    rationale = models.TextField(verbose_name=_("Rationale or context for the request"), blank=True, null=True,
                                 help_text=_("What will the information/advice be used for? Who will be the end user(s)? Will it impact other DFO "
                                             "programs or regions? The text provided here will serve as the context for the terms of reference."))
    risk_text = models.TextField(null=True, blank=True, verbose_name=_("What is the expected consequence if science advice is not provided?"))
    advice_needed_by = models.DateTimeField(verbose_name=_("Latest possible date to receive Science advice"))
    rationale_for_timeline = models.TextField(null=True, blank=True, verbose_name=_("Rationale for deadline?"),
                                              help_text=_("e.g., COSEWIC or consultation meetings, Environmental Assessments, legal or regulatory "
                                                          "requirement, Treaty obligation, international commitments, etc)."
                                                          " Please elaborate and provide anticipatory dates"))
    has_funding = models.BooleanField(default=False, verbose_name=_("Click here if you have funds to cover any extra costs associated with this request?"),
                                      help_text=_("i.e., special analysis, meeting costs, translation)?"), )
    funding_text = models.TextField(null=True, blank=True, verbose_name=_("Please describe"))
    prioritization = models.IntegerField(blank=True, null=True, verbose_name=_("How would you classify the prioritization of this request?"),
                                         choices=model_choices.prioritization_choices)
    prioritization_text = models.TextField(blank=True, null=True, verbose_name=_("What is the rationale behind the prioritization?"))

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
        verbose_name = _("CSAS Request")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if hasattr(self, "review"):
            self.ref_number = self.review.ref_number
            if self.review.advice_date:
                self.fiscal_year_id = fiscal_year(self.review.advice_date, sap_style=True)
        else:
            self.fiscal_year_id = fiscal_year(self.advice_needed_by, sap_style=True)


        # set the STATUS
        # if there is a process, the request the request MUST have been approved.
        if self.id and self.processes.exists():
            if self.processes.filter(status=100).count() == self.processes.all().count():
                self.status = 5  # fulfilled
            elif self.processes.filter(status=90).count() == self.processes.all().count():
                self.status = 12  # withdrawn
            else:
                self.status = 11  # accepted
        else:
            # look at the review to help determine the status
            self.status = 1  # draft
            if self.submission_date:
                self.status = 2  # submitted
            if self.files.filter(is_approval=True).exists():
                self.status = 3  # approved
            if hasattr(self, "review") and self.review.id:
                self.status = 4  # under review
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
        display = self.get_is_multiregional_display()
        if self.is_multiregional == 1:
            text = self.multiregional_text if self.multiregional_text else gettext("no further details provided.")
            return "{} - {}".format(display, text)
        return display

    @property
    def status_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_status_display())}">{self.get_status_display()}</span>')

    @property
    def status_class(self):
        lang = get_language()
        activate("en")
        mystr = slugify(self.get_status_display()) if self.status else ""
        activate(lang)
        return mystr

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
    def sector(self):
        return self.section.division.branch.sector.tname

    @property
    def region(self):
        return self.section.division.branch.region.tname

    @property
    def has_process(self):
        return self.processes.exists()

    @property
    def is_complete(self):
        required_fields = [
            'language',
            'title',
            'coordinator',
            'client',
            'section',
            'issue',
            'assistance_text',
            'rationale',
            'risk_text',
            'advice_needed_by',
            'rationale_for_timeline',
            'prioritization',
        ]
        for field in required_fields:
            if getattr(self, field) in [None, ""]:
                return False
        return True

    @property
    def target_advice_date(self):
        if hasattr(self, "review") and self.review.advice_date:
            return self.review.advice_date
        return self.advice_needed_by


class CSASRequestNote(GenericNote):
    ''' a note pertaining to a csas request'''
    csas_request = models.ForeignKey(CSASRequest, related_name='notes', on_delete=models.CASCADE)


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


class CSASRequestFile(GenericFile):
    csas_request = models.ForeignKey(CSASRequest, related_name="files", on_delete=models.CASCADE, editable=False)
    is_approval = models.BooleanField(default=False, verbose_name=_("is this file an approval for this request?"), choices=YES_NO_CHOICES)
    file = models.FileField(upload_to=request_directory_path)


class Process(SimpleLookupWithUUID, MetadataFields):
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (fr)"))
    status = models.IntegerField(choices=model_choices.get_process_status_choices(), verbose_name=_("status"), default=1)
    scope = models.IntegerField(verbose_name=_("scope"), choices=model_choices.process_scope_choices)
    type = models.IntegerField(verbose_name=_("type"), choices=model_choices.process_type_choices)
    lead_region = models.ForeignKey(Region, blank=True, on_delete=models.DO_NOTHING, related_name="process_lead_regions", verbose_name=_("lead region"))
    other_regions = models.ManyToManyField(Region, blank=True, verbose_name=_("other regions"))
    csas_requests = models.ManyToManyField(CSASRequest, blank=True, related_name="processes", verbose_name=_("Connected CSAS requests"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_coordinator_processes", verbose_name=_("Lead coordinator"),
                                    blank=True)
    advisors = models.ManyToManyField(User, blank=True, verbose_name=_("DFO Science advisors"))
    editors = models.ManyToManyField(User, blank=True, verbose_name=_("process editors"), related_name="process_editors",
                                     help_text=_("A list of non-CSAS staff with permissions to edit the process, meetings and documents"))
    advice_date = models.DateTimeField(verbose_name=_("Target date for to provide Science advice"), blank=True, null=True)

    # non-editable
    is_posted = models.BooleanField(default=False, verbose_name=_("is posted on CSAS website?"))
    posting_request_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("Date of posting request"))
    posting_notification_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("Posting notification date"))
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, related_name="processes", verbose_name=_("fiscal year"), editable=False)

    # calculated

    class Meta:
        ordering = ["fiscal_year", _("name")]

    def save(self, *args, **kwargs):
        # if there is no advice date, take the target date from the first attached request
        if not self.advice_date and self.id and self.csas_requests.exists():
            self.advice_date = self.csas_requests.first().target_advice_date

        # if there is an advice date, FY should follow it..
        if self.advice_date:
            self.fiscal_year_id = fiscal_year(self.advice_date, sap_style=True)
        else:
            self.fiscal_year_id = fiscal_year(timezone.now(), sap_style=True)

        # set the STATUS of the process
        # if the status is withdrawn, not further logic should be pursued.
        if not self.status == 90:

            # if there is a process, the request the request MUST have been approved.
            if hasattr(self, "tor") and self.tor.is_complete:
                self.status = 22  # tor complete!

            # has the latest scheduled meeting passed
            now = timezone.now()
            meeting_qs = self.meetings.filter(is_planning=False, is_estimate=False).order_by("end_date")
            if meeting_qs.exists() and meeting_qs.last().end_date and meeting_qs.last().end_date <= now:
                self.status = 25  # meeting complete!

            # has the key doc been completed
            doc_qs = self.documents.filter(status__in=[12, 17])
            if doc_qs.exists():
                self.status = 100  # complete!

        super().save(*args, **kwargs)

    # @property
    # def status_display(self):
    #     return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_status_display())}">{self.get_status_display()}</span>')
    #
    # @property
    # def status_class(self):
    #     return slugify(self.get_status_display()) if self.status else ""

    @property
    def status_display(self):
        stage = model_choices.get_process_status_lookup().get(self.status).get("stage")
        return mark_safe(f'<span class=" px-1 py-1 {stage}">{self.get_status_display()}</span>')

    @property
    def status_class(self):
        try:
            return model_choices.get_process_status_lookup().get(self.status).get("stage")
        except:
            pass

    def get_absolute_url(self):
        return reverse("csas2:process_detail", args=[self.pk])

    @property
    def scope_type(self):
        return f"{self.get_scope_display()} {self.get_type_display()}"

    @property
    def chair(self):
        if hasattr(self, "tor") and self.tor.meeting:
            return self.tor.meeting.chair

    @property
    def client_sectors(self):
        return listrify(set([r.section for r in self.csas_requests.all()]))

    @property
    def science_leads(self):
        qs = Person.objects.filter(meeting_invites__meeting__process=self, meeting_invites__roles__category=4).distinct()
        if qs.exists():
            return listrify([f"{person}" for person in qs])

    @property
    def client_leads(self):
        qs = Person.objects.filter(meeting_invites__meeting__process=self, meeting_invites__roles__category=2).distinct()
        if qs.exists():
            return listrify([f"{person}" for person in qs])

    @property
    def committee_members(self):
        qs = Person.objects.filter(meeting_invites__meeting__process=self, meeting_invites__roles__category=3).distinct()
        if qs.exists():
            return listrify([f"{person}" for person in qs])

    @property
    def regions(self):
        mystr = self.lead_region
        if self.other_regions.exists():
            mystr = f"<b><u>{mystr}</u></b>"
            mystr += f", {listrify(self.other_regions.all())}"
        return mystr


class ProcessCost(GenericCost):
    process = models.ForeignKey(Process, related_name='costs', on_delete=models.CASCADE, verbose_name=_("process"))


class TermsOfReference(MetadataFields):
    process = models.OneToOneField(Process, on_delete=models.CASCADE, related_name="tor", editable=False)
    context_en = models.TextField(blank=True, null=True, verbose_name=_("context (en)"), help_text=_("English"))
    context_fr = models.TextField(blank=True, null=True, verbose_name=_("context (fr)"), help_text=_("French"))
    objectives_en = models.TextField(blank=True, null=True, verbose_name=_("objectives (en)"), help_text=_("English"))
    objectives_fr = models.TextField(blank=True, null=True, verbose_name=_("objectives (fr)"), help_text=_("French"))
    participation_en = models.TextField(blank=True, null=True, verbose_name=_("participation (en)"), help_text=_("English"))
    participation_fr = models.TextField(blank=True, null=True, verbose_name=_("participation (fr)"), help_text=_("French"))
    references_en = models.TextField(blank=True, null=True, verbose_name=_("references (en)"), help_text=_("English"))
    references_fr = models.TextField(blank=True, null=True, verbose_name=_("references (fr)"), help_text=_("French"))
    meeting = models.OneToOneField("Meeting", blank=True, null=True, on_delete=models.DO_NOTHING, related_name="tor",
                                   verbose_name=_("Linked to which meeting?"),
                                   help_text=_("The ToR will pull several fields from the linked meeting (e.g., dates, chair, location, ...)"))
    expected_document_types = models.ManyToManyField("DocumentType", blank=True, verbose_name=_("expected publications"))
    is_complete = models.BooleanField(default=False, verbose_name=_("Are the ToRs complete?"), choices=YES_NO_CHOICES,
                                      help_text=_("Selecting yes will update the process status"))

    @property
    def context_en_html(self):
        if self.context_en:
            return mark_safe(markdown(self.context_en))

    @property
    def objectives_en_html(self):
        if self.objectives_en:
            return mark_safe(markdown(self.objectives_en))

    @property
    def participation_en_html(self):
        if self.participation_en:
            return mark_safe(markdown(self.participation_en))

    @property
    def references_en_html(self):
        if self.references_en:
            return mark_safe(markdown(self.references_en))

    @property
    def context_fr_html(self):
        if self.context_fr:
            return mark_safe(markdown(self.context_fr))

    @property
    def objectives_fr_html(self):
        if self.objectives_fr:
            return mark_safe(markdown(self.objectives_fr))

    @property
    def participation_fr_html(self):
        if self.participation_fr:
            return mark_safe(markdown(self.participation_fr))

    @property
    def references_fr_html(self):
        if self.references_fr:
            return mark_safe(markdown(self.references_fr))


class ProcessNote(GenericNote):
    ''' a note pertaining to a process'''
    process = models.ForeignKey(Process, related_name='notes', on_delete=models.CASCADE)


class Meeting(SimpleLookup, MetadataFields):
    ''' meeting that is taking place under the umbrella of a csas process'''
    process = models.ForeignKey(Process, related_name='meetings', on_delete=models.CASCADE, verbose_name=_("process"), editable=False)
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (fr)"))
    is_planning = models.BooleanField(default=False, choices=model_choices.yes_no_choices, verbose_name=_("Is this a planning meeting?"))
    is_virtual = models.BooleanField(default=False, choices=model_choices.yes_no_choices, verbose_name=_("Is this a virtual meeting?"))
    location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("location"),
                                help_text=_("City, State/Province, Country or Virtual"))
    start_date = models.DateTimeField(verbose_name=_("initial activity date"), null=True)
    end_date = models.DateTimeField(verbose_name=_("anticipated end date"), null=True)
    is_estimate = models.BooleanField(default=False, choices=model_choices.yes_no_choices, verbose_name=_("The dates provided above are approximations"),
                                      help_text=_("By selecting yes, the meeting date will be displayed in the 'quarter/year' format, e.g.: Summer 2024"))
    time_description_en = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("description of meeting times (en)"),
                                           help_text=_("e.g.: 9am to 4pm (Atlantic)"))
    time_description_fr = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("description of meeting times (fr)"),
                                           help_text=_("e.g.: 9h à 16h (Atlantique)"))

    # non-editable
    somp_notification_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("CSAS office notified about SoMP"))
    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"), related_name="meetings",
                                    editable=False)

    class Meta:
        ordering = ["start_date", _("name")]

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.start_date, sap_style=True)

        if self.is_virtual:
            self.location = 'Virtual / Virtuel'

        super().save(*args, **kwargs)

    @property
    def display(self):
        mystr = self.tname
        if self.is_planning:
            mystr += " ({})".format(gettext("planning"))
        return mystr

    def __str__(self):
        return self.display

    @property
    def full_display(self):
        fy = str(self.fiscal_year) if self.fiscal_year else "TBD"
        invitee_count = self.invitees.count()
        return f"{self.process.lead_region} - {fy} - {self.display} ({invitee_count} invitee{pluralize(invitee_count)})"

    class Meta:
        ordering = ["-is_planning", 'start_date', ]

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
        if not self.is_estimate:
            dates = f'{date(self.start_date)}'
            if self.end_date and self.end_date != self.start_date:
                end = date(self.end_date)
                dates += f' &rarr; {end}'
            days_display = "{} {}{}".format(self.length_days, gettext("day"), pluralize(self.length_days))
            dates += f' ({days_display})'
            return dates
        else:
            est_quarter = get_quarter(self.start_date)
            return f"{est_quarter} {self.start_date.year}"

    @property
    def tor_display_dates(self):
        if not self.is_estimate:
            start = date(self.start_date)
            lang = get_language()
            if lang == 'fr':
                dates = f'Le {start}'
            else:
                dates = f'{start}'
            if self.end_date and self.end_date != self.start_date:
                end = date(self.end_date)
                if lang == 'fr':
                    dates += f' au {end}'
                else:
                    dates += f' to {end}'
            return dates
        else:
            est_quarter = get_quarter(self.start_date)
            return f"{est_quarter} {self.start_date.year}"

    @property
    def expected_publications_en(self):
        """ this is mainly for the email that gets sent to NCR when there is a change on a posted meeting """
        if hasattr(self.process, "tor"):
            lang = get_language()
            activate("en")
            mystr = listrify(self.process.tor.expected_document_types.all())
            activate(lang)
            return mystr

    @property
    def expected_publications_fr(self):
        """ this is mainly for the email that gets sent to NCR when there is a change on a posted meeting """
        if hasattr(self.process, "tor"):
            lang = get_language()
            activate("fr")
            mystr = listrify(self.process.tor.expected_document_types.all())
            activate(lang)
            return mystr

    @property
    def total_cost(self):
        return self.costs.aggregate(dsum=Sum("amount"))["dsum"]

    @property
    def chair(self):
        qs = self.invitees.filter(roles__category=1).distinct()
        if qs.exists():
            return listrify([f"{invitee.person} ({invitee.person.affiliation})" for invitee in qs])

    @property
    def display_dates_deluxe(self):
        mystr = f"{self.display_dates}<br><em>({naturaltime(self.start_date)})</em>"
        return mark_safe(mystr)

    @property
    def ttime(self):
        my_str = self.time_description_en
        if getattr(self, str(_("time_description_en"))):
            my_str = "{}".format(getattr(self, str(_("time_description_en"))))
        return my_str


class MeetingNote(GenericNote):
    ''' a note pertaining to a meeting'''
    meeting = models.ForeignKey(Meeting, related_name='notes', on_delete=models.CASCADE)


class MeetingResource(SimpleLookup, MetadataFields):
    ''' a file attached to to meeting'''
    meeting = models.ForeignKey(Meeting, related_name='resources', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("name (en)"))
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


class MeetingFile(GenericFile):
    meeting = models.ForeignKey(Meeting, related_name="files", on_delete=models.CASCADE, editable=False)
    file = models.FileField(upload_to=meeting_directory_path)
    is_somp = models.BooleanField(default=False, verbose_name=_("is this the SoMP?"))


class InviteeRole(SimpleLookup):
    category = models.IntegerField(null=True, blank=True, choices=model_choices.invitee_role_categories, verbose_name=_("special category"))


class Invitee(models.Model):
    ''' a person that was invited to a meeting'''
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="meeting_invites")
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name="meeting_invites", blank=True, null=True,
                               verbose_name=_("DFO Region (if applicable)"))
    roles = models.ManyToManyField(InviteeRole, verbose_name=_("Function(s)"))
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

    def maximize_attendance(self):
        if self.meeting.start_date and self.meeting.end_date:
            self.attendance.all().delete()
            start_date = self.meeting.start_date
            end_date = self.meeting.end_date
            diff = (end_date - start_date)
            for i in range(0, diff.days + 1):
                date = start_date + timedelta(days=i)
                Attendance.objects.get_or_create(invitee=self, date=date)


class Attendance(models.Model):
    '''we will need to track on which days an invitee actually showed up'''
    invitee = models.ForeignKey(Invitee, on_delete=models.CASCADE, related_name="attendance", verbose_name=_("attendee"))
    date = models.DateTimeField(verbose_name=_("date"))

    class Meta:
        ordering = ['date']
        unique_together = (("invitee", "date"),)


class DocumentType(SimpleLookup):
    days_due = models.IntegerField(null=True, blank=True, verbose_name=_("days due following meeting"))
    hide_from_list = models.BooleanField(default=False, verbose_name=_("hide from main search?"), choices=model_choices.yes_no_choices)


class Document(MetadataFields):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="documents", editable=False, verbose_name=_("process"))
    document_type = models.ForeignKey(DocumentType, on_delete=models.DO_NOTHING, verbose_name=_("document type"))
    title_en = models.CharField(max_length=255, verbose_name=_("title (English)"), blank=True, null=True)
    title_fr = models.CharField(max_length=255, verbose_name=_("title (French)"), blank=True, null=True)
    title_in = models.CharField(max_length=255, verbose_name=_("title (Inuktitut)"), blank=True, null=True)
    year = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)], verbose_name=_("Publication Year"))
    pages = models.IntegerField(null=True, blank=True, verbose_name=_("pages"))

    # file (should be able to get size as well!
    file_en = models.FileField(upload_to=doc_directory_path, blank=True, null=True, verbose_name=_("file attachment (en)"))
    file_fr = models.FileField(upload_to=doc_directory_path, blank=True, null=True, verbose_name=_("file attachment (fr)"))

    url_en = models.URLField(verbose_name=_("document url (en)"), blank=True, null=True, max_length=2000)
    url_fr = models.URLField(verbose_name=_("document url (fr)"), blank=True, null=True, max_length=2000)

    dev_link_en = models.URLField(_("dev link (en)"), max_length=2000, blank=True, null=True)
    dev_link_fr = models.URLField(_("dev link (fr)"), max_length=2000, blank=True, null=True)

    ekme_gcdocs_en = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("EKME# / GCDocs (en)"))
    ekme_gcdocs_fr = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("EKME# / GCDocs (fr)"))

    lib_cat_en = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("library catalogue # (en)"))
    lib_cat_fr = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("library catalogue # (fr)"))

    # non-editable
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("document due date"), editable=False)
    pub_number_request_date = models.DateTimeField(null=True, blank=True, verbose_name=_("date of publication number request"), editable=False)
    pub_number = models.CharField(max_length=25, verbose_name=_("publication number"), blank=True, null=True, editable=False, unique=True)
    meetings = models.ManyToManyField(Meeting, blank=True, related_name="documents", verbose_name=_("csas meeting linkages"))
    people = models.ManyToManyField(Person, verbose_name=_("authors"), editable=False, through="Author")
    status = models.IntegerField(default=1, verbose_name=_("status"), choices=model_choices.get_document_status_choices(), editable=False)
    translation_status = models.IntegerField(verbose_name=_("translation status"), choices=model_choices.get_translation_status_choices(), editable=False,
                                             default=0)
    old_id = models.IntegerField(blank=True, null=True, editable=False)

    class Meta:
        ordering = ["process", _("title_en")]

    def save(self, *args, **kwargs):
        # set status
        self.status = 0  # ok
        if hasattr(self, "tracking"):
            self.pub_number = self.tracking.pub_number
            self.due_date = self.tracking.due_date
            self.status = 1  # tracking started

            for obj in model_choices.document_status_dict:
                trigger = obj.get("trigger")
                if trigger and getattr(self.tracking, trigger):
                    self.status = obj.get("value")

            self.translation_status = 0  # null
            for obj in model_choices.translation_status_dict:
                trigger = obj.get("trigger")
                if trigger and getattr(self.tracking, trigger):
                    self.translation_status = obj.get("value")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("csas2:document_detail", args=[self.pk])

    @property
    def ttitle(self):
        # check to see if a french value is given
        if getattr(self, str(_("title_en"))):
            my_str = "{}".format(getattr(self, str(_("title_en"))))
        else:
            my_str = self.title_en
        if not my_str:
            my_str = str(self.id)
        return my_str

    def __str__(self):
        return self.ttitle

    @property
    def status_display(self):
        stage = model_choices.get_document_status_lookup().get(self.status).get("stage")
        return mark_safe(f'<span class=" px-1 py-1 {stage}">{self.get_status_display()}</span>')

    @property
    def status_class(self):
        return model_choices.get_document_status_lookup().get(self.status).get("stage")

    @property
    def tstatus_display(self):
        stage = model_choices.get_translation_status_lookup().get(self.translation_status).get("stage")
        return mark_safe(f'<span class=" px-1 py-1 {stage}">{self.get_translation_status_display()}</span>')

    @property
    def tstatus_class(self):
        return model_choices.get_translation_status_lookup().get(self.translation_status).get("stage")


class DocumentNote(GenericNote):
    ''' a note pertaining to a meeting'''
    document = models.ForeignKey(Document, related_name='notes', on_delete=models.CASCADE)


class DocumentTracking(MetadataFields):
    ''' since not all docs from meetings will be tracked, we will establish a 1-1 relationship to parse out tracking process'''
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name="tracking")

    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("product due date"))
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("date submitted for review"), )
    submitted_by = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("submitted by"), related_name="doc_submissions")

    chair = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("chairperson"), related_name="doc_chair_positions")
    date_chair_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to chair"))
    date_chair_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by chair"))

    date_coordinator_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to CSAS coordinator"))
    date_coordinator_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by CSAS coordinator"))

    section_head = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("section head"),
                                     related_name="doc_section_heads")
    date_section_head_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to section head"))
    date_section_head_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by section head"))

    division_manager = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("division manager"),
                                         related_name="doc_division_managers")
    date_division_manager_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to division manager"))
    date_division_manager_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by division manager"))

    director = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("director"), related_name="doc_directors")
    date_director_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to director"))
    date_director_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by director"))

    pub_number = models.CharField(max_length=25, verbose_name=_("publication number"), blank=True, null=True)
    date_doc_submitted = models.DateTimeField(null=True, blank=True, verbose_name=_("date document submitted to CSAS office"))

    proof_sent_to = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("proof will be sent to which author"),
                                      related_name="doc_proof_sent")
    date_proof_author_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date PDF proof sent to author"))
    date_proof_author_approved = models.DateTimeField(null=True, blank=True, verbose_name=_("date PDF proof approved by author"))

    anticipated_posting_date = models.DateTimeField(null=True, blank=True, verbose_name=_("anticipated posting date"))
    actual_posting_date = models.DateTimeField(null=True, blank=True, verbose_name=_("actual posting date"))
    updated_posting_date = models.DateTimeField(null=True, blank=True, verbose_name=_("updated posting date"))

    # translation
    is_in_house = models.BooleanField(default=False, verbose_name=_("Will translation be tackled in-house?"))
    target_lang = models.IntegerField(verbose_name=_("target language"), choices=model_choices.language_choices, blank=True, null=True)

    date_translation_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to translation"))
    anticipated_return_date = models.DateTimeField(null=True, blank=True, verbose_name=_("forecasted return date"))
    client_ref_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("client reference number"))
    translation_ref_number = models.CharField(max_length=255, verbose_name=_("translation reference number"), blank=True, null=True)
    is_urgent = models.BooleanField(default=False, verbose_name=_("was submitted as an urgent request?"))
    date_returned = models.DateTimeField(null=True, blank=True, verbose_name=_("date received from translation"))
    invoice_number = models.CharField(max_length=255, verbose_name=_("invoice number"), blank=True, null=True)

    translation_review_date = models.DateTimeField(null=True, blank=True, verbose_name=_("translation review completion date"))
    translation_review_by = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("translation review completed by"),
                                              related_name="translation_review")

    translation_notes = models.TextField(null=True, blank=True, verbose_name=_("translation notes"))


class Author(models.Model):
    ''' a person that was invited to a meeting'''
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="authors", verbose_name=_("document"))
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="authorship", verbose_name=_("person"))
    is_lead = models.BooleanField(default=False, verbose_name=_("lead author?"))

    class Meta:
        ordering = ['-is_lead', 'person__first_name', "person__last_name"]
        unique_together = (("document", "person"),)
