import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.dispatch import receiver
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from textile import textile

from dm_apps import custom_widgets
from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import fiscal_year, listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
# Choices for language
from shared_models.models import SimpleLookup, Lookup
from . import emails

ENG = 1
FRE = 2
LANGUAGE_CHOICES = (
    (ENG, 'English'),
    (FRE, 'French'),
)

YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)

NULL_YES_NO_CHOICES = (
    (None, _("---------")),
    (1, _("Yes")),
    (0, _("No")),
)


class BudgetCode(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['code', ]


class Theme(SimpleLookup):
    pass


class UpcomingDate(models.Model):
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, related_name="project_upcoming_dates2",
                               verbose_name=_("region"))
    description_en = models.TextField(verbose_name=_("description (en)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("description (fr)"))
    date = models.DateField()
    is_deadline = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date", ]

    @property
    def tdescription(self):
        # check to see if a french value is given
        if getattr(self, str(_("description_en"))):
            my_str = "{}".format(getattr(self, str(_("description_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.description_en
        return my_str


class FunctionalGroup(SimpleLookup):
    sections = models.ManyToManyField(shared_models.Section, related_name="functional_groups2", blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, related_name="functional_groups", blank=True, null=True)


class ActivityType(SimpleLookup):
    pass

    class Meta:
        ordering = ['id', ]


class FundingSourceType(SimpleLookup):
    color = models.CharField(max_length=10, blank=True, null=True)


class FundingSource(SimpleLookup):
    name = models.CharField(max_length=255)
    funding_source_type = models.ForeignKey(FundingSourceType, on_delete=models.DO_NOTHING, related_name="funding_sources")

    def __str__(self):
        return "{} - {}".format(self.funding_source_type, self.tname)

    class Meta:
        ordering = ['funding_source_type', 'name', ]
        unique_together = [('funding_source_type', 'name'), ]


class Tag(SimpleLookup):
    pass


class Status(SimpleLookup):
    # choices for used_for
    PROJECT = 1
    REPORTS = 2
    MILESTONES = 3
    USED_FOR_CHOICES = (
        (PROJECT, "Projects"),
        (REPORTS, "Status reports"),
        (MILESTONES, "Milestones"),
    )

    used_for = models.IntegerField(choices=USED_FOR_CHOICES)
    order = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['used_for', 'order', 'name', ]


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


class Project(models.Model):
    # choices for is_national
    is_national_choices = (
        (None, _("Unknown")),
        (1, _("National")),
        (0, _("Regional")),
    )

    year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects2",
                             verbose_name=_("fiscal year"), default=fiscal_year(next=True, sap_style=True))
    # basic
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, related_name="projects2",
                                verbose_name=_("section"))
    project_title = custom_widgets.OracleTextField(verbose_name=_("Project title"))
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name=_("activity type"))
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                         verbose_name=_("Functional group"))
    default_funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, blank=False, null=True, related_name="projects",
                                               verbose_name=_("primary funding source"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags / keywords (used for searching)"), related_name="projects")

    # details
    is_national = models.IntegerField(blank=True, null=True, default=False, verbose_name=_("National or regional?"),
                                      choices=is_national_choices)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True,
                               verbose_name=_("project status"), limit_choices_to={"used_for": 1})

    # DELETE ME!!!! ############################################
    is_competitive = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, default=0,
                                         verbose_name=_("Is the funding competitive?"))
    # DELETE ME!!!! ############################################
    is_approved = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES,
                                      verbose_name=_("Has this project already been approved"))

    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start date of project"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project"))

    # HTML field
    description = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))
    # description_html = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))

    # HTML field
    priorities = models.TextField(blank=True, null=True, verbose_name=_("Project-specific priorities"))
    # HTML field
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("Project deliverables / activities"))

    # SPECIALIZED EQUIPMENT
    ########################
    requires_specialized_equipment = models.BooleanField(default=False, verbose_name=_(
        "Will the project require the purchase, design or fabrication of specialized laboratory or field equipment?"))
    technical_service_needs = models.TextField(blank=True, null=True, verbose_name=_("What technical services are being requested?"))
    mobilization_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Do you anticipate needing assistance with mobilization/demobilization of this equipment?"))

    # TRAVEL
    ########
    has_travel = models.BooleanField(default=False, verbose_name=_("Does this project involved a field component?"))
    vehicle_needs = models.TextField(blank=True, null=True,
                                     verbose_name=_("Describe need for vehicle (type of vehicle, number of weeks, time-frame)"))
    ship_needs = models.TextField(blank=True, null=True, verbose_name=_("Ship (Coast Guard, charter vessel) Requirements"))
    coip_reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_(
        "If this project links to a ship time request in COIP, please include the COIP application number here."))
    instrumentation = models.TextField(blank=True, null=True,
                                       verbose_name=_("What field instrumentation will be deployed during this project?"))
    owner_of_instrumentation = models.TextField(blank=True, null=True, verbose_name=_(
        "Who is the owner/curator of this instrumentation, if known?"))
    # -- > Field staff
    requires_field_staff = models.BooleanField(default=False, verbose_name=_("Does this project involved a field component?"))
    field_staff_needs = models.TextField(blank=True, null=True, verbose_name=_("If so, please include some additional detail, "
                                                                               "e.g., how many people are likely to be required and when"))

    # DATA
    #######
    has_new_data = models.BooleanField(default=False, verbose_name=_("Will new data be collected or generated?"))
    data_collection = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    data_products = models.TextField(blank=True, null=True, verbose_name=_("What data products will be generated (e.g. models, indices)?"))
    open_data_eligible = models.BooleanField(default=True, verbose_name=_("Are these data / data products eligible "
                                                                          "to be placed on the Open Data Platform?"))
    data_storage = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving Plan"))
    regional_dm_needs = models.TextField(blank=True, null=True, verbose_name=_("Describe what data management support is required, "
                                                                               "if any."))

    # LAB WORK
    ##########
    has_lab_work = models.BooleanField(default=False, verbose_name=_("Does this project involve laboratory work?"))
    # maritimes only
    abl_services_required = models.BooleanField(default=False, verbose_name=_(
        "Does this project require the services of Aquatic Biotechnology Lab (ABL)?"))
    lab_space_required = models.BooleanField(default=False, verbose_name=_("Is laboratory space required?"))
    chemical_needs = models.TextField(blank=True, null=True, verbose_name=_("Please provide details regarding chemical "
                                                                            "needs and the plan for storage and disposal."))

    it_needs = models.TextField(blank=True, null=True, verbose_name=_("Special IT requirements (software, licenses, hardware)"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))

    # coding
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_projects2',
                                              verbose_name=_("responsibility center (if known)"))
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_projects2', verbose_name=_("allotment code (if known)"))
    existing_project_codes = models.ManyToManyField(shared_models.Project, blank=True, verbose_name=_("existing project codes (if known)"),
                                                    related_name="projects")

    # admin
    submitted = models.BooleanField(default=False, verbose_name=_("Submit project for review"))
    # approved = models.BooleanField(default=False, verbose_name=_("approved"))
    recommended_for_funding = models.BooleanField(default=False, verbose_name=_("recommended"))
    approved = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("approved"))
    allocated_budget = models.FloatField(blank=True, null=True, verbose_name=_("Allocated budget"))
    notification_email_sent = models.DateTimeField(blank=True, null=True, verbose_name=_("Notification Email Sent"))
    meeting_notes = models.TextField(blank=True, null=True, verbose_name=_("administrative notes"))

    is_hidden = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, default=False,
                                    verbose_name=_("Should the project be hidden from other users?"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"),
                                         related_name="projects_last_modified_by")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{}".format(self.project_title)

    def send_approval_email(self, request):
        if self.approved is not None and not self.notification_email_sent:
            email = emails.ProjectApprovalEmail(self, request)
            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            self.notification_email_sent = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()

        super().save(*args, **kwargs)

    @property
    def status_report_count(self):
        return self.reports.count()

    @property
    def unapproved(self):
        return self.submitted and not self.approved

    @property
    def coding(self):
        if self.responsibility_center:
            rc = self.responsibility_center.code
        else:
            rc = "xxxxx"
        if self.allotment_code:
            ac = self.allotment_code.code
        else:
            ac = "xxx"

        if self.existing_project_codes.count() >= 1:
            pc = listrify([project_code.code for project_code in self.existing_project_codes.all()])
            if self.existing_project_codes.count() > 1:
                pc = "[" + pc + "]"
        else:
            pc = "xxxxx"
        return "{}-{}-{}".format(rc, ac, pc)

    def get_funding_sources(self):
        # look through all expenses and compile a unique list of funding sources
        my_list = []
        for item in self.staff_members.all():
            if item.funding_source and item.cost and item.cost > 0:
                my_list.append(item.funding_source)

        for item in self.om_costs.all():
            if item.funding_source and item.budget_requested and item.budget_requested > 0:
                my_list.append(item.funding_source)

        for item in self.capital_costs.all():
            if item.funding_source and item.budget_requested and item.budget_requested > 0:
                my_list.append(item.funding_source)

        return set(my_list)

    @property
    def funding_sources(self):
        return listrify(self.get_funding_sources())

    @property
    def project_leads(self):
        return listrify([staff for staff in self.staff_members.all() if staff.lead])

    @property
    def project_leads_as_users(self):
        return [staff.user for staff in self.staff_members.all() if staff.lead and staff.user]

    @property
    def total_fte(self):
        return sum(
            [nz(staff.duration_weeks, 0) for staff in self.staff_members.all()]
        )

    @property
    def total_ot(self):
        return sum(
            [nz(staff.overtime_hours, 0) for staff in self.staff_members.all()]
        )

    @property
    def total_salary(self):
        return nz(self.staff_members.filter(employee_type__cost_type=1).aggregate(dsum=Sum("cost"))['dsum'], 0)

    @property
    def total_om(self):
        return nz(self.staff_members.filter(employee_type__cost_type=2).aggregate(dsum=Sum("cost"))['dsum'], 0) + \
               nz(self.om_costs.aggregate(dsum=Sum("budget_requested"))['dsum'], 0)

    @property
    def total_capital(self):
        return nz(self.capital_costs.aggregate(dsum=Sum("budget_requested"))['dsum'], 0)

    @property
    def total_cost(self):
        return nz(self.staff_members.all().aggregate(dsum=Sum("cost"))['dsum'], 0) + \
               nz(self.om_costs.aggregate(dsum=Sum("budget_requested"))['dsum'], 0) + \
               nz(self.capital_costs.aggregate(dsum=Sum("budget_requested"))['dsum'], 0)


