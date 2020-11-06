from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext

from dm_apps import custom_widgets
from lib.functions.custom_functions import fiscal_year
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


class HelpText(HelpTextLookup):
    pass


class Project(models.Model):
    is_national_choices = (
        (None, _("Unknown")),
        (1, _("National")),
        (0, _("Regional")),
    )

    # basic
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, related_name="projects2",
                                verbose_name=_("section"))
    title = custom_widgets.OracleTextField(verbose_name=_("Project title"))
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name=_("activity type"))
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                         verbose_name=_("Functional group"))
    default_funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, blank=False, null=True, related_name="projects",
                                               verbose_name=_("primary funding source"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags / keywords (used for searching)"), related_name="projects")

    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start date of project"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project (leave blank is indeterminate"))

    # HTML field
    overview = models.TextField(blank=True, null=True, verbose_name=_("Project overview"))

    is_hidden = models.BooleanField(default=False, verbose_name=_("Should the project be hidden from other users?"))

    # coding
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_projects2',
                                              verbose_name=_("responsibility center (if known)"))
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_projects2', verbose_name=_("allotment code (if known)"))
    existing_project_codes = models.ManyToManyField(shared_models.Project, blank=True, verbose_name=_("existing project codes (if known)"),
                                                    related_name="projects")

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_project", blank=True, null=True)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.project_title


class ProjectYear(models.Model):
    year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True,
                             verbose_name=_("fiscal year"), default=fiscal_year(next=True, sap_style=True))
    # HTML field
    priorities = models.TextField(blank=True, null=True, verbose_name=_("Year-specific priorities"))
    # HTML field
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("Deliverables / activities specific to year"))

    # SPECIALIZED EQUIPMENT
    ########################
    requires_specialized_equipment = models.BooleanField(default=False, verbose_name=_(
        "Will the project require the purchase, design or fabrication of specialized laboratory or field equipment?"))
    technical_service_needs = models.TextField(blank=True, null=True, verbose_name=_("What technical services are being requested?"))
    mobilization_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Do you anticipate needing assistance with mobilization/demobilization of this equipment?"))

    # FIELD COMPONENT
    ########
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
    requires_field_staff = models.BooleanField(default=False, verbose_name=_("Does this project involved a field component?"))
    field_staff_needs = models.TextField(blank=True, null=True, verbose_name=_("If so, please include some additional detail, "
                                                                               "e.g., how many people are likely to be required and when"))

    # DATA
    #######
    has_data_component = models.BooleanField(default=False, verbose_name=_("Will new data be collected or generated?"))
    data_collected = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    data_products = models.TextField(blank=True, null=True, verbose_name=_("What data products will be generated (e.g. models, indices)?"))
    open_data_eligible = models.BooleanField(default=True, verbose_name=_("Are these data / data products eligible "
                                                                          "to be placed on the Open Data Platform?"))
    data_storage_plan = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving Plan"))
    data_management_needs = models.TextField(blank=True, null=True, verbose_name=_("Describe what data management support is required, "
                                                                                   "if any."))

    # LAB WORK
    ##########
    has_lab_component = models.BooleanField(default=False, verbose_name=_("Does this project involve laboratory work?"))
    # maritimes only
    abl_services_required = models.BooleanField(default=False, verbose_name=_(
        "Does this project require the services of Aquatic Biotechnology Lab (ABL)?"))
    lab_space_required = models.BooleanField(default=False, verbose_name=_("Is laboratory space required?"))
    chemical_needs = models.TextField(blank=True, null=True, verbose_name=_("Please provide details regarding chemical "
                                                                            "needs and the plan for storage and disposal."))

    it_needs = models.TextField(blank=True, null=True, verbose_name=_("Special IT requirements (software, licenses, hardware)"))
    additional_notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))

    submitted = models.DateTimeField(editable=False)

    # admin
    allocated_budget = models.FloatField(blank=True, null=True, verbose_name=_("Allocated budget"))
    notification_email_sent = models.DateTimeField(blank=True, null=True, verbose_name=_("Notification Email Sent"))

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_projectyear", blank=True,
                                    null=True)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)


class EmployeeType(SimpleLookup):
    cost_type_choices = [
        (1, _("Salary")),
        (2, _("O&M")),
    ]
    cost_type = models.IntegerField(choices=cost_type_choices)
    exclude_from_rollup = models.BooleanField(default=False)


class Level(SimpleLookup):
    pass


class Staff(models.Model):
    student_program_choices = [
        (1, "FSWEP"),
        (2, "Coop"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="staff_members", verbose_name=_("project"))
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, verbose_name=_("employee type"))
    is_lead = models.BooleanField(default=False, verbose_name=_("project lead"), choices=((True, _("yes")), (False, _("no"))))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="staff_members",
                                       verbose_name=_("funding source"), default=1)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"),
                             related_name="staff_instances2")
    name = models.CharField(max_length=255, verbose_name=_("Person name (leave blank if user is selected)"), blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("level"))
    student_program = models.IntegerField(choices=student_program_choices, blank=True, null=True, verbose_name=_("student program"))
    duration_weeks = models.FloatField(default=0, blank=True, null=True, verbose_name=_("duration in weeks"))
    overtime_hours = models.FloatField(default=0, blank=True, null=True, verbose_name=_("overtime in hours"))
    overtime_description = models.TextField(blank=True, null=True, verbose_name=_("overtime description"))
    amount = models.FloatField(blank=True, null=True, verbose_name=_("amount (CAD)"))

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
    new_or_existing_choices = [
        (1, _("New")),
        (2, _("Existing")),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="agreements", verbose_name=_("project"))
    partner_organization = models.CharField(max_length=255, blank=True, null=True,
                                            verbose_name=_("collaborating organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
    new_or_existing = models.IntegerField(choices=new_or_existing_choices, verbose_name=_("new or existing"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['partner_organization', ]

    def __str__(self):
        return "{}".format(self.partner_organization)


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
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"))

    def __str__(self):
        return "{}".format(self.om_category)

    class Meta:
        ordering = ['om_category', ]


class CapitalCost(models.Model):
    category_choices = (
        (1, _("IM / IT - computers, hardware")),
        (2, _("Lab Equipment")),
        (3, _("Field Equipment")),
        (4, _("Other")),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="capital_costs",
                                verbose_name=_("project"))
    category = models.IntegerField(choices=category_choices, verbose_name=_("category"))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="capital_costs",
                                       verbose_name=_("funding source"), default=1)
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    amount = models.FloatField(default=0, verbose_name=_("amount"))

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
    amount = models.FloatField(default=0, verbose_name=_("amount"))

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
    status_report = models.ForeignKey("StatusReport", related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, verbose_name=_("external URL"))
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['project', 'status_report', 'name']

    def __str__(self):
        return self.name

    @property
    def ref(self):
        return self.status_report if self.status_report else "Core project"


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
    status_choices = (
        (1, _("On-track")),
        (2, _("Complete")),
        (3, _("Encountering issues")),
        (4, _("Aborted / cancelled")),
    )
    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE)
    status = models.IntegerField(default=1, editable=False, choices=status_choices)
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
        return [report for report in self.project.reports.order_by("date_created")].index(self) + 1

    def __str__(self):
        # what is the number of this report?
        return "{}{}".format(
            _("Status Report #"),
            self.report_number,
        )


class MilestoneUpdate(models.Model):
    status_choices = (
        (1, _("In progress")),
        (2, _("Completed")),
        (3, _("Aborted / cancelled")),
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
            _("Update on "),
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
