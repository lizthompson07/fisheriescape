from datetime import timedelta
from math import floor
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Sum, Q
from django.template.defaultfilters import date, slugify, pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext, get_language, activate
from markdown import markdown
from textile import textile

from csas2 import model_choices, utils
from csas2.model_choices import tor_review_role_choices, request_review_role_choices, review_status_choices, review_decision_choices
from csas2.utils import get_quarter
from lib.functions.custom_functions import fiscal_year, listrify
from lib.templatetags.custom_filters import percentage
from ppt.models import Project
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields, Language, Person, Section, \
    SimpleLookupWithUUID, SubjectMatter

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
    is_national_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)
    is_web_pub_user = models.BooleanField(default=False, verbose_name=_("NCR web & pub staff?"), choices=YES_NO_CHOICES)

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


class GenericReviewer(MetadataFields):
    order = models.IntegerField(null=True, verbose_name=_("process order"))
    role = models.IntegerField(verbose_name=_("role"))
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(class)s_reviews", verbose_name=_("user"))
    decision = models.IntegerField(verbose_name=_("decision"), choices=review_decision_choices, blank=True, null=True)
    decision_date = models.DateTimeField(verbose_name=_("date"), blank=True, null=True)
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"))
    status = models.IntegerField(verbose_name=_("status"), default=10, choices=review_status_choices)

    # non-editable
    reminder_sent = models.DateTimeField(verbose_name=_("reminder sent date"), blank=True, null=True, editable=False)
    review_started = models.DateTimeField(verbose_name=_("review started"), blank=True, null=True, editable=False)
    review_completed = models.DateTimeField(verbose_name=_("review completed"), blank=True, null=True, editable=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        # if the decision is "approved" set the status of the reviewer to 'complete' (40)
        if self.decision == 1:
            self.status = 40
            # populate a decision date if not already there. (this is a safeguard for losing decision dates in the case of post-approval saving)
            if not self.decision_date:
                self.decision_date = timezone.now()
        # if the decision is "request changes" set the status of the TOR to "awaiting changes" (30); do not populate a decision date
        elif self.decision == 2:  # review decision = request changes
            self.update_parent_status_on_changes_requested()  # this will have to be defined by each reviewer model class
        else:
            self.decision_date = None

        # if the reviewer status is "pending" (30) and there is no starting date, this is the starting moment!
        if self.status == 30 and not self.review_started:
            self.review_started = timezone.now()
        # if the reviewer status is "complete" (40) and there is no completion date, this is the completion moment!
        elif self.status == 40 and not self.review_completed:
            self.review_completed = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order', ]

    def update_parent_status_on_changes_requested(self):
        # update the parent status (e.g., tor status or request status) to reflect the fact that there are changes awaiting
        pass

    def reset(self):
        self.status = 10  # DRAFT
        self.decision = None
        self.decision_date = None
        self.review_started = None
        self.review_completed = None
        self.reminder_sent = None
        self.save()

    def queue(self):
        self.status = 20  # QUEUED
        self.decision_date = None
        self.save()

    @property
    def review_duration(self):
        td = None
        if self.review_started and self.review_completed:
            td = self.review_completed - self.review_started
        elif self.review_started:
            td = timezone.now() - self.review_started
        if td:
            # return the total number of days
            return floor((td.seconds + (td.days * 24 * 60 * 60)) / (24 * 60 * 60))

    @property
    def comments_html(self):
        if self.comments:
            return textile(self.comments)
        else:
            return "---"

    @property
    def can_be_modified(self):
        return self.status in [10, 20]


class CSASOffice(models.Model):
    region = models.ForeignKey(Region, blank=True, on_delete=models.DO_NOTHING, related_name="csas_offices", verbose_name=_("region"))
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_offices", verbose_name=_("coordinator / CSA"))
    advisors = models.ManyToManyField(User, blank=True, verbose_name=_("science advisors"), related_name="csas_offices_advisors")
    administrators = models.ManyToManyField(User, blank=True, verbose_name=_("administrators"), related_name="csas_offices_administrators")
    generic_email = models.EmailField(verbose_name=_("generic email address"), blank=True, null=True)
    disable_request_notifications = models.BooleanField(default=False, verbose_name=_("disable notifications from new requests?"), choices=YES_NO_CHOICES)
    no_staff_emails = models.BooleanField(default=False, verbose_name=_("do not send emails directly to office staff?"), choices=YES_NO_CHOICES)
    ppt_default_section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="csas_offices",
                                            verbose_name=_("default section for PPT"),
                                            help_text=_("When exporting CSAS processes to projects, what should be the default section to use?"))

    class Meta:
        ordering = ["region"]

    def __str__(self):
        return str(self.region)

    def get_absolute_url(self):
        return reverse("csas2:office_list")

    @property
    def all_emails(self):
        payload = list()
        if not self.no_staff_emails:
            payload.append(self.coordinator.email)
            payload.extend([u.email for u in self.advisors.all()])
            payload.extend([u.email for u in self.administrators.all()])
        if self.generic_email:
            payload.append(self.generic_email)
        return list(set(payload))

    @property
    def all_emails_display(self):
        payload = listrify(self.all_emails, "<br>")
        if not payload:
            payload = str()
        else:
            payload += f'<br><br>'
        if self.disable_request_notifications:
            payload += f'<span class="text-danger">* request notification emails disabled</span>'
        return payload


