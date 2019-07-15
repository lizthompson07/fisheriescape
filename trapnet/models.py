from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from lib.functions.custom_functions import nz
from shared_models import models as shared_models


class RiverSite(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("site name"))
    river = models.ForeignKey(shared_models.River, on_delete=models.DO_NOTHING, related_name='river_sites', blank=True, null=True)
    stream_order = models.IntegerField(blank=True, null=True)
    elevation_m = models.FloatField(blank=True, null=True, verbose_name=_("elevation (m)"))
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    epsg_id = models.CharField(max_length=255, blank=True, null=True)
    coordinate_resolution = models.FloatField(blank=True, null=True)
    coordinate_precision = models.FloatField(blank=True, null=True)
    coordinate_accuracy = models.FloatField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='river_sites', blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.province.tabbrev)

    class Meta:
        ordering = ['province', 'name']


class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    notes = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.common_name_eng

    class Meta:
        ordering = ['common_name_eng']

    def get_absolute_url(self):
        return reverse("camp:species_detail", kwargs={"pk": self.id})


class WindSpeed(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class WindDirection(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class PrecipitationCategory(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class OperatingCondition(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Trap(models.Model):
    site = models.ForeignKey(RiverSite, related_name='traps', on_delete=models.DO_NOTHING)
    arrival_date = models.DateTimeField(verbose_name="arrival")
    departure_date = models.DateTimeField(blank=True, null=True, verbose_name="departure")
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="Water temperature (°C)")
    max_air_temp = models.FloatField(null=True, blank=True, verbose_name="Water temperature (°C)")
    percent_cloud_cover = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    wind_speed = models.ForeignKey(WindSpeed, related_name='traps', on_delete=models.DO_NOTHING)
    wind_direction = models.ForeignKey(WindDirection, related_name='traps', on_delete=models.DO_NOTHING)
    precipitation_category = models.ForeignKey(PrecipitationCategory, related_name='traps', on_delete=models.DO_NOTHING)
    precipitation_comment = models.CharField(max_length=255, blank=True, null=True)
    water_depth_m = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_level_delta_m = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    discharge_m3_sec = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_temp_shore_c = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="Sand (%)")
    operating_condition = models.ForeignKey(OperatingCondition, related_name='traps', on_delete=models.DO_NOTHING)
    notes = models.TextField(blank=True, null=True)
    season = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"),
                                         related_name="wheel_sample_last_modified_by")
    samplers = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.year = self.arrival_date.year
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-arrival_date',]
        # unique_together = [["start_date", "station"], ]

    def get_absolute_url(self):
        return reverse("camp:sample_detail", kwargs={"pk": self.id})

    def __str__(self):
        return "Sample {}".format(self.id)


class Origin(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Status(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Sex(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Observation(models.Model):
    trap = models.ForeignKey(Trap, on_delete=models.CASCADE, related_name="observations")
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observations")
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
        unique_together = [["trap", "species"], ]
        # ordering = ["-sample__year"] THIS IS WAY TOO SLOW!
