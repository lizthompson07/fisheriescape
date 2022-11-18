import os
import statistics

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext

from dm_apps.utils import get_timezone_time
from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import MetadataFields, SimpleLookup, LatLongFields, Lookup
from shared_models.utils import remove_nulls
from trapnet import model_choices

YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


class TrapNetUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trap_net_user", verbose_name=_("DM Apps user"))
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)
    is_crud_user = models.BooleanField(default=False, verbose_name=_("CRUD only?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class CodeModel(SimpleLookup):
    code = models.CharField(max_length=5, blank=True, null=True, unique=True)

    @property
    def choice(self):
        return f"{self.code} - {self.tname}"

    class Meta:
        ordering = ['code', ]
        abstract = True


class RiverSite(MetadataFields, LatLongFields):
    name = models.CharField(max_length=255, verbose_name=_("site name"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='river_sites', blank=False, null=True)
    stream_order = models.IntegerField(blank=True, null=True)
    elevation_m = models.FloatField(blank=True, null=True, verbose_name=_("elevation (m)"))
    epsg_id = models.CharField(max_length=255, default="WGS84", verbose_name=_("EPSG"))
    coordinate_resolution = models.FloatField(blank=True, null=True)
    coordinate_precision = models.FloatField(blank=True, null=True)
    coordinate_accuracy = models.FloatField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # non-editable
    river = models.ForeignKey(shared_models.River, on_delete=models.DO_NOTHING, related_name='sites', editable=False)

    def __str__(self):
        try:
            return "{} ({})".format(self.name, self.river.name)
        except AttributeError:
            return "{}".format(self.name)

    class Meta:
        ordering = ['river', 'name']


class MonitoringProgram(Lookup):
    pass


class LifeStage(CodeModel):
    pass


class ReproductiveStatus(CodeModel):
    pass


class Species(MetadataFields):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tsn = models.IntegerField(blank=False, null=True, verbose_name="ITIS TSN", help_text=_("Integrated Taxonomic Information System (https://www.itis.gov/)"),
                              unique=True)
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    notes = models.TextField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_spp_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_spp_updated_by')

    def __str__(self):
        my_str = getattr(self, str(_("common_name_eng")))
        return my_str

    @property
    def full_name(self):
        return str(self)

    @property
    def search_name(self):
        return f"({self.code}) - {self.full_name}"

    class Meta:
        ordering = ['common_name_eng']
        verbose_name_plural = _("species")

    def get_absolute_url(self):
        return reverse("trapnet:species_detail", kwargs={"pk": self.id})

    @property
    def observation_count(self):
        return self.observations.count()


class Electrofisher(SimpleLookup):
    model_number = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.tname} (s/n: {nz(self.serial_number, '---')})"


class Sample(MetadataFields):
    site = models.ForeignKey(RiverSite, related_name='samples', on_delete=models.DO_NOTHING)
    sample_type = models.IntegerField(choices=model_choices.sample_type_choices)

    arrival_date = models.DateTimeField(verbose_name="arrival date/time")
    departure_date = models.DateTimeField(verbose_name="departure date/time")
    samplers = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # electro
    crew_probe = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (probe)"))
    crew_seine = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (seine)"))
    crew_dipnet = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (dipnet)"))
    crew_extras = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (extras)"))

    # site description
    percent_riffle = models.IntegerField(blank=True, null=True, verbose_name=_("riffle"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_run = models.IntegerField(blank=True, null=True, verbose_name=_("run"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_flat = models.IntegerField(blank=True, null=True, verbose_name=_("flat"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_pool = models.IntegerField(blank=True, null=True, verbose_name=_("pool"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    bank_length_left = models.FloatField(null=True, blank=True, verbose_name=_("bank length - left (m)"))
    bank_length_right = models.FloatField(null=True, blank=True, verbose_name=_("bank length - right (m)"))
    width_lower = models.FloatField(null=True, blank=True, verbose_name=_("width - lower (m)"))
    depth_1_lower = models.FloatField(null=True, blank=True, verbose_name=_("depth #1 - lower (cm)"))
    depth_2_lower = models.FloatField(null=True, blank=True, verbose_name=_("depth #2 - lower (cm)"))
    depth_3_lower = models.FloatField(null=True, blank=True, verbose_name=_("depth #3 - lower (cm)"))
    width_middle = models.FloatField(null=True, blank=True, verbose_name=_("width - middle (m)"))
    depth_1_middle = models.FloatField(null=True, blank=True, verbose_name=_("depth #1 - middle (cm)"))
    depth_2_middle = models.FloatField(null=True, blank=True, verbose_name=_("depth #2 - middle (cm)"))
    depth_3_middle = models.FloatField(null=True, blank=True, verbose_name=_("depth #3 - middle (cm)"))
    width_upper = models.FloatField(null=True, blank=True, verbose_name=_("width - upper (m)"))
    depth_1_upper = models.FloatField(null=True, blank=True, verbose_name=_("depth #1 - upper (cm)"))
    depth_2_upper = models.FloatField(null=True, blank=True, verbose_name=_("depth #2 - upper (cm)"))
    depth_3_upper = models.FloatField(null=True, blank=True, verbose_name=_("depth #3 - upper (cm)"))
    max_depth = models.FloatField(null=True, blank=True, verbose_name=_("max depth (cm)"), help_text=_("max depth found within the whole site"))

    # temp/climate data
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)")
    min_air_temp = models.FloatField(null=True, blank=True, verbose_name="minimum air temperature (°C)")
    max_air_temp = models.FloatField(null=True, blank=True, verbose_name="maximum air temperature (°C)")
    percent_cloud_cover = models.FloatField(null=True, blank=True, verbose_name="cloud cover", validators=[MinValueValidator(0), MaxValueValidator(1)])
    precipitation_category = models.IntegerField(blank=True, null=True, choices=model_choices.precipitation_category_choices)
    precipitation_comment = models.CharField(max_length=255, blank=True, null=True)
    wind_speed = models.IntegerField(blank=True, null=True, choices=model_choices.wind_speed_choices)
    wind_direction = models.IntegerField(blank=True, null=True, choices=model_choices.wind_direction_choices)

    # water data
    water_depth_m = models.FloatField(null=True, blank=True, verbose_name="water depth (m)")
    water_level_delta_m = models.FloatField(null=True, blank=True, verbose_name="water level delta (m)")
    discharge_m3_sec = models.FloatField(null=True, blank=True, verbose_name="discharge (m3/s)")
    water_temp_c = models.FloatField(null=True, blank=True, verbose_name="water temperature (°C)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at trap (°C)")
    water_cond = models.FloatField(null=True, blank=True, verbose_name="specific conductivity (µS)",
                                   help_text=_("The measurement is to 1 decimal place in micro siemens (µS)"))
    water_ph = models.FloatField(null=True, blank=True, verbose_name="water acidity (pH)")
    overhanging_veg_left = models.FloatField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Left"),
                                             validators=(MinValueValidator(0), MaxValueValidator(100)))
    overhanging_veg_right = models.FloatField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Right"),
                                              validators=(MinValueValidator(0), MaxValueValidator(100)))
    max_overhanging_veg_left = models.FloatField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Left"))
    max_overhanging_veg_right = models.FloatField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Right"))

    # substrate
    percent_fine = models.FloatField(blank=True, null=True, verbose_name=_("fine silt or clay"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_sand = models.FloatField(blank=True, null=True, verbose_name=_("sand"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_gravel = models.FloatField(blank=True, null=True, verbose_name=_("gravel"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_pebble = models.FloatField(blank=True, null=True, verbose_name=_("pebble"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_cobble = models.FloatField(blank=True, null=True, verbose_name=_("cobble"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_rocks = models.FloatField(blank=True, null=True, verbose_name=_("rocks"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_boulder = models.FloatField(blank=True, null=True, verbose_name=_("boulder"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_bedrock = models.FloatField(blank=True, null=True, verbose_name=_("bedrock"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    # rst
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="RPM at start")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="RPM at end")
    time_released = models.DateTimeField(verbose_name="time released", blank=True, null=True)
    operating_condition = models.IntegerField(blank=True, null=True, choices=model_choices.operating_condition_choices)
    operating_condition_comment = models.CharField(max_length=255, blank=True, null=True)

    # ef
    seine_type = models.IntegerField(blank=True, null=True, choices=model_choices.seine_type_choices, verbose_name=_("type of seine"))
    site_type = models.IntegerField(blank=True, null=True, choices=model_choices.site_type_choices, verbose_name=_("type of site"))
    electrofisher = models.ForeignKey(Electrofisher, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("electrofisher"), blank=True,
                                      null=True)
    electrofisher_voltage = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher voltage (V)"))
    electrofisher_output_low = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher output, low (amps)"))
    electrofisher_output_high = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher output, high (amps)"))
    electrofisher_frequency = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher frequency (Hz)"))
    electrofisher_pulse_type = models.IntegerField(blank=True, null=True, choices=model_choices.pulse_type_choices, verbose_name=_("type of pulse"))
    duty_cycle = models.IntegerField(blank=True, null=True, verbose_name=_("duty cycle (%)"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    # non-editable
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_updated_by')
    season = models.IntegerField(null=True, blank=True, editable=False)
    is_reviewed = models.BooleanField(default=False, editable=False, verbose_name=_("Has been reviewed?"))
    reviewed_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_reviewed_by')
    reviewed_at = models.DateTimeField(blank=True, null=True, editable=False)
    old_id = models.CharField(max_length=25, null=True, blank=True, editable=False, unique=True)

    @property
    def julian_day(self):
        return self.arrival_date.timetuple().tm_yday

    @property
    def reviewed_status(self):
        if not self.is_reviewed:
            return gettext("Not reviewed")
        return gettext("Reviewed by {user} on {time}").format(user=self.reviewed_by, time=date(self.reviewed_at))

    @property
    def full_wetted_width(self):
        return self.get_full_wetted_width()

    def get_full_wetted_width(self, show_errors=True):
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
            if show_errors:
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
                my_str += f"{attr}% {substrate}<br> "
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
                my_str += f"{attr}% {substrate}<br> "
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
            arrival=get_timezone_time(self.arrival_date).strftime("%Y-%m-%d %H:%M"),
            departure=get_timezone_time(self.departure_date).strftime("%Y-%m-%d %H:%M"),
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
            f"voltage (V): {nz(self.electrofisher_voltage, '---')} "
            f"<br>output, low (amps): {nz(self.electrofisher_output_low, '---')}"
            f"<br>output, high (amps): {nz(self.electrofisher_output_high, '---')} "
            f"<br>frequency (Hz): {nz(self.electrofisher_frequency, '---')} "
            f"<br>type of pulse: {nz(self.get_electrofisher_pulse_type_display(), '---')} "
            f"<br>duty cycle (%): {nz(self.duty_cycle, '---')} "
        )


class Sweep(MetadataFields):
    sample = models.ForeignKey(Sample, related_name='sweeps', on_delete=models.DO_NOTHING, editable=False)
    sweep_number = models.FloatField(verbose_name=_("sweep number"), help_text=_(
        "open sites are always 0.5. Closed sites begin at 0.5, but then are depleted starting at 1, and counting up until depletion is achieved (e.g., 2, 3,...)"))
    sweep_time = models.IntegerField(verbose_name=_("sweep time (seconds)"), help_text=_("in seconds"))
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


#
#
# class Entry(MetadataFields):
#     first_tag = models.CharField(max_length=50, blank=True, null=True)
#     last_tag = models.CharField(max_length=50, blank=True, null=True)
#     status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="entries", blank=True, null=True)
#     origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="entries", blank=True, null=True)
#     frequency = models.IntegerField(blank=True, null=True, verbose_name=_("frequency"))
#     fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
#     total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))
#     weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
#     sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="entries", blank=True, null=True)
#     smolt_age = models.IntegerField(blank=True, null=True)
#     location_tagged = models.CharField(max_length=500, blank=True, null=True)
#     date_tagged = models.DateTimeField(blank=True, null=True, verbose_name="date tagged")
#     scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"))
#     tags_removed = models.CharField(max_length=250, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#
#     # non-editable
#     species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="entries", editable=False, blank=True, null=True)
#     sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="entries", editable=False, blank=True, null=True)
#
#     def save(self, *args, **kwargs):
#         return super().save(*args, **kwargs)
#
#     class Meta:
#         verbose_name_plural = "entries"


class Observation(MetadataFields):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observations")
    life_stage = models.ForeignKey(LifeStage, related_name='observations', on_delete=models.DO_NOTHING, blank=True, null=True)
    reproductive_status = models.ForeignKey(ReproductiveStatus, related_name='observations', on_delete=models.DO_NOTHING, blank=True, null=True)

    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="observations", blank=False, null=True)
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)

    # consider deleting
    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))

    length = models.FloatField(blank=True, null=True, verbose_name=_("length (mm)"), editable=False)
    length_type = models.IntegerField(blank=True, null=True, verbose_name=_("length type"), choices=model_choices.length_type_choices, editable=False)

    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"))
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"), unique=True)

    # electrofishing only
    fish_size = models.IntegerField(blank=True, null=True, verbose_name=_("fish size"), choices=model_choices.fish_size_choices)
    maturity = models.ForeignKey(Maturity, on_delete=models.DO_NOTHING, related_name="observations", blank=True, null=True)

    # downstream
    age_type = models.IntegerField(blank=True, null=True, verbose_name=_("age type"), choices=model_choices.age_type_choices)
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
        return f"{self.species} ({self.id})"

    class Meta:
        ordering = ["sample__arrival_date"]

    @property
    def is_recapture(self):
        return self.status and self.status.code.lower() in ["rr", "rrl"]

    @property
    def first_tagging(self):
        if self.tag_number and self.is_recapture:
            first_obs_qs = Observation.objects.filter(~Q(id=self.id)).filter(tag_number=self.tag_number)
            if first_obs_qs.exists():
                return first_obs_qs.first()


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'trapnet/observation_{0}/{1}'.format(instance.observation.id, filename)


def sample_file_directory_path(instance, filename):
    return 'trapnet/sample_{0}/{1}'.format(instance.sample.id, filename)


class File(MetadataFields):
    observation = models.ForeignKey(Observation, related_name="files", on_delete=models.CASCADE, editable=False)
    caption = models.CharField(max_length=255)
    image = models.ImageField(upload_to=file_directory_path)

    class Meta:
        ordering = ['caption']

    def __str__(self):
        return self.caption


class SampleFile(MetadataFields):
    sample = models.ForeignKey(Sample, related_name="files", on_delete=models.CASCADE, editable=False)
    caption = models.CharField(max_length=255)
    file = models.FileField(upload_to=sample_file_directory_path)

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


@receiver(models.signals.post_delete, sender=SampleFile)
def auto_delete_sample_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=SampleFile)
def auto_delete_sample_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
