import math

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from shapely.geometry import Polygon, Point

from edna.utils import get_timezone_time
from lib.functions.custom_functions import listrify, fiscal_year
from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, FiscalYear, Region, MetadataFields
from shared_models.utils import format_coordinates

YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)


class ednaUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="edna_user", verbose_name=_("DM Apps user"))
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)
    is_crud_user = models.BooleanField(default=False, verbose_name=_("CRUD permissions?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class FiltrationType(UnilingualLookup):
    pass


class DNAExtractionProtocol(UnilingualLookup):
    pass


class Tag(SimpleLookup):
    pass


class SampleType(SimpleLookup):
    pass


class MasterMix(SimpleLookup):
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
        return self.full_name

    class Meta:
        ordering = ['id']
        verbose_name_plural = _("Species")

    def get_absolute_url(self):
        return reverse('edna:species_detail', kwargs={'pk': self.id})

    @property
    def full_name(self):
        return "{} (<em>{}</em>)".format(self.common_name_en, self.scientific_name)

    @property
    def full_name_plain_text(self):
        return "{} ({})".format(self.common_name_en, self.scientific_name)

    @property
    def formatted_scientific(self):
        return f"<em>{self.scientific_name}</em>"


class Assay(UnilingualSimpleLookup, MetadataFields):
    alias = models.CharField(max_length=50, verbose_name=_("target name / alias"),
                             help_text=_("This is the name that will be used to reference this assay on import spreadsheets."))
    lod = models.FloatField(blank=True, null=True, verbose_name=_("LOD value"))
    loq = models.FloatField(blank=True, null=True, verbose_name=_("LOQ value"))
    units = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("Units for LOQ and LOD"))
    a_coef = models.FloatField(blank=True, null=True, verbose_name=_("formula A coefficient"))
    b_coef = models.FloatField(blank=True, null=True, verbose_name=_("formula B coefficient"))
    is_ipc = models.BooleanField(default=False, verbose_name=_("is this assay being used as an IPC?"), choices=YES_NO_CHOICES)
    species = models.ManyToManyField(Species, verbose_name=_("species"), blank=True)

    def __str__(self):
        mystr = f"{self.name} ({self.alias})"
        # if self.is_ipc:
        #     mystr += ' (IPC)'
        return mystr

    class Meta:
        verbose_name_plural = "Assays"
        ordering = ["name", ]

    @property
    def species_display(self):
        return listrify(self.species.all())


class Collection(UnilingualSimpleLookup, MetadataFields):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name='edna_collections', blank=True, null=True, verbose_name=_("DFO region"))
    description = models.TextField(blank=True, null=True, verbose_name=_("project description"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='edna_collections', blank=True, null=True)
    contact_users = models.ManyToManyField(User, blank=True, verbose_name=_("contact DMApps user(s)"))
    contact_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("contact name"))
    contact_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_("contact email"))

    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("tags"))

    # calculated
    start_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("start date"))
    end_date = models.DateTimeField(blank=True, null=True, editable=False, verbose_name=_("end date"))
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.DO_NOTHING, related_name="collections", blank=True, null=True, editable=False)

    class Meta:
        ordering = ["name", ]
        verbose_name = _("Project")

    def save(self, *args, **kwargs):
        qs = self.samples.all()
        if qs.filter(datetime__isnull=False).exists():
            self.start_date = qs.order_by("datetime").first().datetime
            self.end_date = qs.order_by("datetime").last().datetime
            self.fiscal_year_id = fiscal_year(self.end_date, sap_style=True)
        super().save(*args, **kwargs)

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

    def get_points(self):
        poly_points = list()
        for sample in self.samples.all():
            point = sample.get_point()
            if point:
                poly_points.append(point)
        return poly_points

    def get_polygon(self):
        points = self.get_points()
        if len(points) >= 3:
            return Polygon(points)

    def get_centroid(self):
        points = self.get_points()
        if self.get_polygon():
            p = self.get_polygon()
            return p.centroid
        elif len(points) > 0:
            return points[-1]


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'edna/{0}/{1}'.format(instance.collection.id, filename)


class File(models.Model):
    collection = models.ForeignKey(Collection, related_name="files", on_delete=models.CASCADE, editable=False)
    caption = models.CharField(max_length=255)
    file = models.FileField(upload_to=file_directory_path)
    date_created = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.caption


class Batch(models.Model):
    datetime = models.DateTimeField(default=timezone.now, verbose_name=_("date/time"))
    operators = models.ManyToManyField(User, blank=True, verbose_name=_("operator(s)"))
    default_collection = models.ForeignKey(Collection, on_delete=models.DO_NOTHING, verbose_name=_("project"), blank=False, null=True)
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"))

    class Meta:
        ordering = ["-datetime"]
        abstract = True

    @property
    def display_time(self):
        return get_timezone_time(self.datetime).strftime("%Y-%m-%d %H:%M")


