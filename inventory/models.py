import uuid

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import default_if_none, slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from markdown import markdown

from lib.functions.custom_functions import truncate, fiscal_year, listrify
from shared_models import models as shared_models
# Choices for language
from shared_models.models import SimpleLookup, Region, MetadataFields
from . import model_choices
from .data_fixtures import statuses, maintenance_levels, security_classifications, character_sets, spatial_representation_types, spatial_reference_systems, \
    resource_types, content_types

LANGUAGE_CHOICES = ((1, 'English'), (2, 'French'),)
YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]
NULL_YES_NO_CHOICES = (
    (None, _("Unsure")),
    (1, _("Yes")),
    (0, _("No")),
)

class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="inventory_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="inventory_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class DistributionFormat(SimpleLookup):
    pass


class StorageSolution(SimpleLookup):
    pass


class Location(models.Model):
    location_eng = models.CharField(max_length=1000, blank=True, null=True)
    location_fre = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=25, choices=model_choices.country_choices)
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
    """
    TODO This field should be removed and replaced by the Shared Models.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="person")
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    position_eng = models.CharField(max_length=255, blank=True, null=True)
    position_fre = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    language = models.IntegerField(choices=LANGUAGE_CHOICES, blank=True, null=True, verbose_name=_("language preference"))

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def save(self, *args, **kwargs):
        self.full_name = "{} {}".format(self.user.first_name, self.user.last_name)

        super().save(*args, **kwargs)


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


class Resource(models.Model):
    # IDENTIFICATION
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="resources")
    title_eng = models.TextField(verbose_name="Title (English)")
    title_fre = models.TextField(blank=True, null=True, verbose_name="Title (French)")
    purpose_eng = models.TextField(blank=True, null=True, verbose_name="Purpose (English)")
    purpose_fre = models.TextField(blank=True, null=True, verbose_name="Purpose (French)")
    descr_eng = models.TextField(blank=True, null=True, verbose_name="Description (English)")
    descr_fre = models.TextField(blank=True, null=True, verbose_name="Description (French)")
    notes = models.TextField(blank=True, null=True, verbose_name="General notes (DFO internal)")


    # MANDATORY METADATA
    resource_type = models.IntegerField(choices=model_choices.resource_type_choices, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True, choices=model_choices.status_choices)
    maintenance = models.IntegerField(blank=True, null=True, verbose_name="At what frequency should the metadata be updated?",
                                      choices=model_choices.maintenance_choices,
                                      help_text=_("What should be the expectation for how often the metadata is updated?"))
    maintenance_text = models.TextField(blank=True, null=True, verbose_name=_("Justification for frequency:"),
                                        help_text=_("What justification can be provided for the above selection?"))

    time_start_day = models.IntegerField(blank=True, null=True, verbose_name="Start day")
    time_start_month = models.IntegerField(blank=True, null=True, verbose_name="Start month")
    time_start_year = models.IntegerField(blank=True, null=True, verbose_name="Start year")
    time_end_day = models.IntegerField(blank=True, null=True, verbose_name="End day")
    time_end_month = models.IntegerField(blank=True, null=True, verbose_name="End month")
    time_end_year = models.IntegerField(blank=True, null=True, verbose_name="End year")

    geo_descr_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Geographic description (English)")
    geo_descr_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Geographic description (French)")
    west_bounding = models.FloatField(blank=True, null=True, verbose_name="West bounding coordinate")
    south_bounding = models.FloatField(blank=True, null=True, verbose_name="South bounding coordinate")
    east_bounding = models.FloatField(blank=True, null=True, verbose_name="East bounding coordinate")
    north_bounding = models.FloatField(blank=True, null=True, verbose_name="North bounding coordinate")

    security_classification = models.IntegerField(blank=True, null=True, choices=model_choices.security_classification_choices)
    security_use_limitation_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="Security use limitation (English)")
    security_use_limitation_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="Security use limitation (French)")

    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True, related_name='children',
                               verbose_name="Parent resource", help_text=_("Is this record a child of another metadata record?"))
    distribution_formats = models.ManyToManyField(DistributionFormat, blank=True)
    data_char_set = models.IntegerField(blank=True, null=True, verbose_name="Data character set", choices=model_choices.data_char_set_choices,
                                        help_text=_("What is the encoding type of the distribution format? If you are using excel, please select ASCII."))

    spat_representation = models.IntegerField(blank=True, null=True, verbose_name="Spatial representation type",
                                              choices=model_choices.spat_representation_choices)
    spat_ref_system = models.IntegerField(blank=True, null=True, verbose_name="Spatial reference system", choices=model_choices.spat_ref_system_choices)
    resource_constraint_eng = models.TextField(blank=True, null=True, verbose_name="Resource constraint (English)")
    resource_constraint_fre = models.TextField(blank=True, null=True, verbose_name="Resource constraint (French)")

    # OPTIONAL METADATA
    sampling_method_eng = models.TextField(blank=True, null=True, verbose_name="Sampling method (English)")
    sampling_method_fre = models.TextField(blank=True, null=True, verbose_name="Sampling method (French)")
    physical_sample_descr_eng = models.TextField(blank=True, null=True, verbose_name="Description of physical samples (English)")
    physical_sample_descr_fre = models.TextField(blank=True, null=True, verbose_name="Description of physical samples (French)")
    qc_process_descr_eng = models.TextField(blank=True, null=True, verbose_name="QC process description (English)")
    qc_process_descr_fre = models.TextField(blank=True, null=True, verbose_name="QC process description (French)")
    parameters_collected_eng = models.TextField(blank=True, null=True, verbose_name="Parameters collected (English)")
    parameters_collected_fre = models.TextField(blank=True, null=True, verbose_name="Parameters collected (French)")
    analytic_software = models.TextField(blank=True, null=True, verbose_name="Is any special software required?")
    additional_credit = models.TextField(blank=True, null=True)

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
    had_sharing_agreements = models.IntegerField(verbose_name=_("Is the dataset subject to a data sharing agreement, MOU, etc.?"), blank=True, null=True,
                                                 choices=NULL_YES_NO_CHOICES)
    sharing_agreements_text = models.TextField(blank=True, null=True, verbose_name=_("If yes, who are the counterparts for the agreement(s)?"),
                                               help_text=_("please provide the name of the organization and the primary contact for each agreement."))
    publication_timeframe = models.TextField(blank=True, null=True, verbose_name=_("How soon after data collection will data be made available?"),
                                             help_text=_("The answer provided will set the expectation for the open data publication frequency"))
    publishing_platforms = models.TextField(blank=True, null=True, verbose_name=_("Which open data publishing mechanism(s) will be used?"), help_text=_(
        "The best option is the Government of Canada's Open Data Platform however other platforms / publications are acceptable provided they are"
        " freely available to the general public."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Additional comments to take into consideration (if applicable):"))

    # Open Data Publication
    fgp_url = models.URLField(blank=True, null=True, verbose_name="Link to record on FGP")
    public_url = models.URLField(blank=True, null=True, verbose_name="Link to record on Open Gov't Portal")
    thumbnail_url = models.URLField(blank=True, null=True, verbose_name="Public URL to thumbnail image")
    fgp_publication_date = models.DateTimeField(blank=True, null=True, verbose_name="Date published to FGP")
    od_publication_date = models.DateTimeField(blank=True, null=True, verbose_name="Date published to Open Gov't Portal")
    od_release_date = models.DateTimeField(blank=True, null=True, verbose_name="Date released to Open Gov't Portal")
    last_revision_date = models.DateTimeField(blank=True, null=True, verbose_name="Date of last published revision")
    open_data_notes = models.TextField(blank=True, null=True,
                                       verbose_name="Open data notes")

    # M2m
    citations2 = models.ManyToManyField(shared_models.Citation, related_name='resources', blank=True)
    keywords = models.ManyToManyField(Keyword, related_name='resources', blank=True)

    # non editable etc
    uuid = models.UUIDField(blank=True, null=True, verbose_name="UUID", unique=True, editable=False)
    review_status = models.IntegerField(default=0, editable=False, choices=model_choices.dma_status_choices)
    date_last_modified = models.DateTimeField(auto_now=True, editable=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, editable=False, blank=True, null=True,
                                         related_name="resource_last_modified_by_users")
    flagged_4_deletion = models.BooleanField(default=False, editable=False)
    flagged_4_publication = models.BooleanField(default=False, verbose_name=_("Flagged for Publication"), editable=False)
    completedness_report = models.TextField(blank=True, null=True, verbose_name=_("completedness report"), editable=False)
    completedness_rating = models.FloatField(blank=True, null=True, verbose_name=_("completedness rating"), editable=False)
    translation_needed = models.BooleanField(default=True, verbose_name=_("translation needed"), editable=False)
    publication_fy = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False,
                                       verbose_name=_("FY of latest publication"))
    date_verified = models.DateTimeField(blank=True, null=True, editable=False)
    favourited_by = models.ManyToManyField(User, editable=False, related_name="resource_favourited_by")
    has_dma = models.BooleanField(default=False, verbose_name=_("Does this record have a formalized data management agreement?"), editable=False)

    # TO BE DELETED
    odi_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("ODIP Identifier"), unique=True, editable=False)

    def get_absolute_url(self):
        return reverse('inventory:resource_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return self.t_title

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

        # set the review status...
        if not self.reviews.exists():
            self.review_status = 0  # unevaluated
        else:
            last_review = self.reviews.last()
            if last_review.is_final_review:
                self.review_status = 2  # complete
            elif last_review.decision == 1:  # compliant
                self.review_status = 1  # on-track
                # but wait, what if this is an old evaluation?
                # if the review was more than six months old, set the status to 5
                if (timezone.now() - last_review.created_at).days > (28 * 6):
                    self.review_status = 5  # pending evaluation

            elif last_review.decision == 2:  # non-compliant
                self.review_status = 3  # encountering issues

        super().save(*args, **kwargs)

    @property
    def review_status_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_review_status_display())}">{self.get_review_status_display()}</span>')

    @property
    def region(self):
        if self.section:
            return self.section.division.branch.sector.region

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

    def get_custodians(self):
        return self.resource_people2.filter(roles__code__iexact="RI_409").distinct()

    def get_points_of_contact(self):
        return self.resource_people2.filter(roles__code__iexact="RI_414").distinct()

    def get_status_instance(self):
        if self.status:
            return statuses.get_instance(self.status)

    def get_maintenance_instance(self):
        if self.maintenance:
            return maintenance_levels.get_instance(self.maintenance)

    def get_security_classification_instance(self):
        if self.security_classification:
            return security_classifications.get_instance(self.security_classification)

    def get_data_char_set_instance(self):
        if self.data_char_set:
            return character_sets.get_instance(self.data_char_set)

    def get_spat_representation_instance(self):
        if self.spat_representation:
            return spatial_representation_types.get_instance(self.spat_representation)

    def get_spat_ref_system_instance(self):
        if self.spat_ref_system:
            return spatial_reference_systems.get_instance(self.spat_ref_system)

    def get_resource_type_instance(self):
        if self.resource_type:
            return resource_types.get_instance(self.resource_type)


class ResourcePerson2(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_people2", editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="resource_people")
    roles = models.ManyToManyField(PersonRole, verbose_name=_("roles"), blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("affiliated organization"))

    @property
    def is_custodian(self):
        return self.roles.filter(code__iexact="RI_409").exists()

    class Meta:
        unique_together = (('resource', 'user'),)
        ordering = ['user']
        verbose_name = "Resource Person"
        verbose_name_plural = "Resource People"

    def get_absolute_url(self):
        return reverse('inventory:resource_detail', kwargs={'pk': self.resource.id})

    @property
    def roles_display(self):
        if self.roles.exists():
            return listrify(self.roles.all())

    def __str__(self):
        payload = f"{self.user}"
        return payload


class Review(MetadataFields):
    resource = models.ForeignKey(Resource, related_name="reviews", on_delete=models.CASCADE, editable=False)
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="inventory_reviews", on_delete=models.DO_NOTHING,
                                    default=fiscal_year(timezone.now(), sap_style=True))
    decision = models.IntegerField(default=0, choices=model_choices.review_decision_choices)
    is_final_review = models.BooleanField(default=False, verbose_name=_("Will this be the final review of this agreement?"),
                                          help_text=_("If so, please make sure to provide an explanation in the comments field."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))

    class Meta:
        ordering = ["fiscal_year", '-created_at']
        unique_together = [
            ('resource', 'fiscal_year'),  # there should only be a single review per year on a given DMA
        ]

    @property
    def comments_html(self):
        if self.comments:
            return mark_safe(markdown(self.comments))

    @property
    def decision_display(self):
        return mark_safe(f'<span class=" px-1 py-1 {slugify(self.get_decision_display())}">{self.get_decision_display()}</span>')


class DataResource(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="data_resources", editable=False)
    url = models.URLField()
    name_eng = models.CharField(max_length=255, verbose_name="Name (English)")
    name_fre = models.CharField(max_length=255, verbose_name="Name (French)")
    protocol = models.CharField(max_length=255, choices=model_choices.protocol_choices)
    content_type = models.IntegerField(choices=model_choices.content_type_choices)

    def __str__(self):
        return "{} - {}".format(self.get_content_type_instance().title, self.name_eng)

    def get_content_type_instance(self):
        if self.content_type:
            return content_types.get_instance(self.content_type)


class WebService(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="web_services", editable=False)
    protocol = models.CharField(max_length=255, default="ESRI REST: Map Service")
    service_language = models.CharField(max_length=255, choices=model_choices.service_language_choices)
    url = models.URLField()
    name_eng = models.CharField(max_length=255, verbose_name="Name (English)")
    name_fre = models.CharField(max_length=255, verbose_name="Name (French)")
    content_type = models.IntegerField(choices=model_choices.content_type_choices)

    def __str__(self):
        return "{} - {}".format(self.get_content_type_instance().title, self.name_eng)

    def get_content_type_instance(self):
        if self.content_type:
            return content_types.get_instance(self.content_type)


class ResourcePerson(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_people")
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="resource_people")
    role = models.ForeignKey(PersonRole, on_delete=models.DO_NOTHING, verbose_name=_("role"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

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
    date = models.DateTimeField(blank=True, null=True, auto_now=True, editable=False)

    class Meta:
        ordering = ['-date']


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


class DMA(MetadataFields):
    status = models.IntegerField(default=3, editable=False, choices=model_choices.dma_status_choices)

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
                                               help_text=_("What should be the expectation for how often the metadata is updated?"),
                                               choices=model_choices.dma_frequency_choices)
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
        ordering = ["section__division__branch__sector__region", "status", "title"]

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
    def region(self):
        if self.section:
            return self.section.division.branch.sector.region

    @property
    def display_with_region(self):
        return str(self) + f" ({self.region})"


class DMAReview(MetadataFields):
    dma = models.ForeignKey(DMA, related_name="reviews", on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="inventory_dma_reviews", on_delete=models.DO_NOTHING,
                                    default=fiscal_year(timezone.now(), sap_style=True))
    decision = models.IntegerField(default=0, choices=model_choices.review_decision_choices)
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