class EmployeeType(SimpleLookup):
    # cost_type choices
    SAL = 1
    OM = 2
    COST_TYPE_CHOICES = [
        (SAL, _("Salary")),
        (OM, _("O&M")),
    ]
    cost_type = models.IntegerField(choices=COST_TYPE_CHOICES)
    exclude_from_rollup = models.BooleanField(default=False)


class Level(SimpleLookup):
    pass


class Staff(models.Model):
    # STUDENT_PROGRAM_CHOICES
    FSWEP = 1
    COOP = 2
    STUDENT_PROGRAM_CHOICES = [
        (FSWEP, "FSWEP"),
        (COOP, "Coop"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="staff_members",
                                verbose_name=_("project"))
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, verbose_name=_("employee type"))
    lead = models.BooleanField(default=False, verbose_name=_("project lead"), choices=((True, _("yes")), (False, _("no"))))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="staff_members",
                                       verbose_name=_("funding source"), default=1)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"),
                             related_name="staff_instances2")
    name = models.CharField(max_length=255, verbose_name=_("Person name (leave blank if user is selected)"), blank=True,
                            null=True)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("level"))
    student_program = models.IntegerField(choices=STUDENT_PROGRAM_CHOICES, blank=True, null=True,
                                          verbose_name=_("student program"))
    duration_weeks = models.FloatField(default=0, blank=True, null=True, verbose_name=_("duration in weeks"))
    overtime_hours = models.FloatField(default=0, blank=True, null=True, verbose_name=_("overtime in hours"))
    overtime_description = models.TextField(blank=True, null=True, verbose_name=_("overtime description"))
    cost = models.FloatField(blank=True, null=True, verbose_name=_("cost"))

    def __str__(self):
        if self.user:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['employee_type', 'level']
        unique_together = [('project', 'user'), ]


