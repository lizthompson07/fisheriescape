import os
import statistics

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext
from shapely.geometry import Point

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import MetadataFields, SimpleLookup
from shared_models.utils import remove_nulls


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
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    epsg_id = models.CharField(max_length=255, blank=True, null=True)
    coordinate_resolution = models.FloatField(blank=True, null=True)
    coordinate_precision = models.FloatField(blank=True, null=True)
    coordinate_accuracy = models.FloatField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    exclude_data_from_site = models.BooleanField(default=False, verbose_name=_("Exclude all data from this site?"))

    # non-editable
    river = models.ForeignKey(shared_models.River, on_delete=models.DO_NOTHING, related_name='sites', editable=False)

    def get_point(self):
        if self.latitude and self.longitude:
            return Point(self.latitude, self.longitude)

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


class Electrofisher(SimpleLookup):
    model_number = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.tname} (s/n: {nz(self.serial_number, '---')})"


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
    sample_type_choices = (
        (1, _("Rotary Screw Trap")),
        (2, _("Electrofishing")),
    )

    site = models.ForeignKey(RiverSite, related_name='samples', on_delete=models.DO_NOTHING)
    sample_type = models.IntegerField(choices=sample_type_choices)

    arrival_date = models.DateTimeField(verbose_name="arrival date/time")
    departure_date = models.DateTimeField(verbose_name="departure date/time")
    samplers = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    season = models.IntegerField(null=True, blank=True)
    # electro
    crew_probe = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (probe)"))
    crew_seine = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (seine)"))
    crew_dipnet = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (dipnet)"))
    crew_extras = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (extras)"))

    # site description
    percent_riffle = models.FloatField(blank=True, null=True, verbose_name=_("riffle"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_run = models.FloatField(blank=True, null=True, verbose_name=_("run"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_flat = models.FloatField(blank=True, null=True, verbose_name=_("flat"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_pool = models.FloatField(blank=True, null=True, verbose_name=_("pool"), validators=(MinValueValidator(0), MaxValueValidator(1)))

    bank_length_left = models.FloatField(null=True, blank=True, verbose_name=_("bank length - left (m)"))
    bank_length_right = models.FloatField(null=True, blank=True, verbose_name=_("bank length - right (m)"))
    width_lower = models.FloatField(null=True, blank=True, verbose_name=_("width - lower (m)"))
    depth_1_lower = models.IntegerField(null=True, blank=True, verbose_name=_("depth #1 - lower (cm)"))
    depth_2_lower = models.IntegerField(null=True, blank=True, verbose_name=_("depth #2 - lower (cm)"))
    depth_3_lower = models.IntegerField(null=True, blank=True, verbose_name=_("depth #3 - lower (cm)"))
    width_middle = models.FloatField(null=True, blank=True, verbose_name=_("width - middle (m)"))
    depth_1_middle = models.IntegerField(null=True, blank=True, verbose_name=_("depth #1 - middle (cm)"))
    depth_2_middle = models.IntegerField(null=True, blank=True, verbose_name=_("depth #2 - middle (cm)"))
    depth_3_middle = models.IntegerField(null=True, blank=True, verbose_name=_("depth #3 - middle (cm)"))
    width_upper = models.FloatField(null=True, blank=True, verbose_name=_("width - upper (m)"))
    depth_1_upper = models.IntegerField(null=True, blank=True, verbose_name=_("depth #1 - upper (cm)"))
    depth_2_upper = models.IntegerField(null=True, blank=True, verbose_name=_("depth #2 - upper (cm)"))
    depth_3_upper = models.IntegerField(null=True, blank=True, verbose_name=_("depth #3 - upper (cm)"))

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
    water_temp_c = models.FloatField(null=True, blank=True, verbose_name="water temperature (°C)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at trap (°C)")
    water_cond = models.FloatField(null=True, blank=True, verbose_name="specific conductivity (µS)",
                                   help_text=_("The measurement is to 1 decimal place in micro siemens (µS)"))
    overhanging_veg_left = models.IntegerField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Left"))
    overhanging_veg_right = models.IntegerField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Right"))
    max_overhanging_veg_left = models.IntegerField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Left"))
    max_overhanging_veg_right = models.IntegerField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Right"))

    # substrate
    percent_fine = models.FloatField(blank=True, null=True, verbose_name=_("fine silt or clay"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_sand = models.FloatField(blank=True, null=True, verbose_name=_("sand"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_gravel = models.FloatField(blank=True, null=True, verbose_name=_("gravel"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_pebble = models.FloatField(blank=True, null=True, verbose_name=_("pebble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_cobble = models.FloatField(blank=True, null=True, verbose_name=_("cobble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_rocks = models.FloatField(blank=True, null=True, verbose_name=_("rocks"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_boulder = models.FloatField(blank=True, null=True, verbose_name=_("boulder"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_bedrock = models.FloatField(blank=True, null=True, verbose_name=_("bedrock"), validators=(MinValueValidator(0), MaxValueValidator(1)))

    # rst
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="RPM at start")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="RPM at end")
    operating_condition = models.IntegerField(blank=True, null=True, choices=operating_condition_choices)
    operating_condition_comment = models.CharField(max_length=255, blank=True, null=True)

    electrofisher = models.ForeignKey(Electrofisher, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("electrofisher"), blank=True,
                                      null=True)
    electrofisher_voltage = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher voltage (V)"))
    electrofisher_output = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher output (amps)"))
    electrofisher_frequency = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher frequency (Hz)"))

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_updated_by')

    @property
    def full_wetted_width(self):
        """
        Full wetted width:
        (average of the left and right bank lengths)    X    (average of the lower, middle, and upper stream widths)
        """
        errors = list()
        if not self.bank_length_left:
            errors.append("missing left bank length")
        if not self.bank_length_right:
            errors.append("missing right bank length")
        if not self.width_lower:
            errors.append("missing lower stream width")
        if not self.width_middle:
            errors.append("missing middle stream width")
        if not self.width_upper:
            errors.append("missing upper stream width")
        if len(errors):
            return mark_safe(f"<em class='text-muted'>{listrify(errors)}</em>")
        else:
            return statistics.mean([self.bank_length_left, self.bank_length_right]) * statistics.mean(
                [self.width_lower, self.width_middle, self.width_upper])

    @property
    def substrate_profile(self):
        my_str = ""
        substrates = [
            "fine",
            "sand",
            "gravel",
            "pebble",
            "cobble",
            "rocks",
            "boulder",
            "bedrock",
        ]
        substrates_string = [
            gettext("fine"),
            gettext("sand"),
            gettext("gravel"),
            gettext("pebble"),
            gettext("cobble"),
            gettext("rocks"),
            gettext("boulder"),
            gettext("bedrock"),
        ]
        for substrate in substrates:
            attr = getattr(self, f"percent_{substrate}")
            substrate = gettext(substrate)
            if attr and attr > 0:
                my_str += f"{int(attr * 100)}% {substrate}<br> "
        return mark_safe(my_str)

    def get_avg_depth(self, which_depth):
        d1 = getattr(self, f"depth_1_{which_depth}")
        d2 = getattr(self, f"depth_2_{which_depth}")
        d3 = getattr(self, f"depth_3_{which_depth}")
        depths = [d1, d2, d3]
        remove_nulls(depths)
        if len(depths):
            return round(statistics.mean(depths), 3)

    @property
    def site_profile(self):
        my_str = ""
        substrates = [
            "riffle",
            "run",
            "flat",
            "pool",
        ]
        substrates_string = [
            gettext("riffle"),
            gettext("run"),
            gettext("flat"),
            gettext("pool"),
        ]
        for substrate in substrates:
            attr = getattr(self, f"percent_{substrate}")
            substrate = gettext(substrate)
            if attr and attr > 0:
                my_str += f"{int(attr * 100)}% {substrate}<br> "
        return mark_safe(my_str)

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
        spp = Species.objects.filter(Q(observations__sample=self) | Q(observations__sweep__sample=self)).distinct()
        my_list = list([f"{sp} ({sp.observations.filter(Q(sample=self) | Q(sweep__sample=self)).count()})" for sp in spp])
        my_list.sort()
        return mark_safe(listrify(my_list, "<br>"))

    @property
    def tag_list(self):
        my_list = list([obs.tag_number for obs in self.observations.filter(tag_number__isnull=False)])
        my_list.sort()
        return mark_safe(listrify(my_list))

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
        return "{} ({})".format(self.get_sample_type_display(), self.id)

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
    def water_depth_display(self):
        if self.sample_type == 1:
            return mark_safe(_("<u>depth (m):</u> {depth}&plusmn;{delta}; <u>discharge (m<sup>3</sup>/s):</u> {dischard}").format(
                depth=nz(self.water_depth_m, "---"),
                delta=nz(self.water_level_delta_m, "---"),
                dischard=nz(self.discharge_m3_sec, "---"),
            ))
        elif self.sample_type == 2:
            return mark_safe(_("<u>avg. lower depth (cm):</u> {d1}<br> <u>avg. middle depth (cm):</u> {d2}<br> <u>avg. upper depth (cm):</u> {d3}").format(
                d1=nz(self.get_avg_depth("lower"), "---"),
                d2=nz(self.get_avg_depth("middle"), "---"),
                d3=nz(self.get_avg_depth("upper"), "---"),
            ))

    @property
    def rpms(self):
        return mark_safe(_("<u>@start (m):</u> {start}; <u>@end:</u> {end}").format(
            start=nz(self.rpm_arrival, "---"),
            end=nz(self.rpm_departure, "---"),
        ))

    @property
    def overhanging_veg_display(self):
        return mark_safe(_("<u>left:</u> {left}; <u>right:</u> {right}").format(
            left=nz(self.overhanging_veg_left, "---"),
            right=nz(self.overhanging_veg_right, "---"),
        ))

    @property
    def max_overhanging_veg_display(self):
        return mark_safe(_("<u>left:</u> {left}; <u>right:</u> {right}").format(
            left=nz(self.max_overhanging_veg_left, "---"),
            right=nz(self.max_overhanging_veg_right, "---"),
        ))

    @property
    def crew_display(self):
        return mark_safe(_("<u>probe:</u> {probe}<br> <u>seine:</u> {seine}<br> <u>dipnet:</u> {dipnet}<br> <u>extras:</u> {extras}").format(
            probe=nz(self.crew_probe, "---"),
            seine=nz(self.crew_seine, "---"),
            dipnet=nz(self.crew_dipnet, "---"),
            extras=nz(self.crew_extras, "---"),
        ))

    @property
    def wind(self):
        return _("<u>speed:</u> {speed}; <u>direction:</u> {dir}").format(
            speed=nz(self.get_wind_speed_display(), "---"),
            dir=nz(self.get_wind_direction_display(), "---"),
        )

    @property
    def water_temp(self):
        my_str = _("<u>general:</u> {shore}").format(shore=nz(self.water_temp_c, "---"))
        if self.water_temp_trap_c:
            my_str += _("<br><u>@trap:</u> {trap}").format(trap=nz(self.water_temp_trap_c, "---"))
        return my_str

    @property
    def electrofisher_params(self):
        return mark_safe(
            f"voltage (V) &rarr; {nz(self.electrofisher_voltage, '---')} <br>output (amps) &rarr; {nz(self.electrofisher_output, '---')} <br>frequency (Hz) &rarr; {nz(self.electrofisher_frequency, '---')} ")


class Sweep(MetadataFields):
    sample = models.ForeignKey(Sample, related_name='sweeps', on_delete=models.DO_NOTHING, editable=False)
    sweep_number = models.FloatField(verbose_name=_("sweep number"), help_text=_(
        "open sites are always 0.5. Closed sites begin at 0.5, but then are depleted starting at 1, and counting up until depletion is achieved (e.g., 2, 3,...)"))
    sweep_time = models.IntegerField(verbose_name=_("sweep time (seconds)"), help_text=_("in seconds"), default=500)
    notes = models.TextField(blank=True, null=True)

    @property
    def observation_count(self):
        return self.observations.count()

    def __str__(self):
        return f"Sweep {self.sweep_number}"

    def get_absolute_url(self):
        return reverse("trapnet:sweep_detail", args=[self.id])

    @property
    def species_list(self):
        spp = Species.objects.filter(observations__sweep=self).distinct()
        my_list = list([f"{sp} ({sp.observations.filter(sweep=self).count()})" for sp in spp])
        my_list.sort()
        return mark_safe(listrify(my_list, "<br>"))

    @property
    def tag_list(self):
        my_list = list([obs.tag_number for obs in self.observations.filter(tag_number__isnull=False)])
        my_list.sort()
        return mark_safe(listrify(my_list))


class Origin(CodeModel):
    pass


class Status(CodeModel):
    pass


class Sex(CodeModel):
    pass


class Maturity(CodeModel):
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
    fish_size_choices = (
        (1, _("Fry")),
        (2, _("Parr")),
    )
    age_type_choices = (
        (1, _("scale")),
        (2, _("length-frequency")),
    )
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observations")
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="observations")
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)
    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))
    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    location_tagged = models.CharField(max_length=500, blank=True, null=True)
    tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"), unique=True)
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"))
    date_tagged = models.DateTimeField(blank=True, null=True, verbose_name="original date tagged")
    tags_removed = models.CharField(max_length=250, blank=True, null=True)

    # electrofishing only
    fish_size = models.IntegerField(blank=True, null=True, verbose_name=_("fish size"), choices=fish_size_choices)
    maturity = models.ForeignKey(Maturity, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)

    # downstream
    age_type = models.IntegerField(blank=True, null=True, verbose_name=_("age type"), choices=fish_size_choices)
    river_age = models.IntegerField(blank=True, null=True, verbose_name=_("river age"))
    ocean_age = models.IntegerField(blank=True, null=True, verbose_name=_("ocean age"))

    notes = models.TextField(blank=True, null=True)

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="observations", blank=True, null=True)
    sweep = models.ForeignKey(Sweep, on_delete=models.CASCADE, related_name="observations", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.sweep:
            self.sample = self.sweep.sample
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.species)

    class Meta:
        ordering = ["sample__arrival_date", "species", "tag_number"]


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'trapnet/observation_{0}/{1}'.format(instance.observation.id, filename)


class File(MetadataFields):
    observation = models.ForeignKey(Observation, related_name="files", on_delete=models.CASCADE, editable=False)
    caption = models.CharField(max_length=255)
    image = models.ImageField(upload_to=file_directory_path)

    class Meta:
        ordering = ['caption']

    def __str__(self):
        return self.caption


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).image
    except File.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