class CSASRequest(MetadataFields):
    ''' csas request '''
    language = models.IntegerField(default=1, verbose_name=_("language of request"), choices=model_choices.language_choices)
    title = models.CharField(max_length=1000, verbose_name=_("title"))
    translated_title = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("translated title"))
    office = models.ForeignKey(CSASOffice, on_delete=models.DO_NOTHING, related_name="csas_offices", verbose_name=_("CSAS office"),
                               blank=True, null=False)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="csas_client_requests", verbose_name=_("DFO client"), blank=True, null=False)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="csas_requests", verbose_name=_("client section"), blank=True, null=False)
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
    tags = models.ManyToManyField(SubjectMatter, blank=True, verbose_name=_("keyword tags"), limit_choices_to={"is_csas_request_tag": True})
    editors = models.ManyToManyField(User, blank=True, verbose_name=_("request editors"), related_name="request_editors",
                                     help_text=_("A list of DFO staff, in addition to the primary client, who has permission to edit the draft CSAS request."))

    # non-editable fields
    status = models.IntegerField(default=10, verbose_name=_("status"), choices=model_choices.request_status_choices, editable=False)
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("submission date"), editable=False)
    old_id = models.IntegerField(blank=True, null=True, editable=False)
    uuid = models.UUIDField(editable=False, unique=True, blank=True, null=True, default=uuid4, verbose_name=_("unique identifier"))

    # calculated
    advice_fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="csas_request_advice",
                                           verbose_name=_("advice FY"), editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="csas_requests",
                                    verbose_name=_("request FY"), editable=False)
    ref_number = models.CharField(blank=True, null=True, editable=False, verbose_name=_("reference number"), max_length=255)

    class Meta:
        ordering = ("fiscal_year", "title")
        verbose_name_plural = _("CSAS Requests")
        verbose_name = _("CSAS Request")

    def __str__(self):
        return self.title

    def withdraw(self):
        self.status = 99
        self.save()

    def unsubmit(self):
        utils.end_request_review_process(self)

    def submit(self):
        utils.start_request_review_process(self)

    def save(self, *args, **kwargs):

        # request fiscal year
        if hasattr(self, "review"):
            self.ref_number = self.review.ref_number
            if self.review.advice_date:
                self.advice_fiscal_year_id = fiscal_year(self.review.advice_date, sap_style=True)
            else:
                self.advice_fiscal_year_id = fiscal_year(self.advice_needed_by, sap_style=True)
        else:
            self.advice_fiscal_year_id = fiscal_year(self.advice_needed_by, sap_style=True)

        # submission fiscal year
        if self.submission_date:
            self.fiscal_year_id = fiscal_year(self.submission_date, sap_style=True)
        elif self.created_at:
            self.fiscal_year_id = fiscal_year(self.created_at, sap_style=True)
        else:
            self.fiscal_year_id = fiscal_year(timezone.now(), sap_style=True)

        # set the STATUS

        # if there is a process, the request the request MUST have been approved.
        if self.id and self.processes.exists():
            if self.processes.filter(status=100).count() == self.processes.all().count():
                self.status = 80  # fulfilled
            elif self.processes.filter(status=90).count() == self.processes.all().count():
                self.status = 99  # withdrawn
            else:
                self.status = 70  # accepted
        else:
            # if the request is not submitted, it should automatically be in draft
            if not self.submission_date:
                self.status = 10  # draft
            else:
                # if the status is set to withdrawn, we do nothing more.
                if self.status not in [99, 25]:
                    # look at the review to help determine the status
                    self.status = 20  # under review by client
                    # if all the client reviewers have approved the request AND there is at least one approval, it is ready for csas team
                    if self.reviewers.filter(status=40, role=1).exists() and self.reviewers.filter(status=40).count() == self.reviewers.all().count():
                        self.status = 30  # Ready for CSAS review
                    if hasattr(self, "review") and self.review.id:
                        self.status = 40  # under review
                        if self.review.decision:
                            self.status = self.review.decision + 40
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
            'office',
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

    @property
    def is_rescheduled(self):
        """
        the request is considered rescheduled if the following two met:
        1) there is a review
        2) the review has an advice date
        3) the advice date is different than the request advice date
        """
        return hasattr(self, "review") and self.review.advice_date and self.advice_needed_by != self.review.advice_date

    @property
    def is_valid_request(self):
        if hasattr(self, "review") and (self.review.is_valid == 0 or self.review.is_feasible == 0):
            return False
        return True

    @property
    def coordinator(self):
        return self.office.coordinator

    @property
    def current_reviewer(self):
        """Send back the first reviewer whose status is 'pending' """
        return self.reviewers.filter(status=30).first()


