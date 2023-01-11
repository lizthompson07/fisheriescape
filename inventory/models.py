import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import default_if_none, slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from markdown import markdown

from dm_apps import custom_widgets
from lib.functions.custom_functions import truncate, fiscal_year
from shared_models import models as shared_models
# Choices for language
from shared_models.models import SimpleLookup, Region, MetadataFields

LANGUAGE_CHOICES = ((1, 'English'), (2, 'French'),)
YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="inventory_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="inventory_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class Location(models.Model):
    # Choices for surface_type
    CAN = 'Canada'
    US = 'United States'
    COUNTRY_CHOICES = (
        (CAN, 'Canada'),
        (US, 'United States'),
    )
    location_eng = models.CharField(max_length=1000, blank=True, null=True)
    location_fre = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=25, choices=COUNTRY_CHOICES)
    country_fr = models.CharField(max_length=25)
    abbrev_eng = models.CharField(max_length=25, blank=True, null=True)
    abbrev_fre = models.CharField(max_length=25, blank=True, null=True)
    uuid_gcmd = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.location_eng)


class Organization(models.Model):
    name_eng = models.CharField(max_length=1000, blank=True, null=True)
    name_fre = models.CharField(max_length=1000, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=7, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.name_eng, self.city) if self.city else "{}".format(self.name_eng)

    class Meta:
        ordering = ['name_eng']


class PersonRole(models.Model):
    role = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.role

    class Meta:
        ordering = ['id']


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="person")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    position_eng = models.CharField(max_length=255, blank=True, null=True)
    position_fre = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    language = models.IntegerField(choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name=_("language preference"))
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def save(self, *args, **kwargs):
        self.full_name = "{} {}".format(self.user.first_name, self.user.last_name)

        super().save(*args, **kwargs)


class Status(models.Model):
    label = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.label

        # return "{}  ({})".format(self.label, self.notes) if self.notes else "{}".format(self.label)


class SpatialRepresentationType(models.Model):
    label = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.label


class SpatialReferenceSystem(models.Model):
    label = models.CharField(max_length=255)
    code = models.CharField(max_length=25, blank=True, null=True)
    codespace = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.label


class SecurityClassification(models.Model):
    label = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return self.label


class ResourceType(models.Model):
    label = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'inventory_resource_type'


class Maintenance(models.Model):
    frequency = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.frequency


