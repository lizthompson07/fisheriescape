from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from shared_models.models import UnilingualSimpleLookup
# from django.core.mail import send_mail
from django.urls import reverse
from . import choices


class LakeSystem(UnilingualSimpleLookup):
    pass


class Watershed(UnilingualSimpleLookup):
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Name"))
    group_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Group Code"))

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class River(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Name"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Longitude"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class Organization(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=1000, verbose_name=_("Name"))
    address = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Address"))
    organization_type = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Organization Type"))
    province = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Province/State"))
    country = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Country"))
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Phone"))
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("City"))
    email = models.EmailField(max_length=1000, blank=True, null=True, verbose_name=_("Email"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    section = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Section"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"), related_name="organization_last_modified_by")

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('org_detail', kwargs={'pk': self.pk})


class Person(models.Model):
    objects = models.Manager()
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City"))
    province = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Province/State"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address"))
    organizations = models.ManyToManyField(Organization, default=None, blank=True, verbose_name=_("Organization"))
    role = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Role"))
    section = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Section"))
    other_membership = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Other Membership"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('person_detail', kwargs={'pk': self.pk})

    @property
    def display_name(self):
        my_str = "{}".format(self)
        return my_str

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def contact_card_no_name(self):
        my_str = ""
        if self.phone:
            my_str += "<br>{}: {}".format(_("Phone 1"), self.phone)
        if self.email:
            my_str += "<br>{}: {}".format(_("E-mail 1"), self.email)
        return my_str

    @property
    def contact_card(self):
        my_str = "<b>{first} {last}</b>".format(first=self.first_name, last=self.last_name)
        if self.phone:
            my_str += "<br>{}: {}".format(_("Phone 1"), self.phone)
        if self.email:
            my_str += "<br>{}: {}".format(_("E-mail 1"), self.email)

        return my_str


class Method(models.Model):
    objects = models.Manager()
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_method', verbose_name=_("Agreement Number"))

    field_work_method_type = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Field Work Methods Type"))
    planning_method_type = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Planning Method Type"))
    sample_processing_method_type = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Sample Processing Method Type"))
    data_entry_method_type = models.CharField(max_length=255, default=None, blank=True, verbose_name="Data Entry Method Type")

    scale_processing_location = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_method_scale', verbose_name=_("Scale Processing Location"))
    otolith_processing_location = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_method_otolith', verbose_name=_("Otolith Processing Location"))
    DNA_processing_location = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_method_DNA', verbose_name=_("DNA Processing Location"))
    heads_processing_location = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_method_heads', verbose_name=_("Heads Processing Location"))
    instrument_data_processing_location = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_method_instrument', verbose_name=_("Instrument Data Processing Location"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.project)

    class Meta:
        ordering = ['project']


class Reports(models.Model):
    objects = models.Manager()
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_report', verbose_name=_("Agreement Number"))
    report_timeline = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Report Timeline"))
    report_type = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Report Type"))
    report_concerns = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Report Limitations and Concerns"))
    document_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Name"))
    document_author = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Author"))
    document_reference_information = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Reference Information"))
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Link"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.document_name)

    class Meta:
        ordering = ['document_name']


class Data(models.Model):
    objects = models.Manager()
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_data', verbose_name=_("Agreement Number"))
    species_data = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Species Data"))

    # SAMPLES #
    samples_collected = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Samples Collected"))
    samples_collected_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Samples Collected Comment"))
    samples_data_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Sample Data Database"))
    shared_drive = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("If you have chosen one of the shared drives please specify what drive otherwise leave blank"))
    sample_barrier = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Barriers to Sample Collection"))
    sample_entered_database = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("Was sample collection data entered into database(s)?"))
    data_quality_check = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("Was sample data quality check complete?"))
    data_quality_person = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Person responsible for data quality check?"))
    barrier_data_check_entry = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Barriers to data checks/entry to database?"))
    sample_format = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Sample Format(s)"))

    data_products = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Data Product(s)"))
    data_products_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Data Products Database(s)"))
    data_products_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Data Products Comment"))
    data_programs = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Data Program(s)"))
    data_communication = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("How Was Data Communicated to Recipient?"))

    # META
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.species_data)

    class Meta:
        ordering = ['species_data']


class Feedback(models.Model):
    objects = models.Manager()
    subject = models.CharField(max_length=255, default=None, choices=choices.SUBJECT, blank=True, null=True, verbose_name=_("Subject"))
    comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Comments"))
    sent_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("Sent By"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.sent_by)

    class Meta:
        ordering = ['subject']


class Objective(models.Model):
    objects = models.Manager()
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_objective', verbose_name=_("Agreement Number"))
    task_description = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Task Description"))
    element_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Element Title"))
    activity_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Activity Title"))

    pst_requirement = models.BooleanField(default=False, verbose_name=_("PST Requirement Identified?"))
    location = models.ForeignKey(River, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_objective', verbose_name=_("Location"))
    objective_category = models.CharField(max_length=64, default=None, blank=True, null=True, verbose_name=_("Objective Category"))
    species = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_("Species"))
    sil_requirement = models.BooleanField(default=False, verbose_name=_("SIL Requirement"))

    expected_results = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Expected Result(s)"))
    dfo_report = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Products/Reports to Provide DFO"))

    outcome_met = models.BooleanField(default=False, verbose_name=_("Was the outcome met?"))
    outcomes_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_objective', verbose_name=_("Outcomes Contact"))
    outcomes_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Outcome Comment"))
    outcome_barrier = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Barrier to Achieve Outcomes(?)"))
    capacity_building = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("What capacity building did this project provide?"))
    key_lesson = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Key Lessons Learned"))
    missed_opportunities = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Missed Opportunities"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.location)

    class Meta:
        ordering = ['location']