class SampleBatch(Batch):
    datetime = models.DateTimeField(default=timezone.now, verbose_name=_("date received at facility"))
    operators = models.ManyToManyField(User, blank=True, verbose_name=_("Received by"))
    sent_by = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Received from"))
    storage_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Storage Location at Reception"))

    class Meta:
        verbose_name_plural = _("Sample Collection / Receipt")
        ordering = ["-datetime"]

    def __str__(self):
        return "{} {} ({})".format(_("Sample Collection"), self.id, self.datetime.strftime("%Y-%m-%d"))

    def get_absolute_url(self):
        return reverse('edna:sample_batch_detail', kwargs={'pk': self.id})

    @property
    def sample_count(self):
        return self.samples.count()


class Sample(MetadataFields):
    collection = models.ForeignKey(Collection, related_name='samples', on_delete=models.CASCADE, verbose_name=_("project"))
    sample_batch = models.ForeignKey(SampleBatch, related_name='samples', on_delete=models.CASCADE, verbose_name=_("sample collection / receipt"))
    sample_type = models.ForeignKey(SampleType, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("sample type"))
    is_field_blank = models.BooleanField(default=False, verbose_name=_("is this a field blank?"))
    bottle_id = models.CharField(verbose_name=_("bottle ID"), blank=True, null=True, max_length=50)
    location = models.CharField(max_length=255, verbose_name=_("location"), blank=True, null=True)
    site = models.CharField(max_length=255, verbose_name=_("site"), blank=True, null=True)
    station = models.TextField(verbose_name=_("station"), blank=True, null=True)
    datetime = models.DateTimeField(verbose_name=_("collection date/time"), blank=False, null=True, default=timezone.now)
    samplers = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("collector name"))
    latitude = models.FloatField(blank=False, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=False, null=True, verbose_name=_("longitude"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"))

    # calc
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='edna_samples_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='edna_samples_updated_by')

    def save(self, *args, **kwargs):
        # if not self.bottle_id:
        #     self.bottle_id = get_next_bottle_id()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["datetime", "id"]
        unique_together = (("bottle_id", "sample_batch"))

    def get_absolute_url(self):
        return reverse("edna:sample_detail", args=[self.pk])

    def __str__(self):
        mystr = f"s{self.id}"
        # if self.is_field_blank:
        #     mystr += " (field blank)"
        return mystr

    @property
    def display(self):
        return str(self)

    def get_point(self):
        if self.latitude and self.longitude:
            return Point(self.latitude, self.longitude)

    @property
    def coordinates(self):
        my_str = "---"
        point = self.get_point()
        if point:
            my_str = format_coordinates(point.x, point.y, output_format="dd", sep="|")
        return mark_safe(my_str)

    @property
    def extracts(self):
        return DNAExtract.objects.filter(filter__sample=self)

    @property
    def pcrs(self):
        return PCR.objects.filter(extract__filter__sample=self)

    @property
    def assays(self):
        return PCRAssay.objects.filter(pcr__extract__filter__sample=self)

    @property
    def filter_count(self):
        return self.filters.count()

    @property
    def extract_count(self):
        return self.extracts.count()

    @property
    def pcr_count(self):
        return self.pcrs.count()

    @property
    def assay_count(self):
        return self.assays.count()

    @property
    def full_display(self):
        mystr = str(self)
        # if self.bottle_id:
        #     mystr += f" | b{self.bottle_id}"
        return mystr

    @property
    def is_deletable(self):
        return not self.filters.exists() and not self.extracts.exists()


class FiltrationBatch(Batch):
    class Meta:
        verbose_name_plural = _("Filtration Batches")
        ordering = ["-datetime"]

    def __str__(self):
        return "{} {} ({})".format(_("Filtration Batch"), self.id, self.datetime.strftime("%Y-%m-%d"))

    def get_absolute_url(self):
        return reverse('edna:filtration_batch_detail', kwargs={'pk': self.id})

    @property
    def filter_count(self):
        return self.filters.count()


class Filter(MetadataFields):
    """ the filter id of this table is effectively the tube id"""
    filtration_batch = models.ForeignKey(FiltrationBatch, related_name='filters', on_delete=models.CASCADE, verbose_name=_("filtration batch"))
    sample = models.ForeignKey(Sample, related_name='filters', on_delete=models.DO_NOTHING, verbose_name=_("sample ID"), blank=True, null=True)
    collection = models.ForeignKey(Collection, related_name='filters', on_delete=models.DO_NOTHING, verbose_name=_("project"), blank=True, null=True)
    tube_id = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("tube ID"))
    filtration_type = models.ForeignKey(FiltrationType, on_delete=models.DO_NOTHING, related_name="filters", verbose_name=_("filtration type"), default=1)
    start_datetime = models.DateTimeField(verbose_name=_("start time"))
    end_datetime = models.DateTimeField(verbose_name=_("end time"), blank=True, null=True)
    filtration_volume_ml = models.FloatField(blank=True, null=True, verbose_name=_("volume (ml)"))
    storage_location = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("filter storage location"))
    filtration_ipc = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("filtration IPC"))
    comments = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("comments"))

    # calc
    duration_min = models.FloatField(verbose_name=_("filtration duration (min)"), blank=True, null=True, editable=False)
    order = models.IntegerField(verbose_name=_("order"), default=0)

    class Meta:
        ordering = ["filtration_batch", "order"]

    @property
    def is_filtration_blank(self):
        return not self.sample

    def __str__(self):
        mystr = f"f{self.id}"
        return mystr

    def save(self, *args, **kwargs):
        # if there is a sample, the collection is known
        if self.sample:
            self.collection = self.sample.collection

        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            self.duration_min = (delta.days * 24 * 60) + (delta.seconds / 60)

        super().save(*args, **kwargs)

    @property
    def display(self):
        return str(self)

    @property
    def pcrs(self):
        return PCR.objects.filter(extract__filter=self)

    @property
    def assays(self):
        return PCRAssay.objects.filter(pcr__extract__filter=self)

    @property
    def extract_count(self):
        return self.extracts.count()

    @property
    def pcr_count(self):
        return self.pcrs.count()

    @property
    def assay_count(self):
        return self.assays.count()

    @property
    def full_display(self):
        mystr = str(self)
        if self.tube_id:
            mystr += f" ({self.tube_id})"
        return mystr