class CSASRequestNote(GenericNote):
    ''' a note pertaining to a csas request'''
    csas_request = models.ForeignKey(CSASRequest, related_name='notes', on_delete=models.CASCADE)


class CSASRequestReview(MetadataFields):
    csas_request = models.OneToOneField(CSASRequest, on_delete=models.CASCADE, related_name="review")
    ref_number = models.CharField(max_length=50, verbose_name=_("reference number (optional)"), blank=True, null=True)
    is_valid = models.IntegerField(blank=True, null=True, verbose_name=_("Is this within the scope of CSAS?"), choices=model_choices.yes_no_choices_int)
    is_feasible = models.IntegerField(blank=True, null=True, verbose_name=_("is this feasible from a Science perspective"),
                                      choices=model_choices.yes_no_unsure_choices_int)
    decision = models.IntegerField(blank=True, null=True, verbose_name=_("recommendation"), choices=model_choices.request_decision_choices)
    decision_text = models.TextField(blank=True, null=True, verbose_name=_("recommendation explanation"))
    decision_date = models.DateTimeField(null=True, blank=True, verbose_name=_("recommendation date"))
    advice_date = models.DateTimeField(verbose_name=_("advice required by (final)"), blank=True, null=True)
    deferred_text = models.TextField(null=True, blank=True, verbose_name=_("rationale for alternate scheduling"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("administrative notes"))

    # non-editable
    email_notification_date = models.DateTimeField(verbose_name=_("email notification date"), blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.is_valid == 0 or self.is_feasible == 0:
            self.decision = 2  # the decision MUST be to withdraw

        # if there is a decision, but no decision date, it should be populated
        if self.decision and not self.decision_date:
            self.decision_date = timezone.now()

        elif not self.decision:
            self.decision_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(gettext("Review for CSAS Request #"), self.csas_request.id)

    @property
    def decision_display(self):
        if self.decision:
            text = self.decision_text if self.decision_text else gettext("no further detail provided.")
            return "{} - {} ({})".format(self.get_decision_display(), text, date(self.decision_date))
        return gettext("---")


class CSASRequestFile(GenericFile):
    csas_request = models.ForeignKey(CSASRequest, related_name="files", on_delete=models.CASCADE, editable=False)
    is_approval = models.BooleanField(default=False, verbose_name=_("is this file an approval for this request?"), choices=YES_NO_CHOICES)
    file = models.FileField(upload_to=request_directory_path)


class RequestReviewer(GenericReviewer):
    csas_request = models.ForeignKey(CSASRequest, related_name="reviewers", on_delete=models.CASCADE)
    role = models.IntegerField(verbose_name=_("role"), choices=request_review_role_choices)

    @property
    def can_be_modified(self):
        return self.status in [10, 20] and self.csas_request.status <= 30

    def update_parent_status_on_changes_requested(self):
        r = self.csas_request
        r.status = 25
        r.save()


class Process(SimpleLookupWithUUID, MetadataFields):
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("title (fr)"))
    status = models.IntegerField(choices=model_choices.get_process_status_choices(), verbose_name=_("status"), default=1)
    scope = models.IntegerField(verbose_name=_("scope"), choices=model_choices.process_scope_choices)
    type = models.IntegerField(verbose_name=_("type"), choices=model_choices.process_type_choices)

    lead_office = models.ForeignKey(CSASOffice, on_delete=models.DO_NOTHING, related_name="csas_lead_offices", verbose_name=_("lead CSAS office"),
                                    blank=True, null=False)
    other_offices = models.ManyToManyField(CSASOffice, blank=True, verbose_name=_("other CSAS offices"))
    editors = models.ManyToManyField(User, blank=True, verbose_name=_("process editors"), related_name="process_editors",
                                     help_text=_("A list of non-CSAS staff with permissions to edit the process, meetings and documents"))

    csas_requests = models.ManyToManyField(CSASRequest, blank=True, related_name="processes", verbose_name=_("Connected CSAS requests"))
    advice_date = models.DateTimeField(verbose_name=_("Target date to provide Science advice"), blank=True, null=True)
    projects = models.ManyToManyField(Project, blank=True, related_name="csas_processes", verbose_name=_("Links to PPT Projects"))

    # non-editable
    has_peer_review_meeting = models.BooleanField(default=False, verbose_name=_("has peer review meeting?"))
    has_planning_meeting = models.BooleanField(default=False, verbose_name=_("has planning meeting?"))
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, related_name="processes", verbose_name=_("fiscal year"), editable=False)

    # calculated

    class Meta:
        ordering = ["fiscal_year", _("name")]

    def save(self, *args, **kwargs):
        self.has_peer_review_meeting = self.meetings.filter(is_planning=False).exists()
        self.has_planning_meeting = self.meetings.filter(is_planning=True).exists()

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
            if hasattr(self, "tor") and self.tor.status == 50:  # complete status
                self.status = 22  # tor complete!

            # has the latest scheduled meeting passed
            now = timezone.now()
            meeting_qs = self.meetings.filter(is_planning=False, is_estimate=False).order_by("end_date")
            if meeting_qs.exists() and meeting_qs.last().end_date and meeting_qs.last().end_date <= now:
                self.status = 25  # meeting complete!

            # has the key docs have been completed
            doc_qs = self.documents.filter(status__in=[12, 17])
            # compare the count of posted docs with all (non-translation only) docs)
            if doc_qs.exists() and doc_qs.count() >= self.documents.filter(~Q(document_type__name__icontains="translation")).count():
                self.status = 100  # complete!

        super().save(*args, **kwargs)

    @property
    def has_tor(self):
        return hasattr(self, "tor")

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

    @property
    def tor_status(self):
        try:
            return self.tor.get_status_display()
        except:
            return gettext("n/a")

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
    def client_sections(self):
        return listrify(set([r.section for r in self.csas_requests.all()]))

    @property
    def client_sectors(self):
        return listrify(set([r.section.division.branch.sector for r in self.csas_requests.all()]))

    @property
    def client_regions(self):
        return listrify(set([r.section.division.branch.sector.region for r in self.csas_requests.all()]))

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
        mystr = str(self.lead_office.region)
        if self.other_offices.exists():
            mystr = f"<b><u>{mystr}</u></b>"
            mystr += f", {listrify([o for o in self.other_offices.all()])}"
        return mystr

    @property
    def formatted_notes(self):
        mystr = ""
        for note in self.notes.filter(type=1):
            mystr += f"* {note.note}\n\n"
        return mystr

    @property
    def key_meetings(self):
        mystr = ""
        for meeting in self.meetings.filter(is_planning=False):
            mystr += f"English Title: {meeting.name}\n" \
                     f"French Title: {meeting.nom}\n" \
                     f"Location: {meeting.location}\n" \
                     f"Dates: {meeting.tor_display_dates}\n\n"
        return mystr

    @property
    def doc_summary(self):
        mystr = ""
        for doc in self.documents.all():
            mystr += f"Title: {doc.ttitle}\n" \
                     f"Type: {doc.document_type}\n" \
                     f"Status: {doc.get_status_display()}\n" \
                     f"Translation Status: {doc.get_translation_status_display()}\n"

            if hasattr(doc, "tracking"):
                mystr += f"Due Date: {date(doc.tracking.due_date)}\n" \
                         f"Date Posted: {date(doc.tracking.actual_posting_date)}\n"

            if doc.tracking.due_date and doc.tracking.actual_posting_date:
                mystr += f"Delta: {(doc.tracking.actual_posting_date - doc.tracking.due_date).days}\n"
            elif doc.tracking.due_date:
                mystr += f"Delta: {(timezone.now() - doc.tracking.due_date).days}\n"
            mystr += "\n\n"
        return mystr

    @property
    def coordinator(self):
        return self.lead_office.coordinator

    @property
    def advisors(self):
        return self.lead_office.advisors.all()

    @property
    def editor_email_list(self):
        payload = self.lead_office.all_emails
        for office in self.other_offices.all():
            payload.extend(office.all_emails)
        for editor in self.editors.all():
            payload.append(editor.email)
        return list(set(payload))


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
    # is_complete = models.BooleanField(default=False, verbose_name=_("Are the ToRs complete?"), choices=YES_NO_CHOICES,
    #                                   help_text=_("Selecting yes will update the process status"), editable=False)

    # non-editable fields
    status = models.IntegerField(default=10, verbose_name=_("status"), choices=model_choices.tor_status_choices, editable=False)
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("submission date"), editable=False)
    posting_request_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("Date of posting request"))
    posting_notification_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("Posting notification date"))

    def unsubmit(self):
        utils.end_tor_review_process(self)

    def submit(self):
        utils.start_tor_review_process(self)

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

    def __str__(self):
        return gettext("Terms of Reference")

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

    @property
    def expected_publications_en(self):
        lang = get_language()
        activate("en")
        mystr = listrify(self.expected_document_types.all())
        activate(lang)
        return mystr

    @property
    def expected_publications_fr(self):
        lang = get_language()
        activate("fr")
        mystr = listrify(self.expected_document_types.all())
        activate(lang)
        return mystr

    def get_absolute_url(self):
        return reverse('csas2:tor_detail', args=[self.id])

    @property
    def current_reviewer(self):
        """Send back the first reviewer whose status is 'pending' """
        return self.reviewers.filter(status=30).first()


