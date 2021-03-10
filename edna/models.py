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
    location_description = models.TextField(blank=True, null=True, verbose_name=_("location description"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='edna_collections', blank=True, null=True)
    contact_users = models.ManyToManyField(User, blank=True, verbose_name=_("contact DMApps user(s)"))
    contact_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("contact name"))
    contact_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_("contact email"))
    filtration_type = models.ForeignKey(FiltrationType, on_delete=models.DO_NOTHING, related_name="collections", verbose_name=_("filtration type"))
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
    collection = models.ForeignKey(Collection, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("collection"))
    datetime = models.DateTimeField(verbose_name=_("collection date"), blank=False, null=True)
    site_description = models.TextField(blank=True, null=True, verbose_name=_("site description"))
    site_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("site identifier"))
    collector = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("weather notes"))
    sample_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("sample identifier"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("longitude"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("field comments"))

    class Meta:
        ordering = ["-datetime", "collection"]

    def get_absolute_url(self):
        return reverse("edna:sample_detail", args=[self.pk])


class LabSample(models.Model):
    field_sample = models.ForeignKey(Sample, related_name='lab_samples', on_delete=models.DO_NOTHING, verbose_name=_("field sample"))
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
    lab_sample = models.ForeignKey(LabSample, related_name='observations', on_delete=models.DO_NOTHING, verbose_name=_("lab sample"))
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
