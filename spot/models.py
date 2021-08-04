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
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_method', verbose_name=_("agreement number"))

    #TODO need to daisy chain possibly/ DO NEED TO FIGURE OUT
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
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_report', verbose_name=_("agreement number"))
    report_timeline = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("report timeline"))
    report_type = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("report type"))
    report_concerns = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("report limitations and concerns"))
    document_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document name"))
    document_author = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document author"))
    document_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document location"))
    document_reference_information = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document reference information"))
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document link"))

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
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_data', verbose_name=_("agreement number"))
    species_data = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Species Data"))

    # SAMPLES #
    samples_collected = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("samples collected"))
    samples_collected_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("samples collected comment"))
    samples_data_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Sample Data Database"))
    shared_drive = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("If you have chosen one of the shared drives please specify what drive otherwise leave blank"))
    sample_barrier = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("barriers to sample collection"))
    sample_entered_database = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("was sample collection data entered into database(s)?"))
    data_quality_check = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("was sample data quality check complete?"))
    data_quality_person = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("person responsible for data quality check?"))
    barrier_data_check_entry = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Barriers to data checks/entry to database?"))
    sample_format = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Sample Format(s)"))

    data_products = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("data products"))
    data_products_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Data Products Database(s)"))
    data_products_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("data products comment"))
    data_programs = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("data programs"))
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
    subject = models.CharField(max_length=255, default=None, choices=choices.SUBJECT, blank=True, null=True, verbose_name=_("subject"))
    comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("comments"))
    sent_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("sent by"))

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
    project = models.ForeignKey('Project', default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_objective', verbose_name=_("agreement number"))
    task_description = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("task description"))
    element_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("element title"))
    activity_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("activity title"))

    pst_requirement = models.BooleanField(default=False, verbose_name=_("PST requirement identified?"))
    location = models.ForeignKey(River, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_objective', verbose_name=_("location"))
    objective_category = models.CharField(max_length=64, default=None, blank=True, null=True, verbose_name=_("Objective Category"))
    target_sample_number = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("target sample number"))
    species = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_("species"))
    sil_requirement = models.BooleanField(default=False, verbose_name=_("SIL requirement"))

    expected_results = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("expected results"))
    dfo_report = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Products/Reports to provide dfo"))

    outcome_deadline_met = models.BooleanField(default=False, verbose_name=_("was the outcome deadline met?"))
    outcomes_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_objective', verbose_name=_("Outcomes Contact"))
    outcomes_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("outcome comment"))
    outcome_barrier = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("barrier to achieve outcomes?"))
    capacity_building = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("what capacity building did this project provide"))
    key_lesson = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("key lessons learned"))
    missed_opportunities = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("missed opportunities"))

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
    agreement_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("agreement number"))
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("project name"))
    project_description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("project description"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("starting date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("end date"))

    primary_river = models.ForeignKey(River, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='primary_river', verbose_name=_("primary river"))
    secondary_river = models.ManyToManyField(River, blank=True, related_name='secondary_river', verbose_name=_("secondary river"))

    # NEED TO CREATE MODELS FOR THESE POSSIBLY
    ecosystem_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("eco system type"))
    lake_system = models.ManyToManyField(LakeSystem, default=None, related_name='project', blank=True, verbose_name=_("lake system"))
    watershed = models.ManyToManyField(Watershed, default=None, blank=True, related_name='proeject', verbose_name=_("watershed"))
    management_area = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(142)], verbose_name=_("management area"))
    region = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("region"))

    smu_name = models.CharField(max_length=64, default=None, blank=True, null=True, verbose_name=_("SMU name"))
    cu_index = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("CU index"))
    cu_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("CU name"))

    species = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("target species"))
    salmon_life_stage = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("Salmon Life Stage"))

    # Project type
    project_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("project type"))
    project_sub_type = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("project sub type"))
    project_theme = models.CharField(max_length=255, default=None, blank=True, verbose_name=_("project theme"))
    project_stage = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("project stage"))
    monitoring_approach = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("monitoring approach"))
    core_component = models.CharField(max_length=255, blank=True, verbose_name=_("core component"))
    supportive_component = models.CharField(max_length=255, blank=True, verbose_name=_("supportive component"))
    project_purpose = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project purpose"))
    category_comments = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("category comments"))

    # Project Links
    DFO_link = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("other DFO project link"))
    DFO_program_reference = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("other non-DFO project link"))
    government_organization = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("government organization"))
    government_reference = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("government reference"))

    # PEOPLE & ORGANIZATIONS
    DFO_project_authority = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_project_authority', verbose_name=_("DFO project authority"))
    DFO_area_chief = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_area_chief', verbose_name=_("DFO area chief"))
    DFO_aboriginal_AAA = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_aboriginal_AAA', verbose_name=_("DFO aboriginal AAA"))
    DFO_resource_manager = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_resource_manager', verbose_name=_("DFO resource manager"))
    tribal_council = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='tribal_council', verbose_name=_("tribal council"))
    primary_first_nations_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='primary_first_nations_contact', verbose_name=_("primary first nations contact"))
    primary_first_nations_contact_role = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name=_("primary first nations contact role"))
    DFO_technicians = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_technicians', verbose_name=_("DFO technicians"))

    contractor = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("contractors"))
    primary_contact_contractor = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("primary contact contractor"))
    partner = models.ManyToManyField(Organization,  blank=True, related_name='partner', verbose_name=_("partner"))
    primary_contact_partner = models.ManyToManyField(Person, blank=True, related_name='primary_contact_partner', verbose_name=_("primary contact partner"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.agreement_number)

    class Meta:
        ordering = ['agreement_number', 'name', 'region', 'primary_river', 'DFO_project_authority']


class AgreementHistory(models.Model):
    project = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='project_history', verbose_name=_("agreement number"))
    history = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Agreement History Number"))
    agreement_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("agreement database"))
    agreement_status_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("agreement status comment"))

    funding_sources = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name=_("funding sources"))
    other_funding_sources = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("If you have chosen other above please enter the source here"))
    agreement_type = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name=_("agreement type "))
    project_lead_organization = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name=_("project lead organization"))

    #TODO move to funding year
    annual_agreement_cost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Annual Agreement Cost"))
    annual_project_cost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Annual Project Cost"))

    #TODO use a loop for selection
    #funding_years = models.ForeignKey(FundingYear, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_history, verbose_name=_("funding year"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.project)

    class Meta:
        ordering = ['project']


