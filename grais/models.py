from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    organization = models.CharField(max_length=1000, blank=True, null=True)

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
        return "{}".format(self.station_name)

    def get_absolute_url(self):
        return reverse('grais:station_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['province', 'station_name']


class Species(models.Model):
    # choices for epibiont_type
    UNK = None
    SES = 'ses'
    MOB = 'mob'
    EPIBIONT_TYPE_CHOICES = (
        (UNK, "-----"),
        (SES, "sessile"),
        (MOB, "mobile"),
    )


    common_name = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True, verbose_name="abbreviation")
    epibiont_type = models.CharField(max_length=10, blank=True, null=True, choices=EPIBIONT_TYPE_CHOICES)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="Taxonomic Serial Number")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    color_morph = models.BooleanField(verbose_name="Has color morph")
    invasive = models.BooleanField(verbose_name="is invasive?")
    # biofouling = models.BooleanField()
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.common_name

    class Meta:
        ordering = ['common_name']

    def get_absolute_url(self):
        return reverse('grais:species_detail', kwargs={'pk': self.id})


class Sample(models.Model):
    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    date_deployed = models.DateTimeField()
    date_retrieved = models.DateTimeField(blank=True, null=True)
    days_deployed = models.IntegerField(blank=True, null=True)
    # sampler = models.ForeignKey(Sampler, on_delete=models.DO_NOTHING, related_name='samples')
    samplers = models.ManyToManyField(Sampler)
    # notes = models.TextField(blank=True, null=True)
    # notes_html = models.TextField(blank=True, null=True)
    # date_created = models.DateTimeField(blank=True, null=True, default=timezone.now)
    old_id = models.IntegerField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='SampleSpecies')
    season = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.season = self.date_deployed.year
        if self.date_retrieved != None:
            self.days_deployed = (self.date_retrieved - self.date_deployed).days
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('grais:sample_detail', kwargs={'pk': self.id})

    def __str__(self):
        return "Sample {}".format(self.id)

    @property
    def weeks_deployed(self):
        if self.days_deployed != None:
            return str(round(self.days_deployed / 7, 2))
        else:
            return None

    class Meta:
        ordering = ['-season', 'station', '-date_deployed']


class SampleSpecies(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="sample_spp")
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="sample_spp")
    observation_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('species', 'sample'),)




class SampleNote(models.Model):
    sample = models.ForeignKey(Sample, related_name='notes', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)
    note = models.TextField()

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('grais:sample_detail', kwargs={'pk': self.sample.id,})

    class Meta:
        ordering = ["-date"]


class Line(models.Model):
    sample = models.ForeignKey(Sample, related_name='lines', on_delete=models.CASCADE)
    collector = models.CharField(max_length=56, blank=True, null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='LineSpecies')
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        if self.collector:
            my_str = "Collector {}".format(self.collector)
        else:
            my_str = "Line {} (missing collector number)".format(self.id)

        return my_str

    def get_absolute_url(self):
        return reverse('grais:line_detail', kwargs={'pk': self.id})


def img_file_name(instance, filename):
    img_name = 'grais/sample_{}/{}'.format(instance.line.sample.id, filename)
    return img_name


class LineSpecies(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="line_spp")
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="line_spp")
    observation_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('species', 'line'),)


class Surface(models.Model):
    # Choices for surface_type
    PETRI = 'pe'
    PLATE = 'pl'
    SURFACE_TYPE_CHOICES = (
        (PETRI, 'Petri dish'),
        (PLATE, 'Plate'),
    )

    line = models.ForeignKey(Line, related_name='surfaces', on_delete=models.CASCADE)
    surface_type = models.CharField(max_length=2, choices=SURFACE_TYPE_CHOICES)
    label = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True, upload_to=img_file_name)
    notes = models.TextField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='SurfaceSpecies')
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('grais:surface_detail', kwargs={
            'pk': self.id
        })

    def __str__(self):
        if self.label:
            my_str = "{}".format(self.label)
        else:
            my_str = "Surface {} (missing label)".format(self.id)

        return my_str

    class Meta:
        ordering = ['line', 'surface_type', 'label']