class ExtractionBatch(Batch):
    class Meta:
        verbose_name_plural = _("DNA Extraction Batches")
        ordering = ["-datetime"]

    def __str__(self):
        return "{} {} ({})".format(_("DNA Extraction Batch"), self.id, self.datetime.strftime("%Y-%m-%d"))

    def get_absolute_url(self):
        return reverse('edna:extraction_batch_detail', kwargs={'pk': self.id})

    @property
    def extract_count(self):
        return self.extracts.count()


class DNAExtract(MetadataFields):
    """ the filter id of this table is effectively the tube id"""
    extraction_batch = models.ForeignKey(ExtractionBatch, related_name='extracts', on_delete=models.CASCADE, verbose_name=_("extraction batch"))
    filter = models.ForeignKey(Filter, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='extracts', verbose_name=_("filter ID"))
    # see save method
    sample = models.ForeignKey(Sample, related_name='extracts', on_delete=models.DO_NOTHING, verbose_name=_("sample ID"), blank=True, null=True)
    collection = models.ForeignKey(Collection, related_name='extracts', on_delete=models.DO_NOTHING, verbose_name=_("project"), blank=True, null=True)
    extraction_number = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("extraction number"), unique=True)
    start_datetime = models.DateTimeField(verbose_name=_("extraction date/time"))
    dna_extraction_protocol = models.ForeignKey(DNAExtractionProtocol, on_delete=models.DO_NOTHING, verbose_name=_("extraction protocol"))
    storage_location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("DNA storage location"))
    extraction_plate_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("extraction plate ID"))
    extraction_plate_well = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("extraction plate well"))
    extraction_ipc = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("extraction IPC"))
    comments = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("comments"))

    # calc
    order = models.IntegerField(verbose_name=_("order"), default=0)

    def save(self, *args, **kwargs):
        # if there is a filter, the collection is known
        if self.filter:
            self.collection = self.filter.collection
            # if the filter has a sample, we must make sure that the extraction sample is the same
            if self.filter.sample:
                self.sample = self.filter.sample
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["extraction_batch", "order", "id"]

    @property
    def is_extraction_blank(self):
        return not self.sample and not self.filter

    def __str__(self):
        mystr = f"x{self.id}"
        # if there is no sample or filter associated with this extract, it is an extraction blank
        # if not self.sample and not self.filter:
        #     mystr += " (extraction blank)"
        return mystr

    @property
    def display(self):
        return str(self)

    @property
    def assays(self):
        return PCRAssay.objects.filter(pcr__extract=self)

    @property
    def pcr_count(self):
        return self.pcrs.count()

    @property
    def assay_count(self):
        return self.assays.count()

    @property
    def full_display(self):
        mystr = str(self)
        if self.extraction_number:
            mystr += f" | b{self.extraction_number}"
        return mystr


