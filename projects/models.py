from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from textile import textile

from lib.functions.fiscal_year import fiscal_year
from scifi import models as scifi_models
from django.utils.translation import gettext_lazy as _
import markdown

# Choices for language
ENG = 1
FRE = 2
LANGUAGE_CHOICES = (
    (ENG, 'English'),
    (FRE, 'French'),
)


# Create your models here.

class BudgetCode(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name"))

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        ordering = ['code', ]


class Division(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Section(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    nom = models.CharField(max_length=255, blank=True, null=True)
    division = models.ForeignKey(Division, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="sections")
    section_head = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                     verbose_name=_("section head"))

    def __str__(self):
        return "{} ({})".format(getattr(self, str(_("name"))), self.division)

    class Meta:
        ordering = ['name', ]


class Program(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Status(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class FiscalYear(models.Model):
    full = models.TextField(blank=True, null=True)
    short = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.full)

    class Meta:
        ordering = ['id', ]


class Project(models.Model):
    # fiscal_year = models.CharField(max_length=50, default="2019-2020", verbose_name=_("fiscal year"))
    year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                     verbose_name=_("fiscal year"), default=fiscal_year(next=True, sap_style=True))
    # basic
    project_title = models.TextField(verbose_name=_("Project title"))
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                verbose_name=_("section (Division)"))
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("program"))

    # coding
    responsibility_center = models.ForeignKey(scifi_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_projects',
                                              verbose_name=_("responsibility center (if known)"))
    allotment_code = models.ForeignKey(scifi_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_projects', verbose_name=_("allotment code (if known)"))
    existing_project_code = models.ForeignKey(scifi_models.Project, on_delete=models.DO_NOTHING, blank=True, null=True,
                                              related_name='projects_projects', verbose_name=_("existing project code (if known)"))

    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True,
                               verbose_name=_("project status"))
    approved = models.NullBooleanField(default=False, verbose_name=_("Has this project already been approved"))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"))

    # details
    description = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))
    priorities = models.TextField(blank=True, null=True, verbose_name=_(
        "Project-specific priorities (e.g., what will be the project emphasis in this fiscal year)"))
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("Project deliverables (bulleted form)"))

    description_html = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))
    priorities_html = models.TextField(blank=True, null=True, verbose_name=_(
        "Project-specific priorities"))
    deliverables_html = models.TextField(blank=True, null=True, verbose_name=_("Project deliverables"))

    # data
    data_collection = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    data_sharing = models.TextField(blank=True, null=True,
                                    verbose_name=_(
                                        "Which of these data will be share-worthy and what is the plan to share / disseminate"))
    data_storage = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving Plan"))
    metadata_url = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("please provide link to metadata, if available"))

    # needs
    regional_dm = models.NullBooleanField(
        verbose_name=_("Does the program require assistance of the branch data manager"))
    regional_dm_needs = models.TextField(blank=True, null=True,
                                         verbose_name=_("If yes, please describe"))
    sectional_dm = models.NullBooleanField(
        verbose_name=_("Does the program require assistance of the section's data manager"))
    sectional_dm_needs = models.TextField(blank=True, null=True,
                                          verbose_name=_("If yes, please describe"))
    vehicle_needs = models.TextField(blank=True, null=True,
                                     verbose_name=_(
                                         "Describe need for vehicle (type of vehicle, number of weeks, time-frame)"))
    it_needs = models.TextField(blank=True, null=True, verbose_name=_("IT requirements (software, licenses, hardware)"))
    chemical_needs = models.TextField(blank=True, null=True,
                                      verbose_name=_(
                                          "Please provide details regarding chemical needs and the plan for storage and disposal."))
    ship_needs = models.TextField(blank=True, null=True, verbose_name=_("Ship (Coast Guard, charter vessel) Requirements"))

    # admin
    feedback = models.TextField(blank=True, null=True,
                                verbose_name=_("Do you have any feedback you would like to submit about this process"))
    submitted = models.BooleanField(default=False, verbose_name=_("Submit project for review"))
    section_head_approved = models.DateTimeField(blank=True, null=True)
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                              verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))

    class Meta:
        ordering = ['-year', 'section__division', 'section', 'project_title']

    def __str__(self):
        return "{}".format(self.project_title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        if self.description:
            self.description_html = textile(self.description)
        if self.priorities:
            self.priorities_html = textile(self.priorities)
        if self.deliverables:
            self.deliverables_html = textile(self.deliverables)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})

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
        if self.existing_project_code:
            pc = self.existing_project_code.code
        else:
            pc = "xxxxx"
        return "{}-{}-{}".format(rc, ac, pc)


class EmployeeType(models.Model):
    # cost_type choices
    SAL = 1
    OM = 2
    COST_TYPE_CHOICES = [
        (SAL, _("Salary")),
        (OM, _("O&M")),
    ]

    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    cost_type = models.IntegerField(choices=COST_TYPE_CHOICES)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))


class Level(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class FundingSource(models.Model):
    name = models.CharField(max_length=50)
    nom = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Staff(models.Model):
    # STUDENT_PROGRAM_CHOICES
    FSWEP = 1
    COOP = 1
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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"))
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


class Collaborator(models.Model):
    # TYPE_CHOICES
    COL = 1
    PAR = 2
    TYPE_CHOICES = [
        (COL, _("Collaborator")),
        (PAR, _("Partner")),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="collaborators",
                                verbose_name=_("project"))
    name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name=_("type"))
    critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery"))
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
                                            verbose_name=_("partner organization"))
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
    GROUP_CHOICES = (
        (TRAV, _("Travel")),
        (EQUIP, _("Equipment Purchase")),
        (MAT, _("Material and Supplies")),
        (HR, _("Human Resources")),
        (OTH, _("Contracts, Leases, Services")),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    group = models.IntegerField(choices=GROUP_CHOICES)

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return "{} ({})".format(getattr(self, str(_("name"))), self.get_group_display())


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
