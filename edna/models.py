from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear
from shared_models.utils import get_metadata_string


class ExperimentType(UnilingualLookup):
    pass


class DNAExtractionProtocol(UnilingualLookup):
    pass


class Species(models.Model):
    common_name_en = models.CharField(max_length=255, blank=True, null=True)
    common_name_fr = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")

    def __str__(self):
        return self.common_name_en if self.common_name_en else self.scientific_name

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('diets:species_detail', kwargs={'pk': self.id})

    @property
    def full_name(self):
        return "{} (<em>{}</em>)".format(self.common_name_en, self.scientific_name)


class Collection(UnilingualSimpleLookup):
    program_description = models.TextField(blank=True, null=True, verbose_name=_("program description"))
    site_description = models.TextField(blank=True, null=True, verbose_name=_("site description"))
    site_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("site identifier"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='edna_regions', blank=True, null=True)
    contact_users = models.ManyToManyField(User, blank=True, verbose_name=_("contact DMApps user(s)"))
    contact_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("contact_name"))
    contact_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_("contact_email"))
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.DO_NOTHING, related_name="collections", verbose_name=_("experiment type"))

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


class FieldSample(models.Model):
    collection = models.ForeignKey(Collection, related_name='field_samples', on_delete=models.DO_NOTHING, verbose_name=_("collection"))
    datetime = models.DateTimeField(verbose_name=_("collection date"), blank=False, null=True)
    collector = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("weather notes"))
    sample_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("sample identifier"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("longitude"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["-datetime", "collection"]

    def get_absolute_url(self):
        return reverse("edna:field_sample_detail", args=[self.pk])


class LabSample(models.Model):
    field_sample = models.ForeignKey(Collection, related_name='lab_samples', on_delete=models.DO_NOTHING, verbose_name=_("field sample"))
    tube_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("tube ID"))
    # filtration phase
    filtration_datetime = models.DateTimeField(verbose_name=_("filtration date"))
    filtration_duration_mins = models.IntegerField(verbose_name=_("filtration duration (minutes)"), blank=True, null=True)
    filtration_volume_ml = models.FloatField(blank=True, null=True, verbose_name=_("filtration volume (ml)"))
    filtration_comments = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("filtration comments"))
    filter_storage_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("filter storage location"))
    # extraction phase
    dna_extraction_datetime = models.DateTimeField(verbose_name=_("filtration date"), blank=True, null=True)
    dna_extraction_protocol = models.ForeignKey(DNAExtractionProtocol, related_name='lab_samples', on_delete=models.DO_NOTHING,
                                                verbose_name=_("DNA extraction protocol"))
    dna_extract_storage_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("DNA extraction storage location"))
    # PCR phase
    pcr_datetime = models.DateTimeField(verbose_name=_("PCR date"), blank=True, null=True)
    pcr_number = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("PCR number"))
    plate_id = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("plate id"))
    position = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("position"))
    ipc_added = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("IPC added"))
    qpcr_ipc = models.FloatField(blank=True, null=True, verbose_name=_("qPCR IPC"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    # metadata
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_lab_sample_created_by", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="edna_lab_sample_updated_by", blank=True, null=True, editable=False)
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
        ordering = ["field_sample", "tube_identifier"]


class SpeciesObservation(models.Model):
    lab_sample = models.ForeignKey(Collection, related_name='observations', on_delete=models.DO_NOTHING, verbose_name=_("lab sample"))
    species = models.ForeignKey(Species, related_name='observations', on_delete=models.DO_NOTHING, verbose_name=_("species"))
    ct_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 1"))
    edna_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 1"))
    ct_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 2"))
    edna_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 2"))
    ct_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("cycle threshold (ct) - rep 3"))
    edna_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("eDNA concentration (Pg/L) - rep 3"))
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
        ordering = ["lab_sample", "species"]