class PCRBatch(Batch):
    control_status_choices = (
        (1, _("OK")),
        (0, _("Bad")),
    )
    default_collection = models.ManyToManyField(Collection, verbose_name=_("project(s)"))
    plate_id = models.CharField(max_length=25, blank=True, null=True, verbose_name=_(" qPCR plate ID"))
    machine_number = models.CharField(max_length=25, blank=True, null=True, verbose_name=_(" qPCR machine number"))
    run_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(" qPCR run program"))
    control_status = models.IntegerField(blank=True, null=True, choices=control_status_choices, verbose_name=_("control status"))

    class Meta:
        verbose_name_plural = _("PCR Batches")
        ordering = ["-datetime"]

    def __str__(self):
        return "{} {} ({})".format(_("PCR Batch"), self.id, self.datetime.strftime("%Y-%m-%d"))

    def get_absolute_url(self):
        return reverse('edna:pcr_batch_detail', kwargs={'pk': self.id})

    @property
    def pcr_count(self):
        return self.pcrs.count()

    @property
    def default_collection_list(self):
        return [{'id':obj.id, 'name':obj.name } for obj in self.default_collection.all()]

class PCR(MetadataFields):
    """ the filter id of this table is effectively the tube id"""
    pcr_batch = models.ForeignKey(PCRBatch, related_name='pcrs', on_delete=models.CASCADE, verbose_name=_(" qPCR batch"))
    extract = models.ForeignKey(DNAExtract, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="pcrs", verbose_name=_("extraction ID"))
    collection = models.ForeignKey(Collection, related_name='pcrs', on_delete=models.DO_NOTHING, verbose_name=_("project"), blank=True, null=True)
    pcr_plate_well = models.CharField(max_length=25, blank=True, null=True, verbose_name=_(" qPCR plate well"))
    master_mix = models.ForeignKey(MasterMix, on_delete=models.DO_NOTHING, related_name="pcrs", verbose_name=_("master mix"), blank=False, null=True)

    # calc
    pcr_plate_well_prefix = models.CharField(max_length=1, blank=True, null=True, editable=True)
    pcr_plate_well_suffix = models.IntegerField(blank=True, null=True, editable=True)

    def save(self, *args, **kwargs):
        # if there is a filter, the collection is known
        if self.extract:
            self.collection = self.extract.collection
        if self.pcr_plate_well:
            self.pcr_plate_well_prefix = self.pcr_plate_well[0]
            self.pcr_plate_well_suffix = self.pcr_plate_well[1:]

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["pcr_plate_well_prefix", "pcr_plate_well_suffix", "pcr_batch", "extract__id", "id"]

    def __str__(self):
        return f"q{self.id}"

    @property
    def display(self):
        return str(self)

    @property
    def sample(self):
        if self.extract and self.extract.filter:
            return self.extract.filter.sample

    @property
    def filter(self):
        if self.extract:
            return self.extract.filter

    @property
    def assay_count(self):
        return self.assays.count()


class PCRAssay(MetadataFields):
    result_choices = (
        (8, _("in progress")),
        (1, _("positive")),
        (0, _("negative")),
        (90, _("no assay :(")),
        (91, _("LOD missing :(")),
    )

    pcr = models.ForeignKey(PCR, related_name='assays', on_delete=models.CASCADE, verbose_name=_("PCR"))
    assay = models.ForeignKey(Assay, related_name='pcrs', on_delete=models.DO_NOTHING, verbose_name=_("assay"), blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True, verbose_name=_("threshold"))
    ct = models.FloatField(blank=True, null=True, verbose_name=_("Ct"))
    is_undetermined = models.BooleanField(default=False, verbose_name=_("Undetermined?"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"))

    # calculated
    result = models.IntegerField(verbose_name=_("result"), choices=result_choices, default=8, editable=False)
    edna_conc = models.FloatField(blank=True, null=True, verbose_name=_(" eDNA concentration (Pg/L)"), editable=False)

    class Meta:
        ordering = ["pcr", "assay"]
        unique_together = (("pcr", "assay"),)

    def save(self, *args, **kwargs):
        if self.is_undetermined:
            self.result = 0
        elif self.ct:
            if not self.assay:
                self.result = 90
            elif not self.assay.lod:
                self.result = 91
            else:
                if self.ct <= self.assay.lod:
                    self.result = 1
                else:
                    self.result = 0
            if self.assay and self.assay.a_coef and self.assay.b_coef:
                self.edna_conc = self.assay.b_coef * math.log(self.ct) + self.assay.a_coef
        else:
            self.result = 8

        super().save(*args, **kwargs)
