from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region
from shared_models.utils import get_metadata_string


class FiltrationType(UnilingualLookup):
    pass


class DNAExtractionProtocol(UnilingualLookup):
    pass


class Tag(SimpleLookup):
    pass


class Species(models.Model):
    common_name_en = models.CharField(max_length=255, verbose_name=_("common name (EN)"))
    common_name_fr = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("common name (FR)"))
    scientific_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("scientific name"))
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")

    @property
    def tcommon(self):
        # check to see if a french value is given
        if getattr(self, str(_("common_name_en"))):
            my_str = f'{getattr(self, str(_("common_name_en")))}'
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.common_name_en
        return my_str

    def __str__(self):
        return self.tcommon

    class Meta:
        ordering = ['id']
        verbose_name_plural = _("Species")

    def get_absolute_url(self):
        return reverse('diets:species_detail', kwargs={'pk': self.id})

    @property
    def full_name(self):
        return "{} (<em>{}</em>)".format(self.common_name_en, self.scientific_name)

    @property
    def formatted_scientific(self):
        return f"<em>{self.scientific_name}</em>"


class Collection(UnilingualSimpleLookup):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name='edna_collections', blank=True, null=True, verbose_name=_("DFO region"))
    program_description = models.TextField(blank=True, null=True, verbose_name=_("program description"))
    location_description = models.TextField(blank=True, null=True, verbose_name=_("area of operation"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='edna_collections', blank=True, null=True)
    contact_users = models.ManyToManyField(User, blank=True, verbose_name=_("contact DMApps user(s)"))
    contact_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("contact name"))
    contact_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_("contact email"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("tags"))

    # calculated
    start_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("start date"))
    end_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("end date"))
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, related_name="collections", blank=True, null=True, editable=False)

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_collection_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_collection_updated_by", blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    @property
    def dates(self):
        my_str = date(self.start_date)
        if self.end_date:
            my_str += f" &rarr; {date(self.end_date)}"
        return mark_safe(my_str)

    @property
    def sample_count(self):
        return self.samples.count()

    @property
    def contacts(self):
        if self.contact_users.exists():
            return mark_safe(listrify([f'<a href="mailto:{u.email}">{u.get_full_name()}</a>' for u in self.contact_users.all()]))
        return mark_safe(f'<a href="mailto:{self.contact_email}">{self.contact_name}</a>')

    def get_absolute_url(self):
        return reverse("edna:collection_detail", args=[self.pk])


class Sample(models.Model):
    collection = models.ForeignKey(Collection, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("collection"), editable=False)
    datetime = models.DateTimeField(verbose_name=_("collection date"))
    unique_sample_identifier = models.CharField(max_length=255, unique=True, verbose_name=_("bottle unique identifier"))
    site_identifier = models.CharField(max_length=255, verbose_name=_("site identifier"))
    site_description = models.TextField(verbose_name=_("site description"))
    samplers = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("sampler(s)"))
    latitude = models.FloatField(blank=False, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=False, null=True, verbose_name=_("longitude"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["-datetime", "collection"]

    def get_absolute_url(self):
        return reverse("edna:sample_detail", args=[self.pk])

    def __str__(self):
        return


class FiltrationBatch(models.Model):
    datetime = models.DateTimeField(auto_now=True, verbose_name=_("start date/time"))
    operators = models.ManyToManyField(User, blank=True, verbose_name=_("operators"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["datetime"]


class Filter(models.Model):
    """ the filter id of this table is effectively the tube id"""
    filtration_batch = models.ForeignKey(FiltrationBatch, related_name='filters', on_delete=models.DO_NOTHING, verbose_name=_("filtration batch"))
    sample = models.ForeignKey(Sample, related_name='filters', on_delete=models.DO_NOTHING, verbose_name=_("field sample"), blank=True, null=True)
    filtration_type = models.ForeignKey(FiltrationType, on_delete=models.DO_NOTHING, related_name="filters", verbose_name=_("filtration type"), default=1)
    start_datetime = models.DateTimeField(verbose_name=_("start time"))
    duration_min = models.IntegerField(verbose_name=_("duration (min)"), blank=True, null=True)
    filtration_volume_ml = models.FloatField(blank=True, null=True, verbose_name=_("volume (ml)"))
    storage_location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("storage location"))
    comments = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("comments"))

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_filter_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_filter_updated_by", blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ["filtration_batch", "sample"]


class ExtractionBatch(models.Model):
    datetime = models.DateTimeField(auto_now=True, verbose_name=_("start date/time"))
    operators = models.ManyToManyField(User, blank=True, verbose_name=_("operators"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["datetime"]


class DNAExtract(models.Model):
    """ the filter id of this table is effectively the tube id"""
    filter_id = models.OneToOneField(Filter, on_delete=models.CASCADE)
    extraction_batch = models.ForeignKey(ExtractionBatch, related_name='extracts', on_delete=models.DO_NOTHING, verbose_name=_("extraction batch"))
    start_datetime = models.DateTimeField(verbose_name=_("start time"))
    dna_extraction_protocol = models.ForeignKey(DNAExtractionProtocol, on_delete=models.DO_NOTHING, verbose_name=_("extraction protocol"))
    storage_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("storage location"))

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_extract_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_extract_updated_by", blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ["extraction_batch", "filter_id"]


class PCRBatch(models.Model):
    datetime = models.DateTimeField(auto_now=True, verbose_name=_("start date/time"))
    operators = models.ManyToManyField(User, blank=True, verbose_name=_("operators"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["datetime"]


class PCR(models.Model):
    """ the filter id of this table is effectively the tube id"""
    extract_id = models.OneToOneField(DNAExtract, on_delete=models.CASCADE)
    pcr_batch = models.ForeignKey(ExtractionBatch, related_name='pcrs', on_delete=models.DO_NOTHING, verbose_name=_("PCR batch"))
    start_datetime = models.DateTimeField(verbose_name=_("start time"))
    pcr_number = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("PCR number"))
    plate_id = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("plate id"))
    position = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("position"))
    ipc_added = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("IPC added"))
    qpcr_ipc = models.FloatField(blank=True, null=True, verbose_name=_("qPCR IPC"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_pcr_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_pcr_updated_by", blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ["pcr_batch", "extract_id"]


class SpeciesObservation(models.Model):
    pcr = models.ForeignKey(PCR, related_name='observations', on_delete=models.DO_NOTHING, verbose_name=_("PCR"))
    species = models.ForeignKey(Species, related_name='observations', on_delete=models.DO_NOTHING, verbose_name=_("species"))
    ct_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 1"))
    edna_conc_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 1"))
    ct_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 2"))
    edna_conc_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 2"))
    ct_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 3"))
    edna_conc_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 3"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_obs_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_obs_updated_by", blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(
            self.created_at,
            self.created_by,
            self.updated_at,
            self.updated_by,
        )

    class Meta:
        ordering = ["pcr", "species"]
