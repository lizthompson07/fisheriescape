import statistics

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Count
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
from trapnet.utils import get_age_from_length

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
    def specimen_count(self):
        return self.specimens.count()


class Electrofisher(SimpleLookup):
    model_number = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.tname} (s/n: {nz(self.serial_number, '---')})"


class Sample(MetadataFields):
    # shared stuff
    site = models.ForeignKey(RiverSite, related_name='samples', on_delete=models.DO_NOTHING)
    monitoring_program = models.ForeignKey(MonitoringProgram, on_delete=models.DO_NOTHING, verbose_name=_("monitoring program"),
                                           help_text=_("The sample was collected under which monitoring program"), related_name="samples", blank=True,
                                           null=True)

    arrival_date = models.DateTimeField(verbose_name="arrival date/time")
    departure_date = models.DateTimeField(verbose_name="departure date/time")
    sample_type = models.IntegerField(choices=model_choices.sample_type_choices)

    age_thresh_0_1 = models.IntegerField(blank=True, null=True, verbose_name=_("salmon site-specific age threshold (0+ to 1+)"))
    age_thresh_1_2 = models.IntegerField(blank=True, null=True, verbose_name=_("salmon site-specific age threshold (1+ to 2+)"))
    age_thresh_2_3 = models.IntegerField(blank=True, null=True, verbose_name=_("salmon site-specific age threshold (2+ to 3+)"))
    age_thresh_parr_smolt = models.IntegerField(blank=True, null=True, verbose_name=_("salmon site-specific age threshold (parr to smolt)"))
    didymo = models.IntegerField(blank=True, null=True, verbose_name=_("presence / absence of Didymosphenia geminata"), choices=model_choices.didymo_choices)
    notes = models.TextField(blank=True, null=True)

    # to migrate then delete
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)", editable=False)
    water_temp_c = models.FloatField(null=True, blank=True, verbose_name="water temperature (°C)", editable=False)

    # non-editable, historical
    min_air_temp = models.FloatField(null=True, blank=True, verbose_name="minimum air temperature (°C)", editable=False)
    max_air_temp = models.FloatField(null=True, blank=True, verbose_name="maximum air temperature (°C)", editable=False)
    percent_cloud_cover = models.FloatField(null=True, blank=True, verbose_name="cloud cover", validators=[MinValueValidator(0), MaxValueValidator(1)],
                                            editable=False)
    precipitation_category = models.IntegerField(blank=True, null=True, choices=model_choices.precipitation_category_choices, editable=False)
    precipitation_comment = models.CharField(max_length=255, blank=True, null=True, editable=False)
    wind_speed = models.IntegerField(blank=True, null=True, choices=model_choices.wind_speed_choices, editable=False)
    wind_direction = models.IntegerField(blank=True, null=True, choices=model_choices.wind_direction_choices, editable=False)

    # non-editable
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_sample_updated_by')
    season = models.IntegerField(null=True, blank=True, editable=False)
    is_reviewed = models.BooleanField(default=False, editable=False, verbose_name=_("Has been reviewed?"))
    reviewed_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='trapnet_reviewed_by')
    reviewed_at = models.DateTimeField(blank=True, null=True, editable=False)
    old_id = models.CharField(max_length=25, null=True, blank=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.season = self.arrival_date.year
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

        if self.sample_type == 1:
            RSTSample.objects.get_or_create(sample=self)
        elif self.sample_type == 2:
            EFSample.objects.get_or_create(sample=self)
        elif self.sample_type == 3:
            TrapnetSample.objects.get_or_create(sample=self)

    class Meta:
        ordering = ['-arrival_date', ]
        # unique_together = [["start_date", "station"], ]

    def get_absolute_url(self):
        return reverse("trapnet:sample_detail", kwargs={"pk": self.id})

    def __str__(self):
        return "{} ({})".format(self.get_sample_type_display(), self.id)

    def get_sub_obj(self):
        sub = None
        if self.sample_type == 1:
            sub = self.rst_sample
        elif self.sample_type == 2:
            sub = self.ef_sample
        elif self.sample_type == 3:
            sub = self.trapnet_sample
        return sub

    def get_detailed_salmon(self):
        return self.get_salmon_with_lengths().filter(weight__isnull=False)

    def get_salmon_with_lengths(self):
        return self.specimens.filter(species__tsn=161996, fork_length__isnull=False)

    @property
    def has_thresholds(self):
        return bool(self.age_thresh_0_1 and self.age_thresh_1_2)

    @property
    def julian_day(self):
        return self.arrival_date.timetuple().tm_yday

    @property
    def reviewed_status(self):
        if not self.is_reviewed:
            return gettext("Not reviewed")
        return gettext("Reviewed by {user} on {time}").format(user=self.reviewed_by, time=date(self.reviewed_at))

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
        spp = Species.objects.filter(Q(specimens__sample=self) | Q(specimens__sweep__sample=self)).distinct()
        my_list = list([f"{sp} ({sp.specimens.filter(Q(sample=self) | Q(sweep__sample=self)).count()})" for sp in spp])
        my_list.sort()
        return mark_safe(listrify(my_list, "<br>"))

    @property
    def tag_list(self):
        my_list = list([specimen.tag_number for specimen in self.specimens.filter(tag_number__isnull=False)])
        my_list.sort()
        return mark_safe(listrify(my_list))

    @property
    def arrival_departure(self):
        return mark_safe(_("{arrival} &rarr; {departure} ({duration})").format(
            arrival=get_timezone_time(self.arrival_date).strftime("%Y-%m-%d %H:%M"),
            departure=get_timezone_time(self.departure_date).strftime("%Y-%m-%d %H:%M"),
            duration=self.duration,
        ))

    @property
    def air_temp(self):
        return _("<u>arrival:</u> {arrival}<br> <u>max:</u> {max}<br> <u>min:</u> {min}").format(
            arrival=nz(self.air_temp_arrival, "---"),
            max=nz(self.max_air_temp, "---"),
            min=nz(self.min_air_temp, "---"),
        )

    @property
    def thresholds(self):
        return _("<u>0+ to 1+:</u> {t01}<br> <u>1+ to 2+:</u> {t12}<br> <u>2+ to 3+:</u> {t23}<br> <u>parr to smolt:</u> {tps}").format(
            t01=nz(self.age_thresh_0_1, "---"),
            t12=nz(self.age_thresh_1_2, "---"),
            t23=nz(self.age_thresh_2_3, "---"),
            tps=nz(self.age_thresh_parr_smolt, "---"),
        )

    @property
    def wind(self):
        return _("<u>speed:</u> {speed}; <u>direction:</u> {dir}").format(
            speed=nz(self.get_wind_speed_display(), "---"),
            dir=nz(self.get_wind_direction_display(), "---"),
        )


class EFSample(models.Model):
    sample = models.OneToOneField(Sample, related_name='ef_sample', on_delete=models.CASCADE, editable=False)

    site_type = models.IntegerField(blank=True, null=True, choices=model_choices.site_type_choices, verbose_name=_("type of site"))
    seine_type = models.IntegerField(blank=True, null=True, choices=model_choices.seine_type_choices, verbose_name=_("type of seine"), default=2)

    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)")
    water_temp_c = models.FloatField(null=True, blank=True, verbose_name="water temperature (°C)")

    # site description
    percent_riffle = models.IntegerField(blank=True, null=True, verbose_name=_("riffle"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_run = models.IntegerField(blank=True, null=True, verbose_name=_("run"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_flat = models.IntegerField(blank=True, null=True, verbose_name=_("flat"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_pool = models.IntegerField(blank=True, null=True, verbose_name=_("pool"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    # river description
    bank_length_left = models.FloatField(null=True, blank=True, verbose_name=_("bank length - left (m)"))
    overhanging_veg_left = models.FloatField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Left"),
                                             validators=(MinValueValidator(0), MaxValueValidator(100)))
    max_overhanging_veg_left = models.FloatField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Left"))

    bank_length_right = models.FloatField(null=True, blank=True, verbose_name=_("bank length - right (m)"))
    overhanging_veg_right = models.FloatField(blank=True, null=True, verbose_name=_("Overhanging Vegetation (%) - Right"),
                                              validators=(MinValueValidator(0), MaxValueValidator(100)))
    max_overhanging_veg_right = models.FloatField(blank=True, null=True, verbose_name=_("Max Overhanging Vegetation (m) - Right"))

    # water
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
    water_cond = models.FloatField(null=True, blank=True, verbose_name="specific conductivity (µS)",
                                   help_text=_("The measurement is to 1 decimal place in micro siemens (µS)"))
    water_ph = models.FloatField(null=True, blank=True, verbose_name="water acidity (pH)")

    # substrate
    percent_fine = models.FloatField(blank=True, null=True, verbose_name=_("fine silt or clay"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_sand = models.FloatField(blank=True, null=True, verbose_name=_("sand"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_gravel = models.FloatField(blank=True, null=True, verbose_name=_("gravel"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_pebble = models.FloatField(blank=True, null=True, verbose_name=_("pebble"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_cobble = models.FloatField(blank=True, null=True, verbose_name=_("cobble"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_rocks = models.FloatField(blank=True, null=True, verbose_name=_("rocks"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_boulder = models.FloatField(blank=True, null=True, verbose_name=_("boulder"), validators=(MinValueValidator(0), MaxValueValidator(100)))
    percent_bedrock = models.FloatField(blank=True, null=True, verbose_name=_("bedrock"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    # efisher
    electrofisher = models.ForeignKey(Electrofisher, related_name='ef_samples', on_delete=models.DO_NOTHING, verbose_name=_("electrofisher"), blank=True,
                                      null=True)
    electrofisher_voltage = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher voltage (V)"))
    electrofisher_output_low = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher output, low (amps)"))
    electrofisher_output_high = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher output, high (amps)"))
    electrofisher_frequency = models.FloatField(null=True, blank=True, verbose_name=_("electrofisher frequency (Hz)"))
    electrofisher_pulse_type = models.IntegerField(blank=True, null=True, choices=model_choices.pulse_type_choices, verbose_name=_("type of pulse"))
    duty_cycle = models.IntegerField(blank=True, null=True, verbose_name=_("duty cycle (%)"), validators=(MinValueValidator(0), MaxValueValidator(100)))

    # crew
    crew_probe = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (probe)"))
    crew_seine = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (seine)"))
    crew_dipnet = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (dipnet)"))
    crew_extras = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("crew (extras)"))

    @property
    def avg_wetted_width(self):
        widths = [
            self.width_lower,
            self.width_middle,
            self.width_upper,
        ]
        remove_nulls(widths)
        if len(widths):
            return round(statistics.mean(widths), 3)

    @property
    def avg_wetted_length(self):
        widths = [
            self.bank_length_left,
            self.bank_length_right,
        ]
        remove_nulls(widths)
        if len(widths):
            return round(statistics.mean(widths), 3)

    @property
    def full_wetted_area(self):
        try:
            return round(self.avg_wetted_width * self.avg_wetted_length, 3)
        except:
            pass

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

    def get_avg_depth(self, which_depth):
        d1 = getattr(self, f"depth_1_{which_depth}")
        d2 = getattr(self, f"depth_2_{which_depth}")
        d3 = getattr(self, f"depth_3_{which_depth}")
        depths = [d1, d2, d3]
        remove_nulls(depths)
        if len(depths):
            return round(statistics.mean(depths), 3)

    @property
    def water_depth_display(self):
        return mark_safe(
            _("<u>avg. lower depth (cm):</u> {d1}<br> <u>avg. middle depth (cm):</u> {d2}<br> <u>avg. upper depth (cm):</u> {d3}<br> <u>max depth (cm):</u> {d4}").format(
                d1=nz(self.get_avg_depth("lower"), "---"),
                d2=nz(self.get_avg_depth("middle"), "---"),
                d3=nz(self.get_avg_depth("upper"), "---"),
                d4=nz(self.max_depth, "---"),
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
    def electrofisher_params(self):
        return mark_safe(
            f"voltage (V): {nz(self.electrofisher_voltage, '---')} "
            f"<br>output, low (amps): {nz(self.electrofisher_output_low, '---')}"
            f"<br>output, high (amps): {nz(self.electrofisher_output_high, '---')} "
            f"<br>frequency (Hz): {nz(self.electrofisher_frequency, '---')} "
            f"<br>type of pulse: {nz(self.get_electrofisher_pulse_type_display(), '---')} "
            f"<br>duty cycle (%): {nz(self.duty_cycle, '---')} "
        )


class RSTSample(models.Model):
    sample = models.OneToOneField(Sample, related_name='rst_sample', on_delete=models.CASCADE, editable=False)
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)")
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at trap (°C)")
    water_depth_m = models.FloatField(null=True, blank=True, verbose_name="water depth (m)")
    water_level_delta_m = models.FloatField(null=True, blank=True, verbose_name="water level delta (m)")
    rpm_arrival = models.FloatField(null=True, blank=True, verbose_name="RPM at start")
    rpm_departure = models.FloatField(null=True, blank=True, verbose_name="RPM at end")
    time_released = models.DateTimeField(verbose_name="time released", blank=True, null=True)
    operating_condition = models.IntegerField(blank=True, null=True, choices=model_choices.operating_condition_choices)
    operating_condition_comment = models.CharField(max_length=255, blank=True, null=True)
    samplers = models.TextField(blank=True, null=True)

    # non-editable, historical
    discharge_m3_sec = models.FloatField(null=True, blank=True, verbose_name="discharge (m3/s)", editable=False)

    @property
    def rpms(self):
        return mark_safe(_("<u>@start (m):</u> {start}; <u>@end:</u> {end}").format(
            start=nz(self.rpm_arrival, "---"),
            end=nz(self.rpm_departure, "---"),
        ))

    @property
    def water_display(self):
        return mark_safe(_("<u>depth (m):</u> {depth}&plusmn;{delta}").format(
            depth=nz(self.water_depth_m, "---"),
            delta=nz(self.water_level_delta_m, "---"),
        ))


class TrapnetSample(models.Model):
    sample = models.OneToOneField(Sample, related_name='trapnet_sample', on_delete=models.CASCADE, editable=False)
    water_temp_trap_c = models.FloatField(null=True, blank=True, verbose_name="water temperature at trap (°C)")
    air_temp_arrival = models.FloatField(null=True, blank=True, verbose_name="air temperature on arrival(°C)")

    arrival_condition = models.IntegerField(blank=True, null=True, choices=model_choices.operating_condition_choices)
    arrival_condition_comment = models.CharField(max_length=255, blank=True, null=True)
    departure_condition = models.IntegerField(blank=True, null=True, choices=model_choices.operating_condition_choices)
    departure_condition_comment = models.CharField(max_length=255, blank=True, null=True)

    time_released = models.DateTimeField(verbose_name="time released", blank=True, null=True)
    sea_lice = models.IntegerField(blank=True, null=True, choices=model_choices.sea_lice_choices)
    samplers = models.TextField(blank=True, null=True)


class Sweep(MetadataFields):
    sample = models.ForeignKey(Sample, related_name='sweeps', on_delete=models.CASCADE, editable=False)
    sweep_number = models.FloatField(verbose_name=_("sweep number"), help_text=_(
        "open sites are always 0.5. Closed sites begin at 0.5, but then are depleted starting at 1, and counting up until depletion is achieved (e.g., 2, 3,...)"))
    sweep_time = models.IntegerField(verbose_name=_("sweep time (seconds)"), help_text=_("in seconds"))
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("sample", "sweep_number"),)

    @property
    def specimen_count(self):
        return self.specimens.count()

    def __str__(self):
        return f"Sweep {self.sweep_number}"

    def get_absolute_url(self):
        return reverse("trapnet:sweep_detail", args=[self.id])

    @property
    def species_list(self):
        spp = Species.objects.filter(specimens__sweep=self).distinct()
        my_list = list([f"{sp} ({sp.specimens.filter(sweep=self).count()})" for sp in spp])
        my_list.sort()
        return mark_safe(listrify(my_list, "<br>"))

    @property
    def tag_list(self):
        my_list = list([specimen.tag_number for specimen in self.specimens.filter(tag_number__isnull=False)])
        my_list.sort()
        return mark_safe(listrify(my_list))

    def get_salmon_age_breakdown(self):
        payload = dict()
        count_qs = self.specimens.filter(species__tsn=161996).order_by("smart_river_age").values("smart_river_age").distinct().annotate(
            counts=Count("smart_river_age"))
        for item in count_qs:
            payload[item["smart_river_age"]] = item["counts"]
        return payload


class Origin(CodeModel):
    pass


class Status(CodeModel):
    pass


class Sex(CodeModel):
    pass


class Maturity(CodeModel):
    description = models.TextField(blank=True, null=True)


class Specimen(MetadataFields):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="specimens")
    life_stage = models.ForeignKey(LifeStage, related_name='specimens', on_delete=models.DO_NOTHING, blank=True, null=True)
    reproductive_status = models.ForeignKey(ReproductiveStatus, related_name='specimens', on_delete=models.DO_NOTHING, blank=True, null=True)
    maturity = models.ForeignKey(Maturity, related_name='specimens', on_delete=models.DO_NOTHING, blank=True, null=True)

    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="specimens", blank=False, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="specimens", blank=True, null=True)
    adipose_condition = models.IntegerField(blank=True, null=True, verbose_name=_("adipose condition"), choices=model_choices.adipose_condition_choices)

    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    fork_length_bin_interval = models.FloatField(default=1, verbose_name=_("fork length bin interval (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))

    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"))
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"), unique=True)

    # downstream
    age_type = models.IntegerField(blank=True, null=True, verbose_name=_("age type"), choices=model_choices.age_type_choices)
    river_age = models.IntegerField(blank=True, null=True, verbose_name=_("river age"))
    ocean_age = models.IntegerField(blank=True, null=True, verbose_name=_("ocean age"))

    notes = models.TextField(blank=True, null=True)

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="specimens", blank=True, null=True)
    sweep = models.ForeignKey(Sweep, on_delete=models.CASCADE, related_name="specimens", blank=True, null=True)
    old_id = models.CharField(max_length=25, null=True, blank=True, editable=False)
    smart_river_age = models.IntegerField(null=True, blank=True, editable=False)
    smart_river_age_type = models.IntegerField(null=True, blank=True, editable=False, choices=model_choices.age_type_choices)

    # to be deleted eventually
    origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="specimens", blank=True, null=True, editable=False)

    @property
    def smart_river_age_display(self):
        if self.smart_river_age is not None:
            return f"{self.smart_river_age} ({self.get_smart_river_age_type_display()})"

    def get_smart_river_age_dict(self):
        """ only applies to salmon who have fork lengths. If ever there was a river age assigned, this trumps any calculated ages"""
        payload = dict(age=self.river_age, type=self.age_type)
        if self.river_age is None and (self.is_salmon and self.fork_length):
            payload["age"] = self.get_calc_river_age()
            payload["type"] = 3 if payload["age"] is not None else None

        return payload

    def get_calc_river_age(self):
        """ only applies to salmon who have fork lengths. If ever there was a river age assigned, this trumps any calculated ages"""
        try:
            return get_age_from_length(self.fork_length, self.sample.age_thresh_0_1, self.sample.age_thresh_1_2, self.sample.age_thresh_2_3)
        except:
            return None

    @property
    def is_salmon(self):
        return self.species.tsn == 161996

    def save(self, *args, **kwargs):
        if self.sweep:
            self.sample = self.sweep.sample
        smart_river_age_dict = self.get_smart_river_age_dict()
        self.smart_river_age = smart_river_age_dict.get("age")
        self.smart_river_age_type = smart_river_age_dict.get("type")
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
            first_specimen_qs = Specimen.objects.filter(~Q(id=self.id)).filter(tag_number=self.tag_number)
            if first_specimen_qs.exists():
                return first_specimen_qs.first()


class BiologicalDetailing(MetadataFields):
    '''for historical data'''
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="biological_detailings")
    reproductive_status = models.ForeignKey(ReproductiveStatus, related_name='biological_detailings', on_delete=models.DO_NOTHING, blank=True, null=True)
    maturity = models.ForeignKey(Maturity, related_name='biological_detailings', on_delete=models.DO_NOTHING, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="biological_detailings", blank=False, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="biological_detailings", blank=True, null=True)
    adipose_condition = models.IntegerField(blank=True, null=True, verbose_name=_("adipose condition"), choices=model_choices.adipose_condition_choices)
    life_stage = models.ForeignKey(LifeStage, related_name='biological_detailings', on_delete=models.DO_NOTHING, blank=True, null=True)

    fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
    fork_length_bin_interval = models.FloatField(default=1, verbose_name=_("fork length bin interval (mm)"))
    total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))

    weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
    tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"))
    scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"), unique=True)

    # downstream
    age_type = models.IntegerField(blank=True, null=True, verbose_name=_("age type"), choices=model_choices.age_type_choices)
    river_age = models.IntegerField(blank=True, null=True, verbose_name=_("river age"))

    notes = models.TextField(blank=True, null=True)

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="biological_detailings", blank=True, null=True)
    old_id = models.CharField(max_length=25, null=True, blank=True, editable=False)

    def __str__(self):
        return f"{self.species} ({self.id})"

    class Meta:
        ordering = ["sample__arrival_date"]


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'trapnet/specimen_{0}/{1}'.format(instance.specimen.id, filename)


def sample_file_directory_path(instance, filename):
    return 'trapnet/sample_{0}/{1}'.format(instance.sample.id, filename)


class File(MetadataFields):
    specimen = models.ForeignKey(Specimen, related_name="files", on_delete=models.CASCADE, editable=False)
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

#### NEW WILD STUFF


# class Specimen2(MetadataFields):
#     species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="specimens")
#     notes = models.TextField(blank=True, null=True)
#     sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="specimens", blank=True, null=True)
#     sweep = models.ForeignKey(Sweep, on_delete=models.CASCADE, related_name="specimens", blank=True, null=True)
#     old_id = models.CharField(max_length=25, null=True, blank=True, editable=False)
#
#
# class ObservationType(Lookup, MetadataFields):
#     # choices for data_type
#     DATA_TYPE_CHOICES = (
#         (1, _("integer/categorical")),
#         (2, _("float")),
#         (3, _("string")),
#     )
#     data_type = models.IntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_("data type"))
#     units_to_display = models.IntegerField(blank=True, null=True, verbose_name=_("units to display"), choices=measurement_unit_codes.get_all_choices(),
#                                            help_text=_("Are there units associated with this observation type that should be displayed to an end-user?"))
#     special_type = models.IntegerField(blank=True, null=True, choices=special_observation_types.get_choices(),
#                                        verbose_name=_("Is this the official observation type for a specific measurement?"),
#                                        help_text=_(
#                                            "Certain observation types have hard-coded roles within the system. Those types are identified vis a vis this field."))
#     notes = models.TextField(blank=True, null=True, verbose_name=_("notes"), help_text=_(
#         "Use this field to capture any important notes; especially things that will be important for others to consider when making future adjustments."))
#
#     @property
#     def metadata(self):
#         return get_metadata_string(self.created_at, self.created_by, self.updated_at, self.last_modified_by)
#
#     class Meta:
#         ordering = [_("name"), ]
#         verbose_name = _("observation type")
#
#     def get_absolute_url(self):
#         return reverse('shared_models:ot_detail', kwargs={'pk': self.id})
#
#     @property
#     def display_categories(self):
#         return mark_safe(nz(listrify([obj for obj in self.categories.all()], "; "), ""))
#
#     @property
#     def display_categories_br(self):
#         return mark_safe(nz(listrify([obj for obj in self.categories.all()], "<br>"), ""))
#
#     @property
#     def list_categories(self):
#         return [obj.id for obj in self.categories.all()]
#
#     def save(self, *args, **kwargs):
#         if not self.uuid:
#             self.uuid = uuid.uuid4()
#         if self.special_type:
#             for ot in ObservationType.objects.filter(special_type=self.special_type):
#                 ot.special_type = None
#                 ot.save()
#         super().save(*args, **kwargs)
#
#     @property
#     def category_count(self):
#         return self.categories.count()
#
#
#
# class ObservationTypeCategory(CodeLookup):
#     # Choices for unit type
#     observation_type = models.ForeignKey(ObservationType, on_delete=models.CASCADE, related_name="categories")
#     code = models.CharField(max_length=3)  # need this to be a char and not an Integer field
#     uuid = models.UUIDField(editable=False, unique=True, blank=True, null=True, verbose_name=_("UUID"))
#
#     # metadata
#     created_at = models.DateTimeField(auto_now_add=True, editable=False)
#     updated_at = models.DateTimeField(auto_now=True, editable=False)
#     created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="created_by_obs_type_cat", blank=True, null=True)
#     last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_obs_type_cat", blank=True, null=True)
#
#     @property
#     def metadata(self):
#         return get_metadata_string(self.created_at, self.created_by, self.updated_at, self.last_modified_by)
#
#     @property
#     def tname(self):
#         return self.tdescription
#
#     def __str__(self):
#         return "{}-{}".format(self.code, self.tdescription)
#
#     class Meta:
#         unique_together = ['observation_type', 'code']
#         ordering = ['observation_type', 'code']
#         verbose_name = _("observation type category")
#
#     def save(self, *args, **kwargs):
#         if not self.uuid:
#             self.uuid = uuid.uuid4()
#         super().save(*args, **kwargs)
#         ot = self.observation_type
#         ot.last_modified_by = self.last_modified_by
#         ot.updated_at = self.updated_at
#         ot.save()
#
#
#
#
# class Observation(MetadataFields):
#     specimen = models.ForeignKey(Specimen, on_delete=models.DO_NOTHING, related_name="specimens")
#     life_stage = models.ForeignKey(LifeStage, related_name='specimens', on_delete=models.DO_NOTHING, blank=True, null=True)
#     reproductive_status = models.ForeignKey(ReproductiveStatus, related_name='specimens', on_delete=models.DO_NOTHING, blank=True, null=True)
#
#     status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name="specimens", blank=False, null=True)
#     sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="specimens", blank=True, null=True)
#     adipose_condition = models.IntegerField(blank=True, null=True, verbose_name=_("adipose condition"), choices=model_choices.adipose_condition_choices)
#
#     fork_length = models.FloatField(blank=True, null=True, verbose_name=_("fork length (mm)"))
#     fork_length_bin_interval = models.FloatField(default=1, verbose_name=_("fork length bin interval (mm)"))
#     total_length = models.FloatField(blank=True, null=True, verbose_name=_("total length (mm)"))
#
#     weight = models.FloatField(blank=True, null=True, verbose_name=_("weight (g)"))
#     tag_number = models.CharField(max_length=12, blank=True, null=True, verbose_name=_("tag number"))
#     scale_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("scale ID number"), unique=True)
#
#     # downstream
#     age_type = models.IntegerField(blank=True, null=True, verbose_name=_("age type"), choices=model_choices.age_type_choices)
#     river_age = models.IntegerField(blank=True, null=True, verbose_name=_("river age"))
#     ocean_age = models.IntegerField(blank=True, null=True, verbose_name=_("ocean age"))
#
#     # to be deleted eventually
#     origin = models.ForeignKey(Origin, on_delete=models.DO_NOTHING, related_name="specimens", blank=True, null=True, editable=False)
#
#     class Meta:
#         abstract = True
#
#