class Meetings(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("name"))
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("location"))
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("description"))
    FN_communications = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("FN communications"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class HelpText(models.Model):
    field_name = models.CharField(max_length=255)
    help_text = models.TextField(verbose_name=_("English text"))

    def __str__(self):
        return "{}".format(self.help_text)

    class Meta:
        ordering = ['field_name', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class ObjectiveDataTypeQuality(models.Model):
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='objective_type_quality', verbose_name=_("objective"))
    sample_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("sample type/specific data item"))
    outcome_delivered = models.BooleanField(default=False, verbose_name=_("was the outcome/sample delivered?"))
    outcome_report_delivered = models.BooleanField(default=False, verbose_name=_("were outcome reports delivered?"))
    outcome_quality = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("quality of outcome"))
    report_sent_to = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("reporting sent to"))
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
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='objective_outcome', verbose_name=_("objective"))
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


class Costing(models.Model):
    agreement_database = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Agreement Database"))
    agreement_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Agreement Comment"))
    funding_sources = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Funding Sources"))
    other_funding_sources = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("If you have chosen 'Other' in funding sources above please provide them"))
    agreement_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Agreement Type'))
    project_lead_organization = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Project Lead Organization"))
    agreement_cost = models.FloatField(blank=True, null=True, verbose_name=_("Agreement Cost"))
    project_cost = models.FloatField(blank=True, null=True, verbose_name=_("Project Cost"))

    def __str__(self):
        return "{}".format(self.project_lead_organization)

    class Meta:
        ordering = ['project_lead_organization', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class FundingYears(models.Model):
    costing = models.ForeignKey(Costing, on_delete=models.CASCADE, null=True, blank=True, related_name='year_cost', verbose_name=_('costing'))
    funding_year = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Funding Year"))
    year_cost = models.FloatField(null=True, blank=True, verbose_name=_("Year Cost"))

    def __str__(self):
        return "{}".format(self.funding_year)

    class Meta:
        ordering = ['funding_year', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class MethodDocument(models.Model):
    method_document_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("method document type"))
    authors = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("author"))
    publication_year = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("year of publication"))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("title"))
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("reference number"))
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document link"))

    def __str__(self):
        return "{}".format(self.method_document_type)

    class Meta:
        ordering = ['method_document_type', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)