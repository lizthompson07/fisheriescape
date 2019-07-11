from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from lib.functions.custom_functions import nz
from shared_models import models as shared_models


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


class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    sav = models.BooleanField(default=False, verbose_name="Submerged aquatic vegetation (SAV)")
    ais = models.BooleanField(default=False, verbose_name="Aquatic invasive species")
    notes = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.common_name_eng

    class Meta:
        ordering = ['common_name_eng']

    def get_absolute_url(self):
        return reverse("camp:species_detail", kwargs={"pk": self.id})


class Trap(models.Model):
    # Choices for turbidity
    TURBID = 1
    CLEAR = 2
    TURBIDITY_CHOICES = (
        (TURBID, "Turbid"),
        (CLEAR, "Clear"),
    )

    # choice for tide_state
    LOW = 'l'
    MID = 'm'
    HIGH = 'h'
    TIDE_STATE_CHOICES = (
        (HIGH, "High"),
        (MID, "Mid"),
        (LOW, "Low"),
    )

    # choice for tide_direction
    INCOMING = 'in'
    OUTGOING = 'out'
    TIDE_DIR_CHOICES = (
        (INCOMING, "Incoming"),
        (OUTGOING, "Outgoing"),
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

    river = models.ForeignKey(shared_models.River, related_name='wheel_samples', on_delete=models.DO_NOTHING)
    arrival_date = models.DateTimeField(verbose_name="arrival")
    departure_date = models.DateTimeField(blank=True, null=True, verbose_name="departure")
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="Water temperature (°C)")
    max_air_temp = models.FloatField(null=True, blank=True, verbose_name="Water temperature (°C)")
    percent_cloud_cover = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    wind_speed = models.IntegerField(choices=TURBIDITY_CHOICES, blank=True, null=True)
    wind_direction = models.IntegerField(choices=TURBIDITY_CHOICES, blank=True, null=True)
    precipitation_category = models.IntegerField(choices=TURBIDITY_CHOICES, blank=True, null=True)
    precipitation_comment = models.CharField(max_length=255, blank=True, null=True)
    water_depth_m = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_level_delta_m = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    discharge_m3_sec = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_temp_shore_c = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    operating_condition = models.ForeignKey("x", related_name='samples', on_delete=models.DO_NOTHING)
    notes = models.TextField(blank=True, null=True)
    season = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"),
                                         related_name="wheel_sample_last_modified_by")
    samplers = models.ManyToManyField(Sampler, blank=True)

    def save(self, *args, **kwargs):
        self.year = self.arrival_date.year
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date', 'station']
        unique_together = [["start_date", "station"], ]

    def get_absolute_url(self):
        return reverse("camp:sample_detail", kwargs={"pk": self.id})

    def __str__(self):
        return "Sample {}".format(self.id)


# Origin
# Status

class Observation(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observations")
    trap = models.ForeignKey(Trap, on_delete=models.DO_NOTHING, related_name="observations")
    first_tag = models.CharField(max_length=50, blank=True, null=True)
    last_tag = models.CharField(max_length=50, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="observations")
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="observations")
    count = models.IntegerField(blank=True, null=True)
    fork_length = models.FloatField(blank=True, null=True)
    total_length = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="observations")
    smolt_age = models.IntegerField(blank=True, null=True)
    location_tagged = models.ForeignKey(shared_models.River, related_name='smolt_observations', on_delete=models.DO_NOTHING)
    date_tagged = models.DateTimeField(blank=True, null=True, verbose_name="departure")
    scale_id_number = models.CharField(max_length=50, blank=True, null=True)
    tags_removed = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = [["sample", "species"], ]
        # ordering = ["-sample__year"] THIS IS WAY TOO SLOW!
