from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from shared_models.models import UnilingualSimpleLookup
from django.core.mail import send_mail
from django.urls import reverse


class DataSubType(UnilingualSimpleLookup):
    pass


class DataType(UnilingualSimpleLookup):
    pass


class PlanningMethodType(UnilingualSimpleLookup):
    pass


class Province(UnilingualSimpleLookup):
    pass


class Country(UnilingualSimpleLookup):
    pass


class FundingYear(UnilingualSimpleLookup):
    pass


class Role(UnilingualSimpleLookup):
    pass


class MethodDocumentType(UnilingualSimpleLookup):
    pass


class AgreementDatabase(UnilingualSimpleLookup):
    pass


class AgreementLineage(UnilingualSimpleLookup):
    pass


class OutcomeCategory(UnilingualSimpleLookup):
    pass


class ObjectiveCategory(UnilingualSimpleLookup):
    pass


class Species(UnilingualSimpleLookup):
    pass


class SampleType(UnilingualSimpleLookup):
    pass


class SalmonStage(UnilingualSimpleLookup):
    pass


class DataQualityType(UnilingualSimpleLookup):
    pass


class DataQualityLevel(UnilingualSimpleLookup):
    pass


class Location(UnilingualSimpleLookup):
    pass


class FieldWorkMethodType(UnilingualSimpleLookup):
    pass


class SampleProcessingMethodType(UnilingualSimpleLookup):
    pass


class DataEntryMethodType(UnilingualSimpleLookup):
    pass


class DataAnalysisMethodType(UnilingualSimpleLookup):
    pass


class ReportingMethodType(UnilingualSimpleLookup):
    pass


class Database(UnilingualSimpleLookup):
    pass


class ModelsUsed(UnilingualSimpleLookup):
    pass


class DataFormat(UnilingualSimpleLookup):
    pass


class DataProgram(UnilingualSimpleLookup):
    pass


class DataQuality(UnilingualSimpleLookup):
    pass


class Subject(UnilingualSimpleLookup):
    pass


class FundingSource(UnilingualSimpleLookup):
    pass


class WaterShed(UnilingualSimpleLookup):
    pass


class SMUCode(UnilingualSimpleLookup):
    pass


class SMUName(UnilingualSimpleLookup):
    pass


class CUIndex(UnilingualSimpleLookup):
    pass


class CUName(UnilingualSimpleLookup):
    pass


class ProjectType(UnilingualSimpleLookup):
    pass


class ProjectSubType(UnilingualSimpleLookup):
    pass


class ProjectClass(UnilingualSimpleLookup):
    pass


class ProjectComponent(UnilingualSimpleLookup):
    pass


class ProjectStage(UnilingualSimpleLookup):
    pass


class ProjectStrategicLink(UnilingualSimpleLookup):
    pass


class FundingAmount(UnilingualSimpleLookup):
    pass


class AgreementStatus(UnilingualSimpleLookup):
    pass


class ProjectScale(UnilingualSimpleLookup):
    pass


class MonitoringApproach(UnilingualSimpleLookup):
    pass


class ProjectTheme(UnilingualSimpleLookup):
    pass


class CoreComponent(UnilingualSimpleLookup):
    pass


class SupportComponent(UnilingualSimpleLookup):
    pass


class LinkedGovernmentOrganizations(UnilingualSimpleLookup):
    pass


class StrategicAgreementLink(UnilingualSimpleLookup):
    pass


class FNRelationshipLevel(UnilingualSimpleLookup):
    pass


class DFOLink(UnilingualSimpleLookup):
    pass


class FNCommunications(UnilingualSimpleLookup):
    pass


class ReportTimeline(UnilingualSimpleLookup):
    pass


class ReportTopicProgramLevel(UnilingualSimpleLookup):
    pass


class ReportType(UnilingualSimpleLookup):
    pass


class ReportFormatProjectLevel(UnilingualSimpleLookup):
    pass


class ReportFormatProgramLevel(UnilingualSimpleLookup):
    pass


class FisherySupportLink(UnilingualSimpleLookup):
    pass


class ReportPurpose(UnilingualSimpleLookup):
    pass


class ReportProblemAddressedContent(UnilingualSimpleLookup):
    pass


