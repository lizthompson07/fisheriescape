from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth
from django.core.validators import MaxValueValidator, MinValueValidator
import misaka
import os


# Create your models here.
class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('grais:person_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['first_name', 'last_name']

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class Province(models.Model):
    province = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.province, self.abbrev)


class Station(models.Model):
    station_name = models.CharField(max_length=255, blank=True, null=True)
    province = models.ForeignKey('Province', on_delete=models.DO_NOTHING, related_name='stations', blank=True,
                                 null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    depth = models.FloatField(blank=True, null=True)
    site_desc = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.station_name, self.province.abbrev)

    def get_absolute_url(self):
        return reverse('grais:station_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['province', 'station_name']


class Species(models.Model):
    common_name = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    color_morph = models.BooleanField(verbose_name="Has color morph")
    invasive = models.BooleanField()
    biofouling = models.BooleanField()
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.common_name

    class Meta:
        ordering = ['common_name']

    def get_absolute_url(self):
        return reverse('grais:species_detail', kwargs={'pk': self.id})


class Collector(models.Model):
    tag_number = models.CharField(max_length=55, unique=True)

    def __str__(self):
        return "{}".format(self.tag_number)

    def get_absolute_url(self):
        return reverse('grais:collector_detail', kwargs={'pk': self.id})


class Sample(models.Model):
    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    date_deployed = models.DateTimeField()
    date_retrieved = models.DateTimeField(blank=True, null=True)
    days_deployed = models.IntegerField(blank=True, null=True)
    sampler = models.ForeignKey(Sampler, on_delete=models.DO_NOTHING, related_name='samples')
    # notes = models.TextField(blank=True, null=True)
    # notes_html = models.TextField(blank=True, null=True)
    # date_created = models.DateTimeField(blank=True, null=True, default=timezone.now)
    season = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.season = self.date_deployed.year
        self.notes_html = misaka.html(self.notes)
        if self.date_retrieved != None:
            self.days_deployed = (self.date_retrieved - self.date_deployed).days
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('grais:sample_detail', kwargs={'pk': self.id})

    def __str__(self):
        return "Sample number {} @ {}".format(self.id, self.station)

    @property
    def weeks_deployed(self):
        if self.days_deployed != None:
            return str(round(self.days_deployed / 7, 2))
        else:
            return None

    class Meta:
        ordering = ['-season', 'station', '-date_deployed']


class Note(models.Model):
    sample = models.ForeignKey(Sample, related_name='notes', on_delete=models.DO_NOTHING)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)
    note = models.TextField()

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-date"]


class Line(models.Model):
    sample = models.ForeignKey(Sample, related_name='lines', on_delete=models.DO_NOTHING)
    collector = models.ForeignKey(Collector, related_name='lines', on_delete=models.DO_NOTHING, blank=True, null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('grais:line_detail', kwargs={'sample': self.sample.id, 'pk': self.id})


def img_file_name(instance, filename):
    img_name = 'grais/sample_{}/{}'.format(instance.line.sample.id, filename)
    return img_name


class Surface(models.Model):
    # Choices for surface_type
    PETRI = 'pe'
    PLATE = 'pl'
    SURFACE_TYPE_CHOICES = (
        (PETRI, 'Petri dish'),
        (PLATE, 'Plate'),
    )

    line = models.ForeignKey(Line, related_name='surfaces', on_delete=models.DO_NOTHING)
    surface_type = models.CharField(max_length=2, choices=SURFACE_TYPE_CHOICES)
    label = models.IntegerField()
    image = models.ImageField(blank=True, null=True, upload_to=img_file_name)
    notes = models.TextField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='SurfaceSpecies')
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('grais:surface_detail', kwargs={
            'sample': self.line.sample.id,
            'line': self.line.id,
            'pk': self.id
        })

    def __str__(self):
        return "surface #{}".format(self.id)

    class Meta:
        ordering = ['line', 'surface_type', 'label']