class CharacterSet(models.Model):
    label = models.CharField(max_length=25)
    code = models.CharField(max_length=25, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.label


class KeywordDomain(models.Model):
    name_eng = models.CharField(max_length=255, blank=True, null=True)
    name_fre = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    web_services = models.BooleanField()
    xml_block = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name_eng


class Keyword(models.Model):
    text_value_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Keyword value (English)")
    text_value_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Keyword value (French)")
    uid = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Unique Identifier")
    concept_scheme = models.CharField(max_length=1000, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    keyword_domain = models.ForeignKey(KeywordDomain, on_delete=models.DO_NOTHING, blank=True, null=True)
    xml_block = models.TextField(blank=True, null=True)
    is_taxonomic = models.BooleanField(default=False)

    @property
    def tname(self):
        # check to see if a french value is given
        if getattr(self, str(_("text_value_eng"))):
            my_str = "{}".format(getattr(self, str(_("text_value_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.text_value_eng
        return my_str

    def __str__(self):
        return self.tname

    class Meta:
        ordering = ["keyword_domain", "text_value_eng"]

    def save(self, *args, **kwargs):
        if self.keyword_domain.id == 2 or self.keyword_domain.id == 5:
            self.is_taxonomic = True
        super().save(*args, **kwargs)

    @property
    def non_hierarchical_name_en(self):
        # if the keyword can be split by " > " then take the last item in the list
        if len(self.text_value_eng.split(" > ")) > 1:
            return self.text_value_eng.split(" > ")[-1]
        else:
            return self.text_value_eng

    @property
    def non_hierarchical_name_fr(self):
        # if the keyword can be split by " > " then take the last item in the list
        if self.text_value_fre and len(self.text_value_fre.split(" > ")) > 1:
            return self.text_value_fre.split(" > ")[-1]
        else:
            return self.text_value_fre


class DistributionFormat(SimpleLookup):
    pass


class Resource(models.Model):
    uuid = models.UUIDField(blank=True, null=True, verbose_name="UUID", unique=True)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.DO_NOTHING, blank=True, null=True)
    # section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="resources")
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="resources")
    title_eng = custom_widgets.OracleTextField(verbose_name="Title (English)")
    title_fre = custom_widgets.OracleTextField(blank=True, null=True, verbose_name="Title (French)")
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, blank=True, null=True)
    maintenance = models.ForeignKey(Maintenance, on_delete=models.DO_NOTHING, blank=True, null=True,
                                    verbose_name="Maintenance frequency")
    purpose_eng = custom_widgets.OracleTextField(blank=True, null=True, verbose_name="Purpose (English)")
    purpose_fre = custom_widgets.OracleTextField(blank=True, null=True, verbose_name="Purpose (French)")
    descr_eng = custom_widgets.OracleTextField(blank=True, null=True, verbose_name="Description (English)")
    descr_fre = custom_widgets.OracleTextField(blank=True, null=True, verbose_name="Description (French)")
    time_start_day = models.IntegerField(blank=True, null=True, verbose_name="Start day")
    time_start_month = models.IntegerField(blank=True, null=True, verbose_name="Start month")
    time_start_year = models.IntegerField(blank=True, null=True, verbose_name="Start year")
    time_end_day = models.IntegerField(blank=True, null=True, verbose_name="End day")
    time_end_month = models.IntegerField(blank=True, null=True, verbose_name="End month")
    time_end_year = models.IntegerField(blank=True, null=True, verbose_name="End year")
    sampling_method_eng = models.TextField(blank=True, null=True, verbose_name="Sampling method (English)")
    sampling_method_fre = models.TextField(blank=True, null=True, verbose_name="Sampling method (French)")
    physical_sample_descr_eng = models.TextField(blank=True, null=True,
                                                 verbose_name="Description of physical samples (English)")
    physical_sample_descr_fre = models.TextField(blank=True, null=True,
                                                 verbose_name="Description of physical samples (French)")
    resource_constraint_eng = models.TextField(blank=True, null=True, verbose_name="Resource constraint (English)")
    resource_constraint_fre = models.TextField(blank=True, null=True, verbose_name="Resource constraint (French)")
    qc_process_descr_eng = models.TextField(blank=True, null=True, verbose_name="QC process description (English)")
    qc_process_descr_fre = models.TextField(blank=True, null=True, verbose_name="QC process description (French)")
    security_use_limitation_eng = models.CharField(max_length=255, blank=True, null=True,
                                                   verbose_name="Security use limitation (English)")
    security_use_limitation_fre = models.CharField(max_length=255, blank=True, null=True,
                                                   verbose_name="Security use limitation (French)")
    security_classification = models.ForeignKey(SecurityClassification, on_delete=models.DO_NOTHING, blank=True,
                                                null=True)
    storage_envr_notes = models.TextField(blank=True, null=True, verbose_name="Storage notes (internal)")
    distribution_formats = models.ManyToManyField(DistributionFormat, blank=True)
    data_char_set = models.ForeignKey(CharacterSet, on_delete=models.DO_NOTHING, blank=True, null=True,
                                      verbose_name="Data character set")
    spat_representation = models.ForeignKey(SpatialRepresentationType, on_delete=models.DO_NOTHING, blank=True,
                                            null=True, verbose_name="Spatial representation type")
    spat_ref_system = models.ForeignKey(SpatialReferenceSystem, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name="Spatial reference system")
    geo_descr_eng = models.CharField(max_length=1000, blank=True, null=True,
                                     verbose_name="Geographic description (English)")
    geo_descr_fre = models.CharField(max_length=1000, blank=True, null=True,
                                     verbose_name="Geographic description (French)")
    west_bounding = models.FloatField(blank=True, null=True, verbose_name="West bounding coordinate")
    south_bounding = models.FloatField(blank=True, null=True, verbose_name="South bounding coordinate")
    east_bounding = models.FloatField(blank=True, null=True, verbose_name="East bounding coordinate")
    north_bounding = models.FloatField(blank=True, null=True, verbose_name="North bounding coordinate")
    parameters_collected_eng = models.TextField(blank=True, null=True, verbose_name="Parameters collected (English)")
    parameters_collected_fre = models.TextField(blank=True, null=True, verbose_name="Parameters collected (French)")
    additional_credit = models.TextField(blank=True, null=True)
    analytic_software = models.TextField(blank=True, null=True, verbose_name="Analytic software notes")
    date_verified = models.DateTimeField(blank=True, null=True)

    fgp_url = models.URLField(blank=True, null=True, verbose_name="Link to record on FGP")
    public_url = models.URLField(blank=True, null=True, verbose_name="Link to record on Open Gov't Portal")
    thumbnail_url = models.URLField(blank=True, null=True, verbose_name="Public URL to thumbnail image")
    fgp_publication_date = models.DateTimeField(blank=True, null=True, verbose_name="Date published to FGP")
    od_publication_date = models.DateTimeField(blank=True, null=True, verbose_name="Date published to Open Gov't Portal")
    od_release_date = models.DateTimeField(blank=True, null=True, verbose_name="Date released to Open Gov't Portal")
    odi_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("ODIP Identifier"), unique=True)

    last_revision_date = models.DateTimeField(blank=True, null=True, verbose_name="Date of last published revision")
    open_data_notes = models.TextField(blank=True, null=True,
                                       verbose_name="Open data notes")
    notes = models.TextField(blank=True, null=True, verbose_name="General notes (internal)")
    citations2 = models.ManyToManyField(shared_models.Citation, related_name='resources', blank=True)
    keywords = models.ManyToManyField(Keyword, related_name='resources', blank=True)
    people = models.ManyToManyField(Person, through='ResourcePerson')
    paa_items = models.ManyToManyField(shared_models.PAAItem, blank=True, verbose_name=_("Program Alignment Architecture (PAA) references"))
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True, related_name='children',
                               verbose_name="Parent resource")

    date_last_modified = models.DateTimeField(auto_now=True, editable=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    flagged_4_deletion = models.BooleanField(default=False)
    flagged_4_publication = models.BooleanField(default=False, verbose_name=_("Flagged for Publication"))
    completedness_report = models.TextField(blank=True, null=True, verbose_name=_("completedness report"))
    completedness_rating = models.FloatField(blank=True, null=True, verbose_name=_("completedness rating"))
    translation_needed = models.BooleanField(default=True, verbose_name=_("translation needed"))
    publication_fy = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False,
                                       verbose_name=_("FY of latest publication"))

    def get_absolute_url(self):
        return reverse('inventory:resource_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return "({}) {}".format(self.id, getattr(self, str(_("title_eng"))))

    @property
    def t_title(self):
        return "{}".format(getattr(self, str(_("title_eng"))))

    @property
    def last_certification(self):
        return self.certification_history.first()

    @property
    def last_publication(self):
        if self.fgp_publication_date:
            my_date = self.last_revision_date if self.last_revision_date else self.fgp_publication_date
            return my_date.strftime("%Y-%m-%d")

    def truncated_title(self):
        if self.title_eng:
            my_str = truncate(self.title_eng, 50)
        else:
            my_str = "no title"

        return my_str

    @property
    def time_period(self):
        return mark_safe(f"FROM: {default_if_none(self.time_start_year, '--')} / {default_if_none(self.time_start_month, '--')} / "
                         f"{default_if_none(self.time_start_day, '--')}<br>TO: {default_if_none(self.time_end_year, '--')} / "
                         f"{default_if_none(self.time_end_month, '--')} / {default_if_none(self.time_end_day, '--')}")

    def save(self, *args, **kwargs):
        if self.uuid is None:
            self.uuid = uuid.uuid1()

        if self.fgp_publication_date:
            # if there is a revision date, use this, otherwise use fgp pub date
            pub_date = self.last_revision_date if self.last_revision_date else self.fgp_publication_date
            fy = shared_models.FiscalYear.objects.get(pk=fiscal_year(date=pub_date, sap_style=True))
            self.publication_fy = fy

        # will handle this through the resource form. If not, each time the record is verified, this field will be updated
        # self.date_last_modified = timezone.now()
        super().save(*args, **kwargs)

    @property
    def thumbnail(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        else:
            for file in self.files.all():
                if "thumbnail" in file.caption.lower() or "vignette" in file.caption.lower():
                    return file.file.url

    @property
    def bounds(self):
        if self.east_bounding and self.west_bounding and self.south_bounding and self.north_bounding:
            return [
                (self.east_bounding, self.north_bounding),
                (self.west_bounding, self.north_bounding),
                (self.west_bounding, self.south_bounding),
                (self.east_bounding, self.south_bounding),
            ]


class ContentType(models.Model):
    title = models.CharField(max_length=255, verbose_name="Name (English)")
    english_value = models.CharField(max_length=255, verbose_name="Name (French)")
    french_value = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ["title", ]


class DataResource(models.Model):
    # choices for protocol
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    FTP = "FTP"
    PROTOCOL_CHOICES = [
        (HTTP, HTTP),
        (HTTPS, HTTPS),
        (FTP, FTP),
    ]
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="data_resources", editable=False)
    url = models.URLField()
    name_eng = models.CharField(max_length=255, verbose_name="Name (English)")
    name_fre = models.CharField(max_length=255, verbose_name="Name (French)")
    protocol = models.CharField(max_length=255, choices=PROTOCOL_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.content_type, self.name_eng)


class WebService(models.Model):
    # choices for service_language
    ENG = "urn:xml:lang:eng-CAN"
    FRA = "urn:xml:lang:fra-CAN"
    SERVICE_LANGUAGE_CHOICES = [
        (ENG, "English"),
        (FRA, "French"),
    ]
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="web_services", editable=False)
    protocol = models.CharField(max_length=255, default="ESRI REST: Map Service")
    service_language = models.CharField(max_length=255, choices=SERVICE_LANGUAGE_CHOICES)
    url = models.URLField()
    name_eng = models.CharField(max_length=255, verbose_name="Name (English)")
    name_fre = models.CharField(max_length=255, verbose_name="Name (French)")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.content_type, self.name_eng)


