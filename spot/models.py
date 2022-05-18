from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shared_models.models import Region
from django.urls import reverse
from . import choices


YES_NO_CHOICES = (
        (True, "Yes"),
        (False, "No"),
    )


class SpotUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="spot_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="spot_users", on_delete=models.CASCADE, blank=True, null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)
    is_crud_user = models.BooleanField(default=False, verbose_name=_("CRUD permissions?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class UnilingualSimpleLookup(models.Model):
    class Meta:
        abstract = True
        ordering = ["name", ]

    name = models.CharField(unique=True, max_length=255, verbose_name=_("name"))

    def __str__(self):
        return self.name


class MonitoringApproach(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class EcosystemType(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class Species(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class HatcheryName(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class ManagementArea(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class SalmonLifeStage(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class ProjectSubType(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class ProjectTheme(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class CoreComponent(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class SupportiveComponent(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class ProjectPurpose(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class FundingSources(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class ObjectiveCategory(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class CapacityBuilding(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class OutComeBarrier(UnilingualSimpleLookup):
    objects =models.Manager()
    pass


class LakeSystem(UnilingualSimpleLookup):
    objects = models.Manager()
    pass


class CUName(UnilingualSimpleLookup):
    objects = models.Manager()
    pass


class CUIndex(UnilingualSimpleLookup):
    objects = models.Manager()
    pass


class FirstNations(UnilingualSimpleLookup):
    objects = models.Manager()
    pass


class Watershed(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Name"))
    group_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Group Code"))

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class River(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Name"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Longitude"))
    sub_district_area = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Area"))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, default=None, null=True, blank=True, related_name='river_species', verbose_name=_("Target Species"))
    cu_index = models.ForeignKey(CUIndex, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("CU Index"))
    cu_name = models.ForeignKey(CUName, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("CU Name"))
    stock_management_unit = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Stock Management Unit"))
    pop_id = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Stock Management Unit"))
    du = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("DU"))
    du_number = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("DU Number"))

    def __str__(self):
        return "{} - {}".format(self.name, self.species.name if self.species else None)

    class Meta:
        ordering = ['name']

    @property
    def get_lat_long(self):
        return "{lat:" + str(self.latitude) + "," + "lng:" + str(self.longitude) + "}"

    @property
    def get_name_species(self):
        return "{} {}".format(self.name, self.species.name if self.species else None)


class Organization(models.Model):
    objects = models.Manager()
    is_active = models.CharField(max_length=255, default='Yes', null=True, blank=True, verbose_name=_("Is this organization still active?"))
    name = models.CharField(unique=True, max_length=255, verbose_name=_("Name"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address"))
    organization_type = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Organization Type"))
    province_state = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Province/State"))
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
    is_active = models.CharField(max_length=255, default='Yes', null=True, blank=True, verbose_name=_("Is this person still active?"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City"))
    province_state = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Province/State"))
    country = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Country"))
    organizations = models.ManyToManyField(Organization, default=None, blank=True, verbose_name=_("Organization"))
    role = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Role"))
    section = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Section"))
    other_membership = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Other Membership"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"), related_name="spot_last_modifications")

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

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
    unique_method_number = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Unique Method Number"))
    field_work_method_type = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Field Work Methods Type"))
    planning_method_type = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Planning Method Type"))
    sample_processing_method_type = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Sample Processing Method Type"))
    knowledge_consideration = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Traditional Ecological Knowledge Consideration"))

    scale_processing_location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Scale Processing Location"))
    otolith_processing_location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Otolith Processing Location"))
    DNA_processing_location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("DNA Processing Location"))
    heads_processing_location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Heads Processing Location"))
    instrument_data_processing_location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Instrument Data Processing Location"))

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
    published = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Was this report Published?"))

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
    river = models.ForeignKey(River, on_delete=models.DO_NOTHING, default=None, blank=True, null=True, verbose_name=_("River"))
    samples_collected = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Samples Collected"))
    samples_collected_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Samples Collected Comment"))
    samples_collected_database = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Sample Collected Database"))
    shared_drive = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("If you have chosen one of the shared drives please specify what drive otherwise leave blank"))
    sample_barrier = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Barriers to Sample Collection and Data Entry?"))
    sample_entered_database = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Was sample collection data entered into database(s)?"))
    data_quality_check = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Was sample data quality check complete?"))
    sample_format = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Sample Format(s)"))
    data_products = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Data Product(s)"))
    data_products_database = models.CharField(max_length=255, null=True, default=None, blank=True, verbose_name=_("Data Products Database"))
    data_products_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Data Products Comment"))

    # META
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.project)

    class Meta:
        ordering = ['project']


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
    unique_objective = models.CharField(max_length=255, blank=True, null=True)
    task_description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Task Description"))
    element_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Element Title"))
    activity_title = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Activity Title"))

    pst_requirement = models.CharField(max_length=255, default=None,  blank=True, null=True, verbose_name=_("PST Requirement Identified?"))
    location = models.ForeignKey(River, blank=True, default=None, on_delete=models.DO_NOTHING, null=True, verbose_name=_("Location"))
    objective_category = models.ManyToManyField(ObjectiveCategory, default=None, blank=True, verbose_name=_("Objective Category"))
    sil_requirement = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("SIL Requirement"))

    expected_results = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Expected Result(s)"))
    dfo_report = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Products/Reports to Provide DFO"))

    outcomes_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_objective', verbose_name=_("Outcomes Contact"))
    outcomes_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Outcome Comment"))
    outcome_barrier = models.ManyToManyField(OutComeBarrier, default=None, blank=True, verbose_name=_("Barrier to Achieve Outcomes(?)"))
    capacity_building = models.ManyToManyField(CapacityBuilding, default=None, blank=True, verbose_name=_("What capacity building did this project provide?"))
    key_lesson = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Key Lessons Learned"))
    missed_opportunities = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Missed Opportunities"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.project)

    class Meta:
        ordering = ['project']


class Project(models.Model):

    objects = models.Manager()
    project_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Project Number"))
    agreement_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Agreement Number"))
    agreement_history = models.ManyToManyField('Project', blank=True, verbose_name=_("Agreement History"))
    name = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Project Name"))
    project_description = models.TextField(max_length=5000, null=True, blank=True, verbose_name=_("Project Description"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Starting Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))

    river = models.ManyToManyField(River, blank=True, related_name='river', verbose_name=_("River(s)"))
    other_species = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Are there any other species to add?"))
    ecosystem_type = models.ManyToManyField(EcosystemType, default=None, blank=True, verbose_name=_("Eco System Type"))
    lake_system = models.ManyToManyField(LakeSystem, default=None, related_name='project', blank=True, verbose_name=_("Lake System"))
    watershed = models.ManyToManyField(Watershed, default=None, blank=True, related_name='proeject', verbose_name=_("Watershed"))
    management_area = models.ManyToManyField(ManagementArea, blank=True, verbose_name=_("Pacific Region Management Area"))
    area = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Area"))
    salmon_life_stage = models.ManyToManyField(SalmonLifeStage, default=None, blank=True, verbose_name=_("Salmon Life Stage"))
    aquaculture_license_number = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Aquaculture License Number"))
    water_license_number = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Water License Number"))
    hatchery_name = models.ManyToManyField(HatcheryName, default=None, blank=True, verbose_name=_("Hatchery Name"))
    DFO_tenure = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("DFO Tenure"))
    # Project type
    project_type = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Project Type"))
    project_sub_type = models.ManyToManyField(ProjectSubType, default=None, blank=True, verbose_name=_("Project Sub Type"))
    project_theme = models.ManyToManyField(ProjectTheme, default=None, blank=True, verbose_name=_("Project Theme"))
    project_stage = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Project Stage"))
    monitoring_approach = models.ManyToManyField(MonitoringApproach, blank=True, verbose_name=_("Monitoring Approach"))
    core_component = models.ManyToManyField(CoreComponent, blank=True, verbose_name=_("Core Component"))
    supportive_component = models.ManyToManyField(SupportiveComponent, blank=True, verbose_name=_("Supportive Component"))
    project_purpose = models.ManyToManyField(ProjectPurpose, blank=True, verbose_name=_("Project Purpose"))
    category_comments = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Category Comments"))

    # Project Links
    DFO_link = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Link to other DFO Programs"))
    DFO_program_reference = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Linked DFO Program Project Reference"))
    government_organization = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Link to other Government Departments"))
    policy_program_connection = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Policy and Program Connection"))


    # PEOPLE & ORGANIZATIONS
    DFO_project_authority = models.ManyToManyField(Person, blank=True, related_name='DFO_project_authority', verbose_name=_("DFO Project Authority"))
    DFO_area_chief = models.ManyToManyField(Person, blank=True, related_name='DFO_area_chief', verbose_name=_("DFO Area Chief"))
    DFO_AAA = models.ManyToManyField(Person, blank=True, related_name='DFO_aboriginal_AAA', verbose_name=_("DFO Aboriginal Affairs Advisor"))
    DFO_resource_manager = models.ManyToManyField(Person, blank=True, related_name='DFO_resource_manager', verbose_name=_("DFO Resource Manager"))
    funding_recipient = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Funding Recipient"))
    first_nation = models.ForeignKey(FirstNations, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='tribal_council', verbose_name=_("First Nation/Tribal Council"))
    contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='first_nations_contact', verbose_name=_("Contact"))
    contact_role = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Contact Role"))
    DFO_technicians = models.ManyToManyField(Person, blank=True, related_name='DFO_technicians', verbose_name=_("DFO Technicians/Biologists"))
    contractor = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Contractors"))
    contractor_contact = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Contractor Contact"))
    partner = models.ManyToManyField(Organization,  blank=True, related_name='partner', verbose_name=_("Partner"))
    partner_contact = models.ManyToManyField(Person, blank=True, related_name='partner_contact', verbose_name=_("Partner Contact"))

    # Costing
    agreement_database = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Agreement Database"))
    agreement_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Agreement Comment"))
    funding_sources = models.ManyToManyField(FundingSources, blank=True, verbose_name=_("Funding Sources"))
    other_funding_sources = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("If you have chosen 'Other' in funding sources above please provide them"))
    agreement_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Agreement Type'))
    lead_organization = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Project Lead Organization"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.agreement_number)

    class Meta:
        ordering = ['agreement_number', 'name', 'area',]


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


class SampleOutcome(models.Model):
    objects = models.Manager()
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='sample_outcome', verbose_name=_("Objective"))
    unique_objective_number = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Unique Objective Number"))
    sampling_outcome = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Sampling Outcome"))
    outcome_delivered = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Was the Sampling Outcome Met?"))
    outcome_quality = models.CharField(max_length=255, default=None, blank=True, null=True, verbose_name=_("Quality of Outcome"))
    sample_outcome_comment = models.TextField(max_length=5000, default=None, blank=True, null=True, verbose_name=_("Sample Outcome Comment"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.sampling_outcome)

    class Meta:
        ordering = ['sampling_outcome', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class ReportOutcome(models.Model):
    objects = models.Manager()
    objective = models.ForeignKey(Objective, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='report_outcome', verbose_name=_("Objective"))
    unique_objective_number = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Unique Objective Number"))
    reporting_outcome = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Reporting Outcome"))
    outcome_delivered = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Was the outcome deliverable met?"))
    report_link = models.ForeignKey(Reports, on_delete=models.DO_NOTHING, default=None, blank=True, null=True, verbose_name=_("Report Link"))
    report_outcome_comment = models.TextField(max_length=5000, default=None, null=True, blank=True, verbose_name=_("Reporting Outcome Comment"))
    reporting_outcome_metric = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Reporting Outcome Metric"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.reporting_outcome)

    class Meta:
        ordering = ['reporting_outcome', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class FundingYears(models.Model):
    objects = models.Manager()
    project = models.ForeignKey(Project, default=None, on_delete=models.CASCADE, null=True, blank=True, related_name='funding_year', verbose_name=_("project"))
    funding_year = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Funding Year"))
    agreement_cost = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Annual Agreement Cost"))
    project_cost = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Annual Project Cost"))
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
    objects = models.Manager()
    method = models.ForeignKey(Method, on_delete=models.CASCADE, null=True, blank=True, related_name='method_document', verbose_name=_("method"))
    unique_method_number = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Unique Method Number"))
    method_document_type = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Method Document Type"))
    authors = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Author"))
    publication_year = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Year of Publication"))
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Title"))
    reference_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Reference Number"))
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Link"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return "{}".format(self.method_document_type)

    class Meta:
        ordering = ['method_document_type', ]

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class ProjectCertified(models.Model):
    objects = models.Manager()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, related_name="project_certification", verbose_name=_("Project"))
    certified_date = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    certified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)