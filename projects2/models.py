from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from markdown import markdown

from dm_apps import custom_widgets
from lib.functions.custom_functions import fiscal_year, listrify
from shared_models import models as shared_models
# Choices for language
from shared_models.models import SimpleLookup, Lookup, HelpTextLookup
from shared_models.utils import get_metadata_string

YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)


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
    class Meta:
        ordering = ['id', ]


class FundingSource(SimpleLookup):
    funding_source_choices = (
        (1, _("A-base")),  # #a7aef9
        (2, _("B-base")),  # #d9a7f9
        (3, _("C-base")),  # #eff9a7
    )
    name = models.CharField(max_length=255)
    funding_source_type = models.IntegerField(choices=funding_source_choices)

    def __str__(self):
        return f"{self.tname} ({self.get_funding_source_type_display()})"

    class Meta:
        ordering = ['funding_source_type', 'name', ]
        unique_together = [('funding_source_type', 'name'), ]


class Tag(SimpleLookup):
    pass


class HelpText(HelpTextLookup):
    pass


class Project(models.Model):
    # basic
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, related_name="projects2",
                                verbose_name=_("section"))
    title = custom_widgets.OracleTextField(verbose_name=_("Project title"))
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name=_("activity type"))
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                         verbose_name=_("Functional group"))
    default_funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, blank=False, null=True, related_name="projects",
                                               verbose_name=_("primary funding source"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags / keywords"), related_name="projects")

    # HTML field
    overview = models.TextField(blank=True, null=True, verbose_name=_("Project overview"))

    is_hidden = models.BooleanField(default=False, verbose_name=_("Should the project be hidden from other users?"))

    # calculated fields
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start date of project"), editable=False)
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project"), editable=False)
    fiscal_years = models.ManyToManyField(shared_models.FiscalYear, editable=False, verbose_name=_("fiscal years"))
    funding_sources = models.ManyToManyField(FundingSource, editable=False, verbose_name=_("complete list of funding sources"))
    staff_search_field = models.CharField(editable=False, max_length=1000, blank=True, null=True)
    lead_staff = models.ManyToManyField("Staff", editable=False, verbose_name=_("project leads"))


    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_project", blank=True, null=True)

    def save(self, *args, **kwargs):
        project_years = self.years.order_by("fiscal_year")  # being explicit about ordering here is impnt

        # list of things to do if there are project years
        if project_years.exists():
            # set the start and end dates based on project years
            self.start_date = self.years.first().start_date
            self.end_date = self.years.last().end_date

            # reset some calculated fields
            self.staff_search_field = ""
            self.fiscal_years.clear()
            self.funding_sources.clear()
            self.lead_staff.clear()

            for y in project_years:

                # search for and staff and concatenate into a search field
                for s in y.staff_set.all():
                    if s.smart_name:
                        self.staff_search_field += s.smart_name + " "
                    if s.is_lead:
                        self.lead_staff.add(s)
                # add the fiscal year
                self.fiscal_years.add(y.fiscal_year)

                # cycle through all costs and pull out funding sources
                for c in y.costs:
                    self.funding_sources.add(c.funding_source)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    @property
    def dates(self):
        my_str = date(self.start_date)
        if self.end_date:
            my_str += f" &rarr; {date(self.end_date)}"
        return mark_safe(my_str)

    @property
    def has_unsubmitted_years(self):
        return self.years.filter(submitted__isnull=True).exists()

    @property
    def region(self):
        return self.division.branch.region

    @property
    def division(self):
        return self.section.division

    @property
    def overview_html(self):
        if self.overview:
            return mark_safe(markdown(self.overview))


class ProjectYear(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="years", verbose_name=_("project"))
    start_date = models.DateTimeField(default=timezone.now, verbose_name=_("Start date of project"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project"))

    # HTML field
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("deliverables / activities"))
    # HTML field
    priorities = models.TextField(blank=True, null=True, verbose_name=_("year-specific priorities"))

    # SPECIALIZED EQUIPMENT
    ########################
    requires_specialized_equipment = models.BooleanField(default=False, verbose_name=_(
        "Will the project require the purchase, design or fabrication of specialized laboratory or field equipment?"))
    technical_service_needs = models.TextField(blank=True, null=True, verbose_name=_("What technical services are being requested?"))
    mobilization_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Do you anticipate needing assistance with mobilization/demobilization of this equipment?"))

    # FIELD COMPONENT
    #################
    has_field_component = models.BooleanField(default=False, verbose_name=_("Does this project involved a field component?"))
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
    requires_field_staff = models.BooleanField(default=False, verbose_name=_("Do you require field support staff?"))
    field_staff_needs = models.TextField(blank=True, null=True, verbose_name=_("If so, please include some additional detail, "
                                                                               "e.g., how many people are likely to be required and when"))

    # DATA COMPONENT
    ################
    has_data_component = models.BooleanField(default=False, verbose_name=_("Will new data be collected or generated?"))
    data_collected = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    data_products = models.TextField(blank=True, null=True, verbose_name=_("What data products will be generated (e.g. models, indices)?"))
    open_data_eligible = models.BooleanField(default=False, verbose_name=_("Are these data / data products eligible "
                                                                           "to be placed on the Open Data Platform?"))
    data_storage_plan = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving plan"))
    data_management_needs = models.TextField(blank=True, null=True, verbose_name=_("Describe what data management support is required, "
                                                                                   "if any."))

    # LAB COMPONENT
    ###############
    has_lab_component = models.BooleanField(default=False, verbose_name=_("Does this project involve laboratory work?"))
    # maritimes only
    requires_abl_services = models.BooleanField(default=False, verbose_name=_(
        "Does this project require the services of Aquatic Biotechnology Lab (ABL)?"))
    requires_lab_space = models.BooleanField(default=False, verbose_name=_("Is laboratory space required?"))
    requires_other_lab_support = models.BooleanField(default=False, verbose_name=_(
        "Does this project require other specialized laboratory support or services (provide details below)?"))
    other_lab_support_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Describe other laboratory requirements relevant for project planning purposes."))

    it_needs = models.TextField(blank=True, null=True, verbose_name=_("Special IT requirements (software, licenses, hardware)"))
    additional_notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))

    # CODING
    ########
    # coding
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_projects2',
                                              verbose_name=_("responsibility center (if known)"))
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_projects2', verbose_name=_("allotment code (if known)"))
    existing_project_codes = models.ManyToManyField(shared_models.Project, blank=True, verbose_name=_("existing project codes (if known)"),
                                                    related_name="projects")

    # admin
    submitted = models.DateTimeField(editable=False, blank=True, null=True)
    allocated_budget = models.FloatField(blank=True, null=True, verbose_name=_("Allocated budget"))
    notification_email_sent = models.DateTimeField(blank=True, null=True, verbose_name=_("Notification Email Sent"), editable=False)
    administrative_notes = models.TextField(blank=True, null=True, verbose_name=_("administrative notes"))

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_projectyear", blank=True,
                                    null=True)

    # calculated
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, editable=False, blank=True, null=True,
                                    verbose_name=_("fiscal year"))
    coding = models.TextField(blank=True, null=True, verbose_name=_("financial coding"), editable=False)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    class Meta:
        ordering = ["project", "fiscal_year"]
        unique_together = ["project", "fiscal_year"]

    def save(self, *args, **kwargs):
        # get the fiscal year based on the start date
        if self.start_date:
            self.fiscal_year_id = fiscal_year(self.start_date, sap_style=True)
        # save the project whenever a project year is saved
        self.coding = self.get_coding()
        self.project.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.fiscal_year) if self.fiscal_year else gettext("NEW PROJECT YEAR")

    @property
    def costs(self):
        om_qry = self.omcost_set
        capital_qry = self.capitalcost_set
        staff_qry = self.staff_set
        my_list = []
        if om_qry.exists():
            my_list.extend([c for c in om_qry.all()])
        if capital_qry.exists():
            my_list.extend([c for c in capital_qry.all()])
        if staff_qry.exists():
            my_list.extend([c for c in staff_qry.all()])
        return my_list

    def add_all_om_costs(self):
        for obj in OMCategory.objects.all():
            if not self.omcost_set.filter(om_category=obj).exists():
                OMCost.objects.create(
                    project_year=self,
                    om_category=obj,
                    funding_source=self.project.default_funding_source
                )

    def clear_empty_om_costs(self):
        self.omcost_set.filter(Q(amount__isnull=True)|Q(amount=0)).filter(description__isnull=True).delete()

    @property
    def dates(self):
        my_str = date(self.start_date)
        if self.end_date:
            my_str += f" &rarr; {date(self.end_date)}"
        return mark_safe(my_str)

    @property
    def deliverables_html(self):
        if self.deliverables:
            return mark_safe(markdown(self.deliverables))

    @property
    def priorities_html(self):
        if self.priorities:
            return mark_safe(markdown(self.priorities))

    def get_project_leads_as_users(self):
        return [s.user for s in self.staff_set.filter(is_lead=True)]

    def get_coding(self):
        if self.responsibility_center:
            rc = self.responsibility_center.code
        else:
            rc = "xxxxx"
        if self.allotment_code:
            ac = self.allotment_code.code
        else:
            ac = "xxx"

        # needs to have a value for field "id" before this many-to-many relationship can be used
        if self.id and self.existing_project_codes.exists() >= 1:
            pc = listrify([project_code.code for project_code in self.existing_project_codes.all()])
            if self.existing_project_codes.count() > 1:
                pc = "[" + pc + "]"
        else:
            pc = "xxxxx"
        return "{}-{}-{}".format(rc, ac, pc)