class SurfaceSpecies(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="surface_spp")
    surface = models.ForeignKey(Surface, on_delete=models.CASCADE, related_name="surface_spp")
    percent_coverage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    notes = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        unique_together = (('species', 'surface'),)

    def get_absolute_url(self):
        return reverse('grais:surface_spp_detail_pop', kwargs={
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

    # Choices for timezone
    AST = 'AST'
    ADT = 'ADT'
    UTC = 'UTC'
    TIMEZONE_CHOICES = (
        (AST, 'AST'),
        (ADT, 'ADT'),
        (UTC, 'UTC'),
    )

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="probe_data")
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING)
    time_date = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=5, choices=TIMEZONE_CHOICES, blank=True, null=True)
    tide_descriptor = models.CharField(max_length=2, choices=TIDE_DESCRIPTOR_CHOICES, blank=True, null=True)
    probe_depth = models.FloatField(blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True)
    sal_ppt = models.FloatField(blank=True, null=True)
    o2_percent = models.FloatField(blank=True, null=True)
    o2_mgl = models.FloatField(blank=True, null=True)
    sp_cond_ms = models.FloatField(blank=True, null=True)
    spc_ms = models.FloatField(blank=True, null=True)
    ph = models.FloatField(blank=True, null=True)
    turbidiy = models.FloatField(blank=True, null=True)
    weather_notes = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.time_date

    def get_absolute_url(self):
        return reverse("grais:probe_measurement_detail", kwargs={"pk": self.id})


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
    # Choices for report_source
    PHONE = 1
    INVADERS_EMAIL = 2
    PERS_EMAIL = 3

    REPORT_SOURCE_CHOICES = (
        (PHONE, 'Gulf AIS Hotline'),
        (INVADERS_EMAIL, 'Gulf Invaders E-mail'),
        (PERS_EMAIL, 'Personal E-mail'),
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

    # Choices for requestor

    PUB = 1
    ACAD = 2
    PRIV = 3
    PROV = 4
    FED = 5
    REQUESTOR_TYPE_CHOICES = (
        (PUB,"public"),
        (ACAD,"academia"),
        (PRIV,"private sector"),
        (PROV,"provincial government"),
        (FED,"federal government"),
    )

    # basic details
    species = models.ManyToManyField(Species, verbose_name="Concerning which species")
    report_date = models.DateTimeField(default=timezone.now)
    language_of_report = models.IntegerField(choices=LANGUAGE_CHOICES)
    requestor_name = models.CharField(max_length=150)
    requestor_type = models.IntegerField(choices=REQUESTOR_TYPE_CHOICES, blank=True, null=True)
    report_source = models.IntegerField(choices=REPORT_SOURCE_CHOICES)
    species_confirmation = models.NullBooleanField(blank=True, null=True)
    gulf_ais_confirmed = models.NullBooleanField(blank=True, null=True)
    seeking_general_info_ais = models.NullBooleanField(blank=True, null=True)
    seeking_general_info_non_ais = models.NullBooleanField(blank=True, null=True)
    management_related = models.NullBooleanField(blank=True, null=True)
    dfo_it_related = models.NullBooleanField(blank=True, null=True)
    incorrect_region = models.NullBooleanField(blank=True, null=True)

    # sighting details
    call_answered_by = models.CharField(max_length=150, null=True, blank=True)
    call_returned_by = models.CharField(max_length=150, null=True, blank=True)
    location_description = models.CharField(max_length=500, null=True, blank=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    specimens_retained = models.NullBooleanField(blank=True, null=True)
    sighting_description = models.TextField(null=True, blank=True)
    identified_by = models.CharField(max_length=150, null=True, blank=True)
    date_of_occurrence = models.DateTimeField()
    observation_type = models.IntegerField(choices=OBSERVATION_TYPE_CHOICES)
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
        