class Collaborator(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="collaborators",
                                verbose_name=_("project"))
    name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
    critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery"), choices=YES_NO_CHOICES)
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return "{}".format(self.name)


class CollaborativeAgreement(models.Model):
    # NEW_OR_EXISTING_CHOICES
    NEW = 1
    EXIST = 2
    NEW_OR_EXISTING_CHOICES = [
        (NEW, _("New")),
        (EXIST, _("Existing")),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="agreements", verbose_name=_("project"))
    partner_organization = models.CharField(max_length=255, blank=True, null=True,
                                            verbose_name=_("collaborating organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
    new_or_existing = models.IntegerField(choices=NEW_OR_EXISTING_CHOICES, verbose_name=_("new or existing"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['partner_organization', ]

    def __str__(self):
        return "{}".format(self.partner_organization)


class OMCategory(models.Model):
    # group choices:
    TRAV = 1
    EQUIP = 2
    MAT = 3
    HR = 4
    OTH = 5
    OTH2 = 6
    GROUP_CHOICES = (
        (TRAV, _("Travel")),
        (EQUIP, _("Equipment Purchase")),
        (MAT, _("Material and Supplies")),
        (HR, _("Human Resources")),
        (OTH, _("Contracts, Leases, Services")),
        (OTH2, _("Other")),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    group = models.IntegerField(choices=GROUP_CHOICES)

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return "{} ({})".format(self.tname, self.get_group_display())

    @property
    def tname(self):
        return getattr(self, str(_("name")))


class OMCost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="om_costs", verbose_name=_("project"))
    om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs", verbose_name=_("category"))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="om_costs",
                                       verbose_name=_("funding source"), default=1)
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))

    def __str__(self):
        return "{}".format(self.om_category)

    class Meta:
        ordering = ['om_category', ]


class CapitalCost(models.Model):
    # category choices:
    IMIT = 1
    LAB = 2
    FIELD = 3
    OTH = 4
    CATEGORY_CHOICES = (
        (IMIT, _("IM / IT - computers, hardware")),
        (LAB, _("Lab Equipment")),
        (FIELD, _("Field Equipment")),
        (OTH, _("Other")),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="capital_costs",
                                verbose_name=_("project"))
    category = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name=_("category"))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="capital_costs",
                                       verbose_name=_("funding source"), default=1)
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))

    def __str__(self):
        return "{}".format(self.get_category_display())

    class Meta:
        ordering = ['category', ]