class ReportClient(UnilingualSimpleLookup):
    pass


class OrgType(models.Model):
    pass


class River(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("name"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("longitude"))

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class Region(UnilingualSimpleLookup):
    pass


class Organization(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=1000, verbose_name=_("name"))
    address = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("address"))
    organization_type = models.ForeignKey(OrgType, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("organization type"))
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("province/state"), related_name="organization_province")
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("country"), related_name="organization_country")
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("phone"))
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("city"))
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("postal code/zip"))
    email = models.EmailField(max_length=1000, blank=True, null=True, verbose_name=_("email"))
    website = models.URLField(blank=True, null=True, verbose_name=_("website"))
    section = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("section"))

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
    first_name = models.CharField(max_length=100, verbose_name=_("first name"), blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("last name"), blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("phone"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("email"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("city"))
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("province/state"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("address"))
    organizations = models.ManyToManyField(Organization, default=None, blank=True, verbose_name=_("organization"))
    role = models.ForeignKey(Role, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("role"))
    section = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("section"))
    other_membership = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("other membership"))

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
    project_core_component = models.ForeignKey(CoreComponent, on_delete=models.DO_NOTHING, blank=True, null=True,verbose_name=_("project core component"))

    #methods
    planning_method_type = models.ForeignKey(PlanningMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="planning_method", verbose_name=_("planning method type"))
    field_work_method_type = models.ForeignKey(FieldWorkMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='field_method', verbose_name=_("field work methods type/class"))
    sample_processing_method_type = models.ForeignKey(SampleProcessingMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='sample_processing_method', verbose_name=_("sample processing method type"))
    data_entry_method_type = models.ForeignKey(DataEntryMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="data_entry_method", verbose_name="data entry method type")
    data_analysis_method_type = models.ForeignKey(DataAnalysisMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="data_analysis_methods", verbose_name="data analysis method type")
    reporting_method_type = models.ForeignKey(ReportingMethodType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="reporting_methods", verbose_name="reporting method type")

    #Document
    method_document_type = models.ForeignKey(MethodDocumentType, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="document_type", verbose_name=_("method document type"))
    authors = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("author"))
    publication_year = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("year of publication"))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("title"))
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("reference number"))
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("publisher"))
    #URLFIELD?
    document_link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("document link"))
    ######

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ['project_core_element']