class SurfaceSpecies(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="surface_spp")
    surface = models.ForeignKey(Surface, on_delete=models.DO_NOTHING, related_name="surface_spp")
    percent_coverage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    notes = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        unique_together = (('species', 'surface'),)

    def get_absolute_url(self):
        return reverse('grais:surface_spp_detail_pop', kwargs={
            'sample': self.surface.line.sample.id,
            'line': self.surface.line.id,
            'surface': self.surface.id,
            'pk': self.id,
        })


class Probe(models.Model):
    probe_name = models.CharField(max_length=255)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.probe_name


class ProbeMeasurement(models.Model):
    # Choices for tide_descriptor
    EBB = 'eb'
    FLOOD = 'fl'
    HIGH = 'hi'
    LOW = 'lo'
    TIDE_DESCRIPTOR_CHOICES = (
        (EBB, 'Ebb'),
        (FLOOD, 'Flood'),
        (HIGH, 'High'),
        (LOW, 'Low'),
    )
    sample = models.ForeignKey(Sample, on_delete=models.DO_NOTHING, related_name="probe_data")
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING)
    time_date = models.DateTimeField(blank=True, null=True)
    tide_descriptor = models.CharField(max_length=2, choices=TIDE_DESCRIPTOR_CHOICES, blank=True, null=True)
    probe_depth = models.FloatField(blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True)
    sal_ppt = models.FloatField(blank=True, null=True)
    o2_percent = models.FloatField(blank=True, null=True)
    o2_mgl = models.FloatField(blank=True, null=True)
    sp_cond_ms = models.FloatField(blank=True, null=True)
    spc_ms = models.FloatField(blank=True, null=True)
    ph = models.FloatField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.time_date

    def get_absolute_url(self):
        return reverse("grais:probe_measurement_detail", kwargs={'sample': self.sample.id, "pk": self.id})


# def img_file_name(instance, filename):
#     file_ext = str(filename).split(".")[1]
#     img_name = 'sample_{sample}/surface_{id}.{file_ext}'.format(
#         sample=instance.sample.id,
#         id=instance.id,
#         file_ext=file_ext
#         )
#     fullname = os.path.join(settings.MEDIA_ROOT, img_name)
#     if os.path.exists(fullname):
#         os.remove(fullname)
#     return img_name

class IncidentalReport(models.Model):
    # Choices for report_type
    PHONE = 1
    EMAIL = 2
    REPORT_TYPE_CHOICES = (
        (PHONE, 'Telephone hotline'),
        (EMAIL, 'E-mail'),
    )

    # Choices for language
    ENG = 1
    FRE = 2
    LANGUAGE_CHOICES = (
        (ENG, 'English'),
        (FRE, 'French'),
    )

    # Choices for observation_type
    SINGLE = 1
    ONGOING = 2
    OBSERVATION_TYPE_CHOICES = (
        (SINGLE, 'Single observation'),
        (ONGOING, 'Ongoing presence'),
    )

    report_date = models.DateTimeField()
    reporter_name = models.CharField(max_length=150)
    report_type = models.IntegerField(choices=REPORT_TYPE_CHOICES)
    language_of_report = models.IntegerField(choices=LANGUAGE_CHOICES)
    call_answered_by = models.CharField(max_length=150, null=True, blank=True)
    call_returned_by = models.CharField(max_length=150, null=True, blank=True)
    location_description = models.CharField(max_length=500, null=True, blank=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    specimens_retained = models.NullBooleanField(blank=True, null=True)
    sighting_description = models.TextField(null=True, blank=True)
    identified_by = models.CharField(max_length=150, null=True, blank=True)
    date_of_occurence = models.DateTimeField()
    obvservation_type = models.IntegerField(choices=OBSERVATION_TYPE_CHOICES)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    season = models.IntegerField()
    date_last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def save(self):
        self.season = self.report_date.year
        self.date_last_modified = timezone.now()
        return super().save()

    def get_absolute_url(self):
        return reverse("grais:report_detail", kwargs={"pk":self.pk})

    def __str__(self):
        return "Incidental Report #{}".format(self.id)

    class Meta:
        ordering = ["-report_date"]
        
# TODO: create another model for report species... should have "confirmed" attribute
# TODO: create followup model
