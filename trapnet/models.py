from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import MetadataFields, SimpleLookup


class CodeModel(SimpleLookup):
    code = models.CharField(max_length=5, blank=True, null=True, unique=True)

    @property
    def choice(self):
        return f"{self.code} - {self.tname}"

    class Meta:
        ordering = ['code', ]
        abstract = True


class RiverSite(MetadataFields):
    name = models.CharField(max_length=255, verbose_name=_("site name"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='river_sites', blank=False, null=True)
    stream_order = models.IntegerField(blank=True, null=True)
    elevation_m = models.FloatField(blank=True, null=True, verbose_name=_("elevation (m)"))
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    epsg_id = models.CharField(max_length=255, blank=True, null=True)
    coordinate_resolution = models.FloatField(blank=True, null=True)
    coordinate_precision = models.FloatField(blank=True, null=True)
    coordinate_accuracy = models.FloatField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    exclude_data_from_site = models.BooleanField(default=False, verbose_name=_("Exclude all data from this site?"))

    # non-editable
    river = models.ForeignKey(shared_models.River, on_delete=models.DO_NOTHING, related_name='river_sites', blank=True, null=True, editable=False)

    def __str__(self):
        try:
            return "{} ({})".format(self.name, self.river.name)
        except AttributeError:
            return "{}".format(self.name)

    class Meta:
        ordering = ['river', 'name']


class LifeStage(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Species(MetadataFields):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    life_stage = models.ForeignKey(LifeStage, related_name='species', on_delete=models.DO_NOTHING, blank=True, null=True)
    abbrev = models.CharField(max_length=10, verbose_name="abbreviation", unique=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    notes = models.TextField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_spp_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_spp_updated_by')

    def __str__(self):
        my_str = getattr(self, str(_("common_name_eng")))
        if self.life_stage:
            my_str += " ({})".format(self.life_stage)
        return my_str

    @property
    def full_name(self):
        return str(self)

    @property
    def search_name(self):
        return f"{self.full_name} / {self.scientific_name} ({self.code})"

    class Meta:
        ordering = ['common_name_eng']
        verbose_name_plural = _("species")

    def get_absolute_url(self):
        return reverse("trapnet:species_detail", kwargs={"pk": self.id})


class SampleType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Sample(MetadataFields):
    wind_speed_choices = (
        (1, _("no wind")),
        (2, _("calm / slight wind")),
        (3, _("light wind")),
        (4, _("moderate wind")),
        (5, _("heavy wind")),
        (6, _("variable")),
    )
    wind_direction_choices = (
        (1, _("north")),
        (2, _("northeast")),
        (3, _("east")),
        (4, _("southeast")),
        (5, _("south")),
        (6, _("southwest")),
        (7, _("west")),
        (8, _("northwest")),
    )
    precipitation_category_choices = (
        (1, _("no precipitation")),
        (2, _("mist")),
        (3, _("light rain")),
        (4, _("moderate rain")),
        (5, _("heavy rain")),
        (6, _("intermittent")),
        (7, _("flurries")),
    )
    operating_condition_choices = (
        (1, _("fully operational")),
        (2, _("partially operational")),
        (3, _("not operational")),
    )

    site = models.ForeignKey(RiverSite, related_name='samples', on_delete=models.DO_NOTHING)
    sample_type = models.ForeignKey(SampleType, related_name='samples', on_delete=models.DO_NOTHING)
    arrival_date = models.DateTimeField(verbose_name="arrival date/time")
    departure_date = models.DateTimeField(verbose_name="departure date/time")
    samplers = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    season = models.IntegerField(null=True, blank=True)

    # temp/climate data
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)")
    min_air_temp = models.FloatField(null=True, blank=True, verbose_name="minimum air temperature (°C)")
    max_air_temp = models.FloatField(null=True, blank=True, verbose_name="maximum air temperature (°C)")
    percent_cloud_cover = models.FloatField(null=True, blank=True, verbose_name="cloud cover (0-1)", validators=[MinValueValidator(0), MaxValueValidator(1)])
    precipitation_category = models.IntegerField(blank=True, null=True, choices=precipitation_category_choices)
    precipitation_comment = models.CharField(max_length=255, blank=True, null=True)
    wind_speed = models.IntegerField(blank=True, null=True, choices=wind_speed_choices)
    wind_direction = models.IntegerField(blank=True, null=True, choices=wind_direction_choices)

    # water data
    water_depth_m = models.FloatField(null=True, blank=True, verbose_name="water depth (m)")
    water_level_delta_m = models.FloatField(null=True, blank=True, verbose_name="water level delta (m)")
    discharge_m3_sec = models.FloatField(null=True, blank=True, verbose_name="discharge (m3/s)")
    water_temp_shore_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at shore (°C)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at trap (°C)")

    # smolt wheel
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="RPM at start")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="RPM at end")
    operating_condition = models.IntegerField(blank=True, null=True, choices=operating_condition_choices)
    operating_condition_comment = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_updated_by')

    @property
    def duration(self):
        diff = self.departure_date - self.arrival_date
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours} hours, {minutes} minutes"

    @property
    def species_list(self):
        my_list = list(set([str(obs.species) for obs in self.entries.all()]))
        my_list.sort()
        return mark_safe(listrify(my_list, "<br>"))

    def save(self, *args, **kwargs):
        self.season = self.arrival_date.year
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-arrival_date', ]
        # unique_together = [["start_date", "station"], ]

    def get_absolute_url(self):
        return reverse("trapnet:sample_detail", kwargs={"pk": self.id})

    def __str__(self):
        return "Sample {}".format(self.id)

    @property
    def arrival_departure(self):
        return mark_safe(_("{arrival} &rarr; {departure} ({duration})").format(
            arrival=self.arrival_date.strftime("%Y-%m-%d %H:%M"),
            departure=self.departure_date.strftime("%Y-%m-%d %H:%M"),
            duration=self.duration,
        ))

    @property
    def air_temp(self):
        return _("<u>arrival:</u> {arrival}; <u>max:</u> {max} <u>min:</u> {min}").format(
            arrival=nz(self.air_temp_arrival, "---"),
            max=nz(self.max_air_temp, "---"),
            min=nz(self.min_air_temp, "---"),
        )

    @property
    def water(self):
        return mark_safe(_("<u>depth (m):</u> {depth}&plusmn;{delta}; <u>discharge (m<sup>3</sup>/s):</u> {dischard}").format(
            depth=nz(self.water_depth_m, "---"),
            delta=nz(self.water_level_delta_m, "---"),
            dischard=nz(self.discharge_m3_sec, "---"),
        ))

    @property
    def rpms(self):
        return mark_safe(_("<u>@start (m):</u> {start}; <u>@end:</u> {end}").format(
            start=nz(self.rpm_arrival, "---"),
            end=nz(self.rpm_departure, "---"),
        ))

    @property
    def wind(self):
        return _("<u>speed:</u> {speed}; <u>direction:</u> {dir}").format(
            speed=nz(self.get_wind_speed_display(), "---"),
            dir=nz(self.get_wind_direction_display(), "---"),
        )

    @property
    def water_temp(self):
        return _("<u>@shore:</u> {shore} <u>@trap:</u> {trap}").format(
            shore=nz(self.water_temp_shore_c, "---"),
            trap=nz(self.water_temp_trap_c, "---"),
        )


class Origin(CodeModel):
    pass


class Status(CodeModel):
    pass


class Sex(CodeModel):
    pass


class Entry(MetadataFields):
    first_tag = models.CharField(max_length=50, blank=True, null=True)
    last_tag = models.CharField(max_length=50, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="entries")
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="entries", blank=True, null=True)
    frequency = models.IntegerField(blank=True, null=True, verbose_name=_("frequency"))
    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))
    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="entries", blank=True, null=True)
    smolt_age = models.IntegerField(blank=True, null=True)
    location_tagged = models.CharField(max_length=500, blank=True, null=True)
    date_tagged = models.DateTimeField(blank=True, null=True, verbose_name="date tagged")
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"))
    tags_removed = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # non-editable
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="entries", editable=False)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="entries", editable=False)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "entries"


class Observation(MetadataFields):
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="observations")
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)
    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))
    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    age = models.IntegerField(blank=True, null=True, verbose_name=_("age"))
    location_tagged = models.CharField(max_length=500, blank=True, null=True)
    date_tagged = models.DateTimeField(blank=True, null=True, verbose_name="date tagged")
    tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"), unique=True)
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"))
    tags_removed = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observations")
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="observations")

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