class Project(models.Model):

    objects = models.Manager()
    agreement_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Agreement Number"))
    agreement_history = models.ManyToManyField('Project', default=None, null=True, blank=True, verbose_name=_("Agreement History"))
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Project Name"))
    project_description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Project Description"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Starting Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))

    primary_river = models.ForeignKey(River, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='primary_river', verbose_name=_("Primary River"))
    secondary_river = models.ManyToManyField(River, blank=True, related_name='secondary_river', verbose_name=_("Secondary River"))
    ecosystem_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Eco System Type"))
    lake_system = models.ManyToManyField(LakeSystem, default=None, related_name='project', blank=True, verbose_name=_("Lake System"))
    watershed = models.ManyToManyField(Watershed, default=None, blank=True, related_name='proeject', verbose_name=_("Watershed"))
    management_area = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(142)], verbose_name=_("Management Area"))
    region = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Region"))

    smu_name = models.CharField(max_length=64, default=None, blank=True, null=True, verbose_name=_("SMU Name"))
    cu_index = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("CU Index"))
    cu_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("CU Name"))
    species = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Target Species"))
    salmon_life_stage = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Salmon Life Stage"))

    # Project type
    project_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Project Type"))
    project_sub_type = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Project Sub Type"))
    project_theme = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Project Theme"))
    project_stage = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Project Stage"))
    monitoring_approach = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Monitoring Approach"))
    core_component = models.CharField(max_length=255, blank=True, verbose_name=_("Core Component"))
    supportive_component = models.CharField(max_length=255, blank=True, verbose_name=_("Supportive Component"))
    project_purpose = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Project Purpose"))
    category_comments = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Category Comments"))

    # Project Links
    DFO_link = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Other DFO Project Link"))
    DFO_program_reference = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Other Non-DFO Project Link"))
    government_organization = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Government Organization"))
    government_reference = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Government Reference"))

    # PEOPLE & ORGANIZATIONS
    DFO_project_authority = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_project_authority', verbose_name=_("DFO Project Authority"))
    DFO_area_chief = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_area_chief', verbose_name=_("DFO Area Chief"))
    DFO_aboriginal_AAA = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_aboriginal_AAA', verbose_name=_("DFO Aboriginal AAA"))
    DFO_resource_manager = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_resource_manager', verbose_name=_("DFO Resource Manager"))
    tribal_council = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='tribal_council', verbose_name=_("Tribal Council"))
    primary_first_nations_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='primary_first_nations_contact', verbose_name=_("Primary First Nations Contact"))
    primary_first_nations_contact_role = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name=_("Primary First Nations Contact Role"))
    DFO_technicians = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_technicians', verbose_name=_("DFO Technicians"))
    contractor = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Contractors"))
    primary_contact_contractor = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Primary Contact Contractor"))
    partner = models.ManyToManyField(Organization,  blank=True, related_name='partner', verbose_name=_("Partner"))
    primary_contact_partner = models.ManyToManyField(Person, blank=True, related_name='primary_contact_partner', verbose_name=_("Primary Contact Partner"))

    # Costing
    agreement_database = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Agreement Database"))
    agreement_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Agreement Comment"))
    funding_sources = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Funding Sources"))
    other_funding_sources = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("If you have chosen 'Other' in funding sources above please provide them"))
    agreement_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Agreement Type'))
    project_lead_organization = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Project Lead Organization"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.agreement_number)

    class Meta:
        ordering = ['agreement_number', 'name', 'region', 'primary_river', 'DFO_project_authority']


class Meetings(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Name"))
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Location"))
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Description"))
    FN_communications = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("FN Communications"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class ObjectiveDataTypeQuality(models.Model):
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='objective_type_quality', verbose_name=_("Objective"))
    species = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Species"))
    location = models.ForeignKey(River, on_delete=models.DO_NOTHING, default=None, null=True, blank=True, verbose_name=_("Location"))
    sample_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Sample Type"))
    outcome_delivered = models.BooleanField(default=False, verbose_name=_("Was the outcome/sample delivered?"))
    outcome_report_delivered = models.BooleanField(default=False, verbose_name=_("Were outcome reports delivered?"))
    outcome_quality = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Quality of Outcome"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.sample_type)

    class Meta:
        ordering = ['sample_type', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class ObjectiveOutcome(models.Model):
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='objective_outcome', verbose_name=_("Objective"))
    outcome_category = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("outcomes category"))
    report_reference = models.ForeignKey(Reports, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='objective_outcome', verbose_name=_("report reference"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.report_reference)

    class Meta:
        ordering = ['report_reference', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class FundingYears(models.Model):
    project = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='funding_year', verbose_name=_("project"))
    funding_year = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Funding Year"))
    agreement_cost = models.FloatField(blank=True, null=True, verbose_name=_("Agreement Cost"))
    project_cost = models.FloatField(blank=True, null=True, verbose_name=_("Project Cost"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.funding_year)

    class Meta:
        ordering = ['funding_year', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class MethodDocument(models.Model):
    method = models.ForeignKey(Method, on_delete=models.CASCADE, null=True, blank=True, related_name='method_document', verbose_name=_("method"))
    method_document_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("method document type"))
    authors = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("author"))
    publication_year = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("year of publication"))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("title"))
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("reference number"))
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document link"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.method_document_type)

    class Meta:
        ordering = ['method_document_type', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)
