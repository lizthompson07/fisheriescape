import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from textile import textile
from lib.functions.custom_functions import fiscal_year, listrify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models

from dm_apps import custom_widgets

# Choices for language
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


class Theme(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Program(models.Model):
    is_core_choices = (
        # (None, _("Unknown")),
        (True, _("Core")),
        (False, _("Flex")),
    )

    national_responsibility_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="National responsibilty (English)")
    national_responsibility_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name="National responsibilty (French)")
    program_inventory = models.CharField(max_length=255, blank=True, null=True, verbose_name="program inventory")
    funding_source_and_type = models.CharField(max_length=255, blank=True, null=True)
    regional_program_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="regional program name (English)")
    regional_program_name_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name="regional program name (French)")
    short_name = models.CharField(max_length=255, blank=True, null=True)
    is_core = models.BooleanField(verbose_name=_("Is program core or flex?"), choices=is_core_choices)
    examples = models.CharField(max_length=255, blank=True, null=True)
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, related_name="programs", blank=True, null=True)

    @property
    def regions(self):
        projects = self.projects.filter(section__isnull=False)
        return listrify(list(set([str(p.section.division.branch.region) for p in projects])))

    @property
    def tname(self):
        # check to see if a french value is given
        if getattr(self, str(_("regional_program_name_eng"))):
            regional_program_name = "{}".format(getattr(self, str(_("regional_program_name_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            regional_program_name = "{}".format(self.regional_program_name_eng)

        # check to see if a french value is given
        if getattr(self, str(_("national_responsibility_eng"))):
            national_responsibility = "{}".format(getattr(self, str(_("national_responsibility_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            national_responsibility = "{}".format(self.national_responsibility_eng)

        return "{} - {}".format(regional_program_name, national_responsibility)

    def __str__(self):

        # check to see if a french value is given
        if getattr(self, str(_("regional_program_name_eng"))):
            regional_program_name = "{}".format(getattr(self, str(_("regional_program_name_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            regional_program_name = "{}".format(self.regional_program_name_eng)

        # check to see if a french value is given
        if getattr(self, str(_("national_responsibility_eng"))):
            national_responsibility = "{}".format(getattr(self, str(_("national_responsibility_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            national_responsibility = "{}".format(self.national_responsibility_eng)

        my_str = "{} - {} ({})".format(national_responsibility, regional_program_name, self.get_is_core_display())

        if self.examples:
            return "{} (e.g., {})".format(my_str, self.examples)
        else:
            return "{}".format(my_str)

    class Meta:
        ordering = [_("national_responsibility_eng"), _("regional_program_name_eng")]


class FunctionalGroup(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, related_name="functional_groups", blank=True, null=True)
    sections = models.ManyToManyField(shared_models.Section, related_name="functional_groups")

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class ActivityType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['id', ]


class FundingSourceType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class FundingSource(models.Model):
    name = models.CharField(max_length=500)
    nom = models.CharField(max_length=500, blank=True, null=True)
    funding_source_type = models.ForeignKey(FundingSourceType, on_delete=models.DO_NOTHING, related_name="funding_sources")

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            my_str = "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.name)
        return "{} - {}".format(str(self.funding_source_type), my_str)

    class Meta:
        ordering = ['funding_source_type', 'name', ]


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    nom = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = [_('name'), ]


class Status(models.Model):
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
        (True, _("National")),
        (False, _("Regional")),
    )

    year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                             verbose_name=_("fiscal year"), default=fiscal_year(next=True, sap_style=True))
    # basic
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, related_name="projects",
                                verbose_name=_("section"))
    project_title = custom_widgets.OracleTextField(verbose_name=_("Project title"))
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name=_("activity type"))
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("Functional group"))
    default_funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, blank=False, null=True,
                                               verbose_name=_("primary funding source"))
    programs = models.ManyToManyField(Program, blank=True, verbose_name=_("Science regional program name(s)"), related_name="projects")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags / keywords"), related_name="projects")

    # details
    is_national = models.NullBooleanField(default=False, verbose_name=_("National or regional?"), choices=is_national_choices)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True,
                               verbose_name=_("project status"), limit_choices_to={"used_for": 1})

    # DELETE FOLLOWING TWO FIELDS
    is_competitive = models.NullBooleanField(default=False, verbose_name=_("Is the funding competitive?"))
    is_approved = models.NullBooleanField(verbose_name=_("Has this project already been approved"))

    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start date of project"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project"))

    # HTML field
    description = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))
    # description_html = models.TextField(blank=True, null=True, verbose_name=_("Project objective & description"))

    # HTML field
    priorities = models.TextField(blank=True, null=True, verbose_name=_("Project-specific priorities"))
    # HTML field
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("Project deliverables / activities"))

    # data
    #######
    # HTML field
    data_collection = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    # HTML field
    data_sharing = models.TextField(blank=True, null=True,
                                    verbose_name=_(
                                        "Which of these data / data products will be placed on the Open Data Platform this year?"))
    # HTML field
    data_storage = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving Plan"))
    metadata_url = models.CharField(max_length=1000, blank=True, null=True,
                                    verbose_name=_("Provide link to existing metadata record, if available"))

    # needs
    ########

    # DELETE ME!! #
    regional_dm_needs = models.TextField(blank=True, null=True,
                                         verbose_name=_("Describe assistance required from the branch data manager, if applicable"))
    # DELETE ME!! #
    sectional_dm_needs = models.TextField(blank=True, null=True,
                                          verbose_name=_("Describe assistance required from the section data manager, if applicable"))

    # HTML field
    vehicle_needs = models.TextField(blank=True, null=True,
                                     verbose_name=_(
                                         "Describe need for vehicle (type of vehicle, number of weeks, time-frame)"))
    # HTML field
    it_needs = models.TextField(blank=True, null=True, verbose_name=_("Special IT requirements (software, licenses, hardware)"))
    # HTML field
    chemical_needs = models.TextField(blank=True, null=True,
                                      verbose_name=_(
                                          "Please provide details regarding chemical needs and the plan for storage and disposal."))
    # HTML field
    ship_needs = models.TextField(blank=True, null=True, verbose_name=_("Ship (Coast Guard, charter vessel) Requirements"))

    # HTML field
    notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))

    # coding
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_projects',
                                              verbose_name=_("responsibility center (if known)"))
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_projects', verbose_name=_("allotment code (if known)"))
    existing_project_codes = models.ManyToManyField(shared_models.Project, blank=True, verbose_name=_("existing project codes (if known)"))

    feedback = models.TextField(blank=True, null=True,
                                verbose_name=_("Do you have any feedback you would like to submit about this process"))

    # admin
    submitted = models.BooleanField(default=False, verbose_name=_("Submit project for review"))
    # approved = models.BooleanField(default=False, verbose_name=_("approved"))
    approved = models.BooleanField(default=False, verbose_name=_("approved"))
    # section_head_feedback = models.TextField(blank=True, null=True, verbose_name=_("section head feedback"))

    # manager_approved = models.BooleanField(default=False, verbose_name=_("division manager approved"))
    # manager_feedback = models.TextField(blank=True, null=True, verbose_name=_("division manager feedback"))

    # rds_approved = models.BooleanField(default=False, verbose_name=_("RDS approved"))
    # rds_feedback = models.TextField(blank=True, null=True, verbose_name=_("RDS feedback"))

    meeting_notes = models.TextField(blank=True, null=True, verbose_name=_("meeting notes"))

    is_hidden = models.NullBooleanField(default=False, verbose_name=_("Should the project be hidden from other users?"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{}".format(self.project_title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        super().save(*args, **kwargs)

    # @property
    # def approved(self):
    #     return self.submitted and self.approved

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
            if item.funding_source:
                my_list.append(item.funding_source)

        for item in self.om_costs.all():
            if item.funding_source:
                my_list.append(item.funding_source)

        for item in self.capital_costs.all():
            if item.funding_source:
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
    def core_status(self):
        return "/".join(list(set(([program.get_is_core_display() for program in self.programs.all()]))))

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
    def a_salary(self):
        funding_source_id = 1
        staff_salary = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        return nz(staff_salary, 0)

    @property
    def a_om(self):
        funding_source_id = 1
        staff_om = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        other_om = self.om_costs.filter(funding_source_id=funding_source_id
                                        ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(staff_om, 0) + nz(other_om, 0)

    @property
    def a_capital(self):
        funding_source_id = 1
        capital = self.capital_costs.filter(funding_source=funding_source_id
                                            ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(capital, 0)

    @property
    def b_salary(self):
        funding_source_id = 2
        staff_salary = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        return nz(staff_salary, 0)

    @property
    def b_om(self):
        funding_source_id = 2
        staff_om = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        other_om = self.om_costs.filter(funding_source_id=funding_source_id
                                        ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(staff_om, 0) + nz(other_om, 0)

    @property
    def b_capital(self):
        funding_source_id = 2
        capital = self.capital_costs.filter(funding_source=funding_source_id
                                            ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(capital, 0)

    @property
    def c_salary(self):
        funding_source_id = 3
        staff_salary = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=1, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        return nz(staff_salary, 0)

    @property
    def c_om(self):
        funding_source_id = 3
        staff_om = self.staff_members.filter(
            employee_type__exclude_from_rollup=False, employee_type__cost_type=2, funding_source_id=funding_source_id
        ).order_by("cost").aggregate(dsum=Sum("cost"))['dsum']
        other_om = self.om_costs.filter(funding_source_id=funding_source_id
                                        ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(staff_om, 0) + nz(other_om, 0)

    @property
    def c_capital(self):
        funding_source_id = 3
        capital = self.capital_costs.filter(funding_source=funding_source_id
                                            ).order_by("budget_requested").aggregate(dsum=Sum("budget_requested"))['dsum']
        return nz(capital, 0)

    @property
    def total_salary(self):
        return self.a_salary + self.b_salary + self.c_salary

    @property
    def total_om(self):
        return self.a_om + self.b_om + self.c_om

    @property
    def total_capital(self):
        return self.a_capital + self.b_capital + self.c_capital


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
    exclude_from_rollup = models.BooleanField(default=False)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class Level(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"),
                             related_name="staff_instances")
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
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("created by"))

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


class SectionNote(models.Model):
    section = models.ForeignKey(shared_models.Section, related_name="notes", on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="section_notes", on_delete=models.CASCADE)
    pressures = models.TextField(blank=True, null=True)
    general_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(
            self.fiscal_year,
            str(self.section).title(),
            _("section notes").title(),
        )

    @property
    def pressures_html(self):
        if self.pressures:
            return textile(self.pressures)

    @property
    def general_notes_html(self):
        if self.general_notes:
            return textile(self.general_notes)