class ToRReviewer(GenericReviewer):
    tor = models.ForeignKey(TermsOfReference, on_delete=models.CASCADE, related_name="reviewers")
    role = models.IntegerField(verbose_name=_("role"), choices=tor_review_role_choices)

    @property
    def can_be_modified(self):
        return self.status in [10, 20] and self.tor.status != 50

    def update_parent_status_on_changes_requested(self):
        tor = self.tor
        tor.status = 30
        tor.save()


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
    chair_comments = models.TextField(blank=True, null=True, verbose_name=_("post-meeting chair comments"),
                                      help_text=_("Does the chair have comments to be captured OR passed on to NCR following the peer-review meeting."))
    has_media_attention = models.BooleanField(default=False, verbose_name=_("will this meeting generate media attention?"),
                                              choices=model_choices.yes_no_choices,
                                              help_text=_("The answer to this question will be used by NCR for regular reporting on the meeting (i.e., TAB7)"))
    media_notes = models.TextField(blank=True, null=True, verbose_name=_("status of media lines"), help_text=_("Please indicate the status of the media lines"))

    # non-editable
    is_somp_submitted = models.BooleanField(default=False, verbose_name=_("have the SoMP been submitted?"), editable=False)
    somp_notification_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("CSAS office notified about SoMP"))
    is_posted = models.BooleanField(default=False, verbose_name=_("is meeting posted on CSAS website?"))
    posting_request_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Date of posting request"), editable=False)
    posting_notification_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("Posting notification date"))

    # calculated
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year of meeting"),
                                    related_name="meetings", editable=False)

    class Meta:
        ordering = ["start_date", _("name")]

    def save(self, *args, **kwargs):
        self.fiscal_year_id = fiscal_year(self.start_date, sap_style=True)

        if self.is_virtual:
            self.location = 'Virtual / Virtuel'

        super().save(*args, **kwargs)

    @property
    def chair_comments_html(self):
        if self.chair_comments:
            return mark_safe(markdown(self.chair_comments))

    @property
    def media_display(self):
        if self.has_media_attention:
            text = self.media_notes if self.media_notes else gettext("no further details provided.")
            return "{} - {}".format(gettext("Yes"), text)
        return gettext("No")

    @property
    def posting_status(self):
        if self.posting_request_date and not self.is_posted:
            return gettext("Requested")
        elif self.is_posted:
            return gettext("Posted")
        elif not self.is_planning:
            return gettext("Not posted")
        return "n/a"

    @property
    def can_post_meeting(self):
        """ stores the business rules for whether the meeting can be posted to the csas website"""
        can_post = [True]  # start off optimistic
        reasons = []

        if self.is_planning:
            reasons.append(gettext("cannot post a planning meeting"))
            can_post.append(False)
        else:
            # the process must have a tor started and that tor must have expected pubs listed
            if not self.process.has_tor or not self.process.tor.expected_document_types.exists():
                reasons.append(gettext("cannot post because the CSAS Process must have a Terms of Reference with a list of expected publications"))
                can_post.append(False)
            if self.is_posted:
                reasons.append(gettext("this meeting is already posted"))
                can_post.append(False)
            if self.posting_request_date:
                reasons.append(gettext("a posting request has already been made for this meeting"))
                can_post.append(False)

        return dict(
            can_post=False not in can_post, reasons=reasons
        )

    @property
    def can_submit_somp(self):
        """ stores the business rules for whether the meeting can be posted to the csas website"""
        reasons = []
        is_allowed = [True]  # start off optimistic

        if self.is_planning:
            reasons.append(gettext("SoMP can only be submitted for a peer-review meeting"))
            is_allowed.append(False)
        else:
            # the meeting must be in the past
            if self.start_date > timezone.now():
                reasons.append(gettext("the meeting must have already taken place"))
                is_allowed.append(False)
            # the meeting must have linked documents
            if not self.documents.exists():
                reasons.append(gettext("this meeting is not linked to any documents"))
                is_allowed.append(False)
            # the meeting must have linked documents that are all confirmed
            elif not self.documents.filter(is_confirmed=True).exists():
                reasons.append(gettext("all linked documents must be confirmed before submitting"))
                is_allowed.append(False)
            # cannot already have been submitted
            # if self.is_somp_submitted:
            #     reasons.append(gettext("the SoMP have already been submitted for this meeting"))
            #     is_allowed.append(False)

        return dict(
            is_allowed=False not in is_allowed,
            reasons=reasons
        )

    @property
    def mmmmyy(self):
        if self.start_date:
            return self.start_date.strftime("%B %Y")

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
        return f"{self.process.lead_office.region} - {fy} - {self.display} ({invitee_count} invitee{pluralize(invitee_count)})"

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
    def quarter(self):
        est_quarter = get_quarter(self.start_date, "verbose")
        return f"{est_quarter}"

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
            return self.process.tor.expected_publications_en

    @property
    def expected_publications_fr(self):
        """ this is mainly for the email that gets sent to NCR when there is a change on a posted meeting """
        if hasattr(self.process, "tor"):
            return self.process.tor.expected_publications_fr

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

    @property
    def email_list(self):
        invitees = self.invitees.filter(~Q(status=2)).filter(person__email__isnull=False)
        return listrify([i.person.email for i in invitees], separator=";")

    @property
    def key_invitees(self):
        return self.invitees.filter(roles__category__in=[1, 5]).distinct()


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