class Reports(models.Model):
    objects = models.Manager()
    report_timeline = models.ForeignKey(ReportTimeline, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_timeline', verbose_name=_("report timeline"))
    report_topic_program_level = models.ForeignKey(ReportTopicProgramLevel, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_topic', verbose_name=_("report topic"))
    report_type = models.ForeignKey(ReportType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_type', verbose_name=_("report typel"))
    report_format_project_level = models.ForeignKey(ReportFormatProjectLevel, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_form_project_level', verbose_name=_("report form project level"))
    report_format_program_level = models.ForeignKey(ReportFormatProjectLevel, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_form_program_level', verbose_name=_("report form program level"))
    report_purpose = models.ForeignKey(ReportPurpose, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_purpose', verbose_name=_("report purpose"))
    fishery_support_link = models.ForeignKey(FisherySupportLink, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='fishery_support_link', verbose_name=_("fishery support link"))
    report_client = models.ForeignKey(ReportClient, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_client', verbose_name=_("report client"))
    report_problem_addressed_content = models.ForeignKey(ReportProblemAddressedContent, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='report_problem_addressed_content', verbose_name=_("report problem addressed content"))
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
        ordering = ['report_topic']


class Data(models.Model):
    objects = models.Manager()
    species_data = models.ForeignKey(Species, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='species_data', verbose_name=_("species data"))

    data_type = models.ForeignKey(DataType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_type', verbose_name=_("data type"))
    data_subtype = models.ForeignKey(DataSubType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_sub_type', verbose_name=_("data subtype"))
    data_type_comment = models.TextField(max_length=1000, blank= True, null=True, verbose_name=_("data type comment"))
    data_subtype_comment = models.TextField(max_length=1000, blank= True, null=True, verbose_name=_("data sub type comment"))
    #TODO: doesnt make sense?
    sample_types_included = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("sample_types_included"))

    primary_data_contact = models.ForeignKey(Person, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='primary_data_contact', verbose_name=_("primary data contact"))
    data_format = models.ForeignKey(DataFormat, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_format',  verbose_name=_("data format"))

    database = models.ForeignKey(Database, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='database', verbose_name=_("database"))
    data_program = models.ForeignKey(DataProgram, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_program',  verbose_name=_("data program"))
    data_quality_type = models.ForeignKey(DataQualityType, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_quality_type', verbose_name=_("data quality type"))
    data_quality_level = models.ForeignKey(DataQualityLevel, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='data_quality_level', verbose_name=_("data quality level"))
    #PEOPLE
    DFO_analysts = models.ForeignKey(Person, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_analysts', verbose_name=_("Non DFO analysts"))
    Non_DFO_analysts = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("DFO analysts"))

    #META
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.database)

    class Meta:
        ordering = ['species_data']


class Feedback(models.Model):
    objects = models.Manager()
    subject = models.ForeignKey(Subject, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("subject"))
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
    work_plan_section = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("work plan section"))
    task_description = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("task description"))

    key_element = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("key element"))
    activity = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("activity"))
    element_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("element title"))
    activity_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("activity title"))

    pst_requirement = models.BooleanField(default=False, verbose_name=_("PST requirement identified?"))
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("location"))
    objective_category = models.ForeignKey(ObjectiveCategory, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='objective_category', verbose_name=_("Objective Category"))
    duration = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("duration"))

    species = models.ForeignKey(Species, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("species"))
    target_sample_num = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("target sample number"))
    sample_type = models.ForeignKey(SampleType, default=None, on_delete=models.DO_NOTHING, related_name='sample_type', blank=True, null=True, verbose_name=_("sample type/specific data item"))
    salmon_stage = models.ForeignKey(SalmonStage, default=None, on_delete=models.DO_NOTHING, related_name='salmon_stage', blank=True, null=True, verbose_name=_("salmon stage"))

    sil_requirement = models.BooleanField(default=False, verbose_name=_("SIL requirement"))
    expected_results = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("expected results"))
    dfo_report = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Products/Reports to provide dfo"))

    scientific_outcome = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("scientific outcome"))
    outcomes_category = models.ForeignKey(OutcomeCategory, default=None, on_delete=models.DO_NOTHING, null=True, blank= True, related_name='outcomes_category', verbose_name=_("outcomes category"))
    outcomes_deadline = models.DateField(blank=True, null=True, verbose_name=_("outcomes deadline"))
    outcomes_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='outcomes_contact', verbose_name=_("Outcomes Contact"))

    data_quality_type = models.ForeignKey(DataQualityType, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='data_quality_type', verbose_name=_("data quality type"))
    data_quality_level = models.ForeignKey(DataQualityLevel, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='data_quality_level', verbose_name=_("data quality level"))
    report_reference = models.ForeignKey(Reports, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='report_reference', verbose_name=_("report reference"))

    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.number)

    class Meta:
        ordering = ['number']