class ResourcePerson(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_people")
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="resource_people")
    role = models.ForeignKey(PersonRole, on_delete=models.DO_NOTHING)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('resource', 'person', 'role'),)
        db_table = 'inventory_resource_people'
        ordering = ['role']

    def get_absolute_url(self):
        return reverse('inventory:resource_detail', kwargs={'pk': self.resource.id})

    def __str__(self):
        return f"{self.person} ({self.role})"


class BoundingBox(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    west_bounding = models.FloatField(blank=True, null=True)
    south_bounding = models.FloatField(blank=True, null=True)
    east_bounding = models.FloatField(blank=True, null=True)
    north_bounding = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name


class ResourceCertification(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="certification_history", editable=False)
    certifying_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, editable=False)
    certification_date = models.DateTimeField(auto_now_add=True, verbose_name="Date published to FGP", editable=False)
    notes = models.TextField(blank=False, null=True)

    class Meta:
        ordering = ['-certification_date']
        db_table = 'inventory_resource_certification'


class Correspondence(models.Model):
    custodian = models.ForeignKey(User, on_delete=models.CASCADE, related_name="correspondences")
    subject = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True, default=timezone.now)

    class Meta:
        ordering = ['-date']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     Person.profile.save()


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'inventory/resource_{0}/{1}'.format(instance.resource.id, filename)