class InviteeRole(SimpleLookup):
    category = models.IntegerField(null=True, blank=True, choices=model_choices.invitee_role_categories, verbose_name=_("special category"))


class Invitee(models.Model):
    ''' a person that was invited to a meeting'''
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="invitees")
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="meeting_invites")
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name="meeting_invites", blank=True, null=True,
                               verbose_name=_("DFO Region (if applicable)"))
    roles = models.ManyToManyField(InviteeRole, verbose_name=_("Function(s)"))
    status = models.IntegerField(choices=model_choices.invitee_status_choices, verbose_name=_("status"), default=9)
    invitation_sent_date = models.DateTimeField(verbose_name=_("date invitation was sent"), editable=False, blank=True, null=True)
    resources_received = models.ManyToManyField("MeetingResource", editable=False)
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"))

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

    @property
    def tname(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            my_str = "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.name
        return my_str


class Document(MetadataFields):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="documents", editable=False, verbose_name=_("process"))
    meetings = models.ManyToManyField(Meeting, blank=True, related_name="documents", verbose_name=_("linkage to peer-review meetings"))
    document_type = models.ForeignKey(DocumentType, on_delete=models.DO_NOTHING, verbose_name=_("document type"))
    lead_office = models.ForeignKey(CSASOffice, on_delete=models.DO_NOTHING, related_name="documents", verbose_name=_("lead CSAS office"),
                                    blank=True, null=True, help_text=_(
            "The Lead CSAS office will process approvals and translation and will be listed on the cover page of the publication"))
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
    people = models.ManyToManyField(Person, verbose_name=_("authors"), editable=False, through="Author")
    status = models.IntegerField(default=1, verbose_name=_("status"), choices=model_choices.get_document_status_choices(), editable=False)
    translation_status = models.IntegerField(verbose_name=_("translation status"), choices=model_choices.get_translation_status_choices(), editable=False,
                                             default=0)
    old_id = models.IntegerField(blank=True, null=True, editable=False)
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Has been confirmed?"), editable=False)

    @property
    def can_confirm(self):
        can_confirm = [True]
        reasons = list()

        # is there a tentative title?
        if self.is_confirmed:
            can_confirm.append(False)
            reasons.append(
                gettext("Cannot confirm because document is already confirmed")
            )
        else:
            # is there a tentative title?
            if not self.title_en and not self.title_fr:
                can_confirm.append(False)
                reasons.append(
                    gettext("Cannot confirm because there must be a tentative title")
                )
            # is there a lead office?
            if not self.lead_office:
                can_confirm.append(False)
                reasons.append(
                    gettext("Cannot confirm because there is no lead office")
                )
            # is there a lead author?
            if not self.lead_authors.exists():
                can_confirm.append(False)
                reasons.append(
                    gettext("Cannot confirm because there are no lead authors")
                )

        return {
            "can_confirm": False not in can_confirm,
            "reasons": listrify(reasons),
        }

    @property
    def lead_authors(self):
        return self.authors.filter(is_lead=True)

    class Meta:
        ordering = ["process", _("title_en")]

    def save(self, *args, **kwargs):
        # set status
        self.status = 0  # unconfirmed

        if self.is_confirmed:
            # self.status = 20  # confirmed
            self.status = 1  # tracking started

        if hasattr(self, "tracking"):
            self.pub_number = self.tracking.pub_number
            self.due_date = self.tracking.due_date

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
            my_str = gettext("Untitled") + " " + str(self.document_type)
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
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_("date submitted by author"), )
    submitted_by = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("submitted by"), related_name="doc_submissions")

    chair = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("chairperson"), related_name="doc_chair_positions")
    date_chair_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to chair"))
    date_chair_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by chair"))
    chair_comments = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    date_coordinator_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to CSAS coordinator"))
    date_coordinator_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by CSAS coordinator"))
    coordinator_comments = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    section_head = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("section head"),
                                     related_name="doc_section_heads")
    date_section_head_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to section head"))
    date_section_head_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by section head"))
    section_head_comments = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    division_manager = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("division manager"),
                                         related_name="doc_division_managers")
    date_division_manager_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to division manager"))
    date_division_manager_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by division manager"))
    division_manager_comments = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    director = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("director"), related_name="doc_directors")
    date_director_sent = models.DateTimeField(null=True, blank=True, verbose_name=_("date sent to director"))
    date_director_appr = models.DateTimeField(null=True, blank=True, verbose_name=_("date approved by director"))
    director_comments = models.TextField(null=True, blank=True, verbose_name=_("comment"))

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