class GenericCost(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, verbose_name=_("project year"))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, verbose_name=_("funding source"), default=1)
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"), blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.amount: self.amount = 0

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class EmployeeType(SimpleLookup):
    cost_type_choices = [
        (1, _("Salary")),
        (2, _("O&M")),
    ]
    cost_type = models.IntegerField(choices=cost_type_choices)
    exclude_from_rollup = models.BooleanField(default=False)


class Level(SimpleLookup):
    pass


class Staff(GenericCost):
    student_program_choices = [
        (1, "FSWEP"),
        (2, "Coop"),
    ]
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, verbose_name=_("employee type"))
    is_lead = models.BooleanField(default=False, verbose_name=_("project lead"), choices=((True, _("yes")), (False, _("no"))))
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"),
                             related_name="staff_instances2")
    name = models.CharField(max_length=255, verbose_name=_("Person name (leave blank if user is selected)"), blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("level"))
    student_program = models.IntegerField(choices=student_program_choices, blank=True, null=True, verbose_name=_("student program"))
    duration_weeks = models.FloatField(default=0, blank=True, null=True, verbose_name=_("duration (weeks)"))
    overtime_hours = models.FloatField(default=0, blank=True, null=True, verbose_name=_("overtime (hours)"))
    overtime_description = models.TextField(blank=True, null=True, verbose_name=_("overtime description"))

    def __str__(self):
        if self.user:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['employee_type', 'level']
        unique_together = [('project_year', 'user'), ]

    @property
    def smart_name(self):
        if self.user or self.name:
            return self.user.get_full_name() if self.user else self.name