class File(models.Model):
    caption = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource, related_name="files", on_delete=models.CASCADE, editable=False)
    file = models.FileField(upload_to=file_directory_path)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.caption


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


class StorageSolution(SimpleLookup):
    pass


class DMA(MetadataFields):
    status_choices = (
        (0, _("Unevaluated")),
        (1, _("On-track")),
        (2, _("Complete")),
        (3, _("Encountering issues")),
        (4, _("Aborted / cancelled")),
        (5, _("Pending new evaluation")),
    )
    frequency_choices = (
        (1, _("Daily")),
        (2, _("Weekly")),
        (3, _("Monthly")),
        (4, _("Annually")),
        (5, _("Irregular / as needed")),
        (9, _("Other")),
    )
    status = models.IntegerField(default=3, editable=False, choices=status_choices)

    # Identification

    # todo make me non nullable
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, blank=False, related_name="dmas")

    title = models.CharField(max_length=1000, verbose_name=_("Title"), help_text=_("What is the title of the Data Management Agreement?"))
    data_contact = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="data_contact_for_dmas", blank=True, null=True,
                                     verbose_name=_("Who is the primary steward of this data?"),
                                     help_text=_("i.e., who is the primary responsible party?"))
    data_contact_text = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("other data contacts"))

    # Metadata
    metadata_contact = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="metadata_contact_for_dmas", blank=True, null=True,
                                         verbose_name=_("Who is primary person responsible for creating and maintaining the metadata?"),
                                         help_text=_("i.e., who is responsible for keeping metadata records up-to-date?"))
    metadata_contact_text = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("other metadata contacts"))

    resource = models.OneToOneField(Resource, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='dma',
                                    verbose_name="DM Apps Data Inventory record", help_text=_("Does this agreement relate to a dmapps data inventory record?"))

    metadata_tool = models.TextField(blank=True, null=True, verbose_name=_("Describe the tools or processes that will be used to create metadata"),
                                     help_text=_(
                                         "e.g., Metadata Inventory app in DM Apps, DFO Enterprise Data Hub, Federal Geospatial Portal, stand-alone file, ..."))
    metadata_url = models.CharField(blank=True, null=True, max_length=1000, verbose_name=_("Please provide any URLs to the metadata"),
                                    help_text=_("Full link to any metadata records available online, if applicable"))
    metadata_update_freq = models.IntegerField(blank=True, null=True, verbose_name=_("At what frequency should the metadata be updated? "),
                                               help_text=_("What should be the expectation for how often the metadata is updated?"), choices=frequency_choices)
    metadata_freq_text = models.TextField(blank=True, null=True, verbose_name=_("Justification for frequency:"),
                                          help_text=_("What justification can be provided for the above selection?"))

    # Archiving / Storage
    storage_solutions = models.ManyToManyField(StorageSolution, blank=True, verbose_name=_(
        "Which storage solution(s) will be used to house the raw field data, processed data, and all other data products?"))
    storage_solution_text = models.TextField(blank=True, null=True, verbose_name=_("Justification for selection of storage solution(s)"),
                                             help_text=_("Provide your rational for the selection(s) made above."))
    storage_needed = models.TextField(blank=True, null=True, verbose_name=_("What is the estimated storage space needed for the above?"),
                                      help_text=_("This includes raw field data, processed data, and all other data products etc.)"))
    raw_data_retention = models.TextField(blank=True, null=True, verbose_name=_("What is the retention policy for the raw field data?"), help_text=_(
        "This would include instrument data, field sheets, physical samples etc. Please refer to the DFO EOS Retention Policy for clarification)"))
    data_retention = models.TextField(blank=True, null=True, verbose_name=_("What is the retention policy for the data?"),
                                      help_text=_("Please refer to the DFO EOS Retention Policy for clarification."))
    backup_plan = models.TextField(blank=True, null=True, verbose_name=_("What procedures will be taken to back-up/secure the data?"))
    cloud_costs = models.TextField(blank=True, null=True,
                                   verbose_name=_("If using cloud storage, what is the estimated annual cost and who will be covering the cost? "),
                                   help_text=_(
                                       "e.g., cloud storage is estimated at $1000/yr and will be paid for under the the division manager's budget"))

    # Sharing
    had_sharing_agreements = models.BooleanField(default=False, verbose_name=_("Is the dataset subject to a data sharing agreement, MOU, etc.?"),
                                                 choices=YES_NO_CHOICES)
    sharing_agreements_text = models.TextField(blank=True, null=True, verbose_name=_("If yes, who are the counterparts for the agreement(s)?"),
                                               help_text=_("please provide the name of the organization and the primary contact for each agreement."))
    publication_timeframe = models.TextField(blank=True, null=True, verbose_name=_("How soon after data collection will data be made available?"),
                                             help_text=_("The answer provided will set the expectation for the open data publication frequency"))
    publishing_platforms = models.TextField(blank=True, null=True, verbose_name=_("Which open data publishing mechanism(s) will be used?"), help_text=_(
        "The best option is the Government of Canada's Open Data Platform however other platforms / publications are acceptable provided they are"
        " freely available to the general public."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Additional comments to take into consideration (if applicable):"))
    # todo remove once the Ppt models are removed
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='inventorydmas_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='inventorydmas_updated_by')

    class Meta:
        verbose_name = _("Data Management Agreement")
        ordering = ["section__division__branch__sector__region", "section__division", "section", "title"]

    def get_absolute_url(self):
        return reverse('inventory:dma_detail', args=[self.id])

    def save(self, *args, **kwargs):
        # set the status...
        if not self.reviews.exists():
            self.status = 0  # unevaluated
        else:
            last_review = self.reviews.last()
            if last_review.is_final_review:
                self.status = 2  # complete
            elif last_review.decision == 1:  # compliant
                self.status = 1  # on-track
                # but wait, what if this is an old evaluation?
                # if the review was more than six months old, set the status to 5
                if (timezone.now() - last_review.created_at).days > (28 * 6):
                    self.status = 5  # pending evaluation

            elif last_review.decision == 2:  # non-compliant
                self.status = 3  # encountering issues

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def status_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_status_display())}">{self.get_status_display()}</span>')

    @property
    def region(self):
        if self.section:
            return self.section.division.branch.sector.region


class DMAReview(MetadataFields):
    decision_choices = (
        (0, _("Unevaluated")),
        (1, _("Compliant")),
        (2, _("Non-compliant")),
    )
    dma = models.ForeignKey(DMA, related_name="reviews", on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="inventory_dma_reviews", on_delete=models.DO_NOTHING,
                                    default=fiscal_year(timezone.now(), sap_style=True))
    decision = models.IntegerField(default=0, choices=decision_choices)
    is_final_review = models.BooleanField(default=False, verbose_name=_("Will this be the final review of this agreement?"),
                                          help_text=_("If so, please make sure to provide an explanation in the comments field."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))
    # todo remove once the Ppt models are removed
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='inventorydmareviews_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='inventorydmareviews_updated_by')

    class Meta:
        ordering = ["fiscal_year", '-created_at']
        unique_together = [
            ('dma', 'fiscal_year'),  # there should only be a single review per year on a given DMA
        ]

    @property
    def comments_html(self):
        if self.comments:
            return mark_safe(markdown(self.comments))

    @property
    def decision_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_decision_display())}">{self.get_decision_display()}</span>')