class GCCost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gc_costs", verbose_name=_("project"))
    recipient_org = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Recipient organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    proposed_title = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name=_("Proposed title of agreement"))
    gc_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name of G&C program"))
    budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))

    def __str__(self):
        return "{} - {}".format(self.recipient_org, self.gc_program)

    class Meta:
        ordering = ['recipient_org', ]


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'projects/project_{0}/{1}'.format(instance.project.id, filename)


class File(models.Model):
    project = models.ForeignKey(Project, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("resource name"))
    file = models.FileField(upload_to=file_directory_path, blank=True, null=True, verbose_name=_("file attachment"))
    external_url = models.URLField(blank=True, null=True, verbose_name=_("external URL"))
    status_report = models.ForeignKey("StatusReport", related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['project', 'status_report', 'name']

    def __str__(self):
        return self.name

    @property
    def ref(self):
        return self.status_report if self.status_report else "Core project"


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


class Milestone(models.Model):
    project = models.ForeignKey(Project, related_name="milestones", on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name=_("name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    class Meta:
        ordering = ['project', 'name']

    def __str__(self):
        # what is the number of this report?
        return "{}".format(self.name)

    @property
    def latest_update(self):
        return self.updates.first()


class StatusReport(models.Model):
    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name="reports", on_delete=models.DO_NOTHING, limit_choices_to={"used_for": 2})
    major_accomplishments = models.TextField(blank=True, null=True,
                                             verbose_name=_(
                                                 "major accomplishments (this can be left blank if reported at the milestone level)"))
    major_issues = models.TextField(blank=True, null=True, verbose_name=_("major issues encountered"))
    target_completion_date = models.DateTimeField(blank=True, null=True, verbose_name=_("target completion date"))
    rationale_for_modified_completion_date = models.TextField(blank=True, null=True,
                                                              verbose_name=_("rationale for a modified completion date"))
    general_comment = models.TextField(blank=True, null=True, verbose_name=_("general comments"))
    section_head_comment = models.TextField(blank=True, null=True, verbose_name=_("section head comment"))
    section_head_reviewed = models.BooleanField(default=False, verbose_name=_("reviewed by section head"))

    date_created = models.DateTimeField(default=timezone.now, verbose_name=_("date created"))
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("created by"),
                                   related_name="status_report_created_by")

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['date_created']

    @property
    def report_number(self):
        return [report for report in self.project.reports.order_by("date_created")].index(self) + 1

    def __str__(self):
        # what is the number of this report?
        return "{}{}".format(
            _("Status Report #"),
            self.report_number,
        )


class MilestoneUpdate(models.Model):
    milestone = models.ForeignKey(Milestone, related_name="updates", on_delete=models.CASCADE)
    status_report = models.ForeignKey(StatusReport, related_name="updates", on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name="updates", on_delete=models.DO_NOTHING, limit_choices_to={"used_for": 3}, default=9)
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        ordering = ['-status_report', 'status']
        unique_together = [('milestone', 'status_report'), ]

    def __str__(self):
        # what is the number of this report?
        return "{} {}".format(
            _("Update on "),
            self.milestone,
        )


class Note(models.Model):
    # fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey(shared_models.Section, related_name="notes2", on_delete=models.CASCADE, blank=True, null=True)
    funding_source = models.ForeignKey(FundingSource, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
    functional_group = models.ForeignKey(FunctionalGroup, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
    summary = models.TextField(blank=True, null=True, verbose_name=_("executive summary"))
    pressures = models.TextField(blank=True, null=True, verbose_name=_("pressures"))

    class Meta:
        unique_together = (("section", "functional_group"), ("funding_source", "functional_group"))

    @property
    def pressures_html(self):
        if self.pressures:
            return textile(self.pressures)

    @property
    def summary_html(self):
        if self.summary:
            return textile(self.summary)


def ref_mat_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'projects/{filename}'


class ReferenceMaterial(SimpleLookup):
    file = models.FileField(upload_to=ref_mat_directory_path, verbose_name=_("file attachment"))
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, related_name="reference_materials2",
                               verbose_name=_("region"), blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    @property
    def file_display(self):
        if self.file:
            return mark_safe(
                f"<a href='{self.file.url}'> <span class='mdi mdi-file'></span></a>"
            )

    class Meta:
        ordering = ["region", "file"]


@receiver(models.signals.post_delete, sender=ReferenceMaterial)
def auto_delete_ReferenceMaterial_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=ReferenceMaterial)
def auto_delete_ReferenceMaterial_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = ReferenceMaterial.objects.get(pk=instance.pk).file
    except ReferenceMaterial.DoesNotExist:
        return False

    new_file = instance.file
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