class Project(models.Model):

    objects = models.Manager()
    objectives = models.ForeignKey(Objective, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("project objectives"))
    methods = models.ForeignKey(Method, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("project methods"))
    reports = models.ForeignKey(Reports, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("project reports"))

    agreement_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("agreement number"))
    agreement_database = models.ForeignKey(AgreementDatabase, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='agreement_database', verbose_name=_("agreement database"))
    agreement_status = models.CharField(default=None, choices=AgreementStatus, blank=True, null=True, verbose_name=_("agreement status"))
    agreement_status_comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("agreement status comment"))

    funding_sources = models.ForeignKey(FundingSource, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='funding_sources', verbose_name=_("funding sources"))
    funding_years = models.ForeignKey(FundingYear, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='funding_years', verbose_name=_("funding year"))

    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("project name"))
    project_description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("project description"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("starting date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("end date"))

    primary_river = models.ForeignKey(River, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='primary_river', verbose_name=_("primary river"))
    secondary_river = models.ForeignKey(River, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='secondary_river', verbose_name=_("secondary river"))

    #NEED TO CREATE MODELS FOR THESE POSSIBLY
    lake_system = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_("lake system"))
    watershed = models.CharField(max_length=1000, null=True, blank=True, verbose_name=("watershed"))
    management_area = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(142)], verbose_name=_("management area"))
    region = models.ForeignKey(Region, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("region"))

    smu_name = models.ForeignKey(SMUName, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='smu_name', verbose_name=_("smu name"))
    cu_index = models.ForeignKey(CUIndex, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='cu_index', verbose_name=_("cu index"))
    cu_name = models.ForeignKey(CUName, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='cu_name', verbose_name=_("cu name"))

    species = models.ForeignKey(Species, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='target_species', verbose_name=_("target species"))
    salmon_life_cycle = models.ForeignKey(SalmonStage, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='salmon_life_cycle', verbose_name=_("salmon life cycle"))


    #Project type
    project_type = models.ForeignKey(ProjectType, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_type', verbose_name=_("project type"))
    project_sub_type = models.ForeignKey(ProjectSubType, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_sub_type', verbose_name=_("project sub type"))
    project_theme = models.ForeignKey(ProjectTheme, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_theme', verbose_name=_("project theme"))
    project_stage = models.ForeignKey(ProjectStage, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='project_stage', verbose_name=_("project stage"))
    project_scale = models.ForeignKey(ProjectScale, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_scale', verbose_name=_("project scale"))
    monitoring_approach = models.ForeignKey(MonitoringApproach, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='monitoring_approach', verbose_name=_("monitoring approach"))
    core_component = models.ForeignKey(CoreComponent, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='core_component', verbose_name=_("core component"))
    supportive_component = models.ForeignKey(SupportComponent, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='supportive_component', verbose_name=_("supportive component"))
    category_comments = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("category comments"))

    ## COULD USE A REMODEL
    DFO_link = models.ForeignKey(DFOLink, default=None, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='DFO_link', verbose_name=_("other DFO project link"))
    ## TYPED OR AGREEMENT NUMBER?
    DFO_program_reference = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("other non-DFO project link"))
    ##FILTER GOV ORG TO PICK
    government_organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='government_organization', verbose_name=_("government organization"))
    ##DO WE NEED THIS IF ABOVE HAS LINK TO IT?
    government_reference = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("government reference"))
    strategic_agreement_link = models.ForeignKey(StrategicAgreementLink, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='strategic_agreement_link', verbose_name=_("strategic agreemnent link"))

    #PEOPLE & ORGANIZATIONS
    DFO_project_authority = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_project_authority', verbose_name=_("DFO project authority"))
    DFO_aboriginal_AAA = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_aboriginal_AAA', verbose_name=_("DFO aboriginal AAA"))
    DFO_resource_manager = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_resource_manager', verbose_name=_("DFO resource manager"))
    tribal_council = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='tribal_council', verbose_name=_("tribal council"))
    primary_first_nations_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name= 'primary_first_nations_contact', verbose_name=_("primary first nations contact"))
    primary_first_nations_contact_role = models.ForeignKey(Role, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='primary_first_nations_contact_role', verbose_name=_("primary first nations contact role"))
    FN_relationship_level = models.ForeignKey(FNRelationshipLevel, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='FN_relationship_level', verbose_name=_("first nations relationship level"))
    other_first_nations_contact = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='other_first_nations_contact', verbose_name=_("other first nations contact"))
    other_first_nations_contact_role = models.ForeignKey(Role, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='other_first_nations_contact_role', verbose_name=_("other first nations contact role"))
    DFO_technicians = models.ForeignKey(Person, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='DFO_technicians', verbose_name=_("DFO technicians"))
    #ADD as many as possible
    third_party_organization = models.ManyToManyField(Organization, null=True, blank=True, related_name='third_party_organization', verbose_name=_("third party organizations"))
    primary_third_party_contact = models.ManyToManyField(Person, null=True, blank=True, related_name='primary_third_party_contact', verbose_name=_("primary third party contact"))
    others = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("other"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['agreement_number', 'name', 'region', 'primary_river', 'species', 'DFO_project_authority']


class Meetings(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("name"))
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("location"))
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("description"))
    FN_communications = models.ForeignKey(FNCommunications, default=None, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_("FN communications"))

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
    field_name = models.CharField()
    description = models.TextField()