class OMCategory(models.Model):
    group_choices = (
        (1, _("Travel")),
        (2, _("Equipment Purchase")),
        (3, _("Material and Supplies")),
        (4, _("Human Resources")),
        (5, _("Contracts, Leases, Services")),
        (6, _("Other")),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    group = models.IntegerField(choices=group_choices)

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return f"{self.tname} ({self.get_group_display()})"

    @property
    def tname(self):
        return getattr(self, str(_("name")))


class OMCost(GenericCost):
    om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs", verbose_name=_("category"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    @property
    def category_type(self):
        return self.om_category.get_group_display()

    def __str__(self):
        return f"{self.om_category}"

    class Meta:
        ordering = ['om_category', ]


class CapitalCost(GenericCost):
    category_choices = (
        (1, _("IM / IT - computers, hardware")),
        (2, _("Lab Equipment")),
        (3, _("Field Equipment")),
        (4, _("Other")),
    )
    category = models.IntegerField(choices=category_choices, verbose_name=_("category"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    def __str__(self):
        return f"{self.get_category_display()}"

    class Meta:
        ordering = ['category', ]


class GCCost(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="gc_costs", verbose_name=_("project year"))
    recipient_org = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Recipient organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    proposed_title = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name=_("Proposed title of agreement"))
    gc_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name of G&C program"))
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"))

    def __str__(self):
        return f"{self.recipient_org} - {self.gc_program}"

    class Meta:
        ordering = ['recipient_org', ]


class Collaborator(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="collaborators", verbose_name=_("project year"))
    name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
    critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery"), choices=YES_NO_CHOICES)
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return "{}".format(self.name)


class CollaborativeAgreement(models.Model):
    new_or_existing_choices = [
        (1, _("New")),
        (2, _("Existing")),
    ]
    partner_organization = models.CharField(max_length=255, blank=True, null=True,
                                            verbose_name=_("collaborating organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
    new_or_existing = models.IntegerField(choices=new_or_existing_choices, verbose_name=_("new or existing"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="agreements", verbose_name=_("project year"))

    class Meta:
        ordering = ['partner_organization', ]

    def __str__(self):
        return "{}".format(self.partner_organization)


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'projects/project_{0}/{1}'.format(instance.project.id, filename)


class File(models.Model):
    project = models.ForeignKey(Project, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("resource name"))
    file = models.FileField(upload_to=file_directory_path, blank=True, null=True, verbose_name=_("file attachment"))
    project_year = models.ForeignKey(ProjectYear, related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    status_report = models.ForeignKey("StatusReport", related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, verbose_name=_("external URL"))
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['project', 'project_year', 'status_report', 'name']

    def __str__(self):
        return self.name

    @property
    def ref(self):
        return self.status_report if self.status_report else "Core project"


class StatusReport(models.Model):
    status_choices = (
        (3, _("On-track")),
        (4, _("Complete")),
        (5, _("Encountering issues")),
        (6, _("Aborted / cancelled")),
    )
    project_year = models.ForeignKey(ProjectYear, related_name="reports", on_delete=models.CASCADE)
    status = models.IntegerField(default=1, editable=False, choices=status_choices)
    major_accomplishments = models.TextField(blank=True, null=True, verbose_name=_(
        "major accomplishments (this can be left blank if reported at the milestone level)"))
    major_issues = models.TextField(blank=True, null=True, verbose_name=_("major issues encountered"))
    target_completion_date = models.DateTimeField(blank=True, null=True, verbose_name=_("target completion date"))
    rationale_for_modified_completion_date = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for a modified completion date"))
    general_comment = models.TextField(blank=True, null=True, verbose_name=_("general comments"))
    section_head_comment = models.TextField(blank=True, null=True, verbose_name=_("section head comment"))
    section_head_reviewed = models.BooleanField(default=False, verbose_name=_("reviewed by section head"))

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_status_report", blank=True,
                                    null=True)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']

    @property
    def report_number(self):
        return [report for report in self.project_year.reports.order_by("date_created")].index(self) + 1

    def __str__(self):
        # what is the number of this report?
        return "{}{}".format(
            gettext("Status Report #"),
            self.report_number,
        )


class Milestone(models.Model):
    project_year = models.ForeignKey(ProjectYear, related_name="milestones", on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name=_("name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    class Meta:
        ordering = ['project_year', 'name']

    def __str__(self):
        return self.name

    @property
    def latest_update(self):
        return self.updates.first()


class MilestoneUpdate(models.Model):
    status_choices = (
        (7, _("In progress")),
        (8, _("Completed")),
        (9, _("Aborted / cancelled")),
    )
    milestone = models.ForeignKey(Milestone, related_name="updates", on_delete=models.CASCADE)
    status_report = models.ForeignKey(StatusReport, related_name="updates", on_delete=models.CASCADE)
    status = models.IntegerField(default=1, editable=False, choices=status_choices)
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        ordering = ['-status_report', 'status']
        unique_together = [('milestone', 'status_report'), ]

    def __str__(self):
        # what is the number of this report?
        return "{} {}".format(
            gettext("Update on "),
            self.milestone,
        )


#
# class Note(models.Model):
#     # fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
#     section = models.ForeignKey(shared_models.Section, related_name="notes2", on_delete=models.CASCADE, blank=True, null=True)
#     funding_source = models.ForeignKey(FundingSource, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
#     functional_group = models.ForeignKey(FunctionalGroup, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
#     summary = models.TextField(blank=True, null=True, verbose_name=_("executive summary"))
#     pressures = models.TextField(blank=True, null=True, verbose_name=_("pressures"))
#
#     class Meta:
#         unique_together = (("section", "functional_group"), ("funding_source", "functional_group"))
#
#     @property
#     def pressures_html(self):
#         if self.pressures:
#             return textile(self.pressures)
#
#     @property
#     def summary_html(self):
#         if self.summary:
#             return textile(self.summary)


def ref_mat_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'projects/{filename}'


class ReferenceMaterial(SimpleLookup):
    file = models.FileField(upload_to=ref_mat_directory_path, verbose_name=_("file attachment"))
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, related_name="reference_materials2",
                               verbose_name=_("region"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at)

    @property
    def file_display(self):
        if self.file:
            return mark_safe(
                f"<a href='{self.file.url}'> <span class='mdi mdi-file'></span></a>"
            )

    class Meta:
        ordering = ["region", "file"]
