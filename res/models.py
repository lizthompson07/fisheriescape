from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from shapely.geometry import MultiPoint, Point

from scuba.utils import calc_nautical_dist
from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, MetadataFields
from shared_models.utils import decdeg2dm, dm2decdeg


YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)

class Region(UnilingualLookup):
    abbreviation = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='scuba_regions', blank=True, null=True)

    def __str__(self):
        mystr = self.name
        if self.province:
            mystr += f" ({self.province.tabbrev})"
        return mystr

    @property
    def samples(self):
        return Sample.objects.filter(site__region=self).count()

    @property
    def site_count(self):
        return self.sites.count()


class Site(UnilingualLookup):
    abbreviation = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation"))
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name='sites', verbose_name=_("region"), editable=False)
    latitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("latitude (degrees)"))
    latitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("latitude (minutes)"))
    longitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("longitude (degrees)"))
    longitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("longitude (minutes)"))

    # calculated
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude (decimal degrees)"), editable=False)
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("longitude (decimal degrees)"), editable=False)

    def save(self, *args, **kwargs):
        self.latitude = dm2decdeg(self.latitude_d, self.latitude_mm)
        self.longitude = dm2decdeg(self.longitude_d, self.longitude_mm)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Site {self.name}"

    @property
    def transect_count(self):
        return self.transects.count()

    def get_coordinates(self):
        # should be the centroid of all transect coords
        points = list()
        for t in self.transects.all():
            if t.has_coordinates:
                points.extend([
                    Point(t.start_latitude, t.start_longitude),
                    Point(t.end_latitude, t.end_longitude),
                ])
            if len(points):
                return MultiPoint(points).centroid

    @property
    def coordinates(self):
        my_str = "---"
        if self.get_coordinates():
            my_str = self.get_coordinates_ddmm()
        return mark_safe(my_str)

    def get_coordinates_ddmm(self):
        coords = self.get_coordinates()
        if coords:
            dmx = decdeg2dm(coords.x)
            dmy = decdeg2dm(coords.y)
            return mark_safe(f"lat: {int(dmx[0])}° {format(dmx[1], '4f')}'<br>lng: {int(dmy[0])}° {format(dmy[1], '4f')}'")


class Transect(UnilingualLookup):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    site = models.ForeignKey(Site, related_name='transects', on_delete=models.DO_NOTHING, verbose_name=_("site"), editable=False)

    start_latitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("start latitude"), help_text=_("Degrees (DD)"))
    start_latitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("start latitude (minutes)"), help_text=_("Minutes (MM.mmmmm)"))
    start_longitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("start longitude"), help_text=_("Degrees (DD)"))
    start_longitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("start longitude (minutes)"), help_text=_("Minutes (MM.mmmmm)"))
    end_latitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("end latitude"), help_text=_("Degrees (DD)"))
    end_latitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("end latitude (minutes)"), help_text=_("Minutes (MM.mmmmm)"))
    end_longitude_d = models.IntegerField(blank=True, null=True, verbose_name=_("end longitude"), help_text=_("Degrees (DD)"))
    end_longitude_mm = models.FloatField(blank=True, null=True, verbose_name=_("end longitude (minutes)"), help_text=_("Minutes (MM.mmmmm)"))

    # calculated

    start_latitude = models.FloatField(blank=True, null=True, verbose_name=_("start latitude (decimal degrees)"), editable=False)
    start_longitude = models.FloatField(blank=True, null=True, verbose_name=_("start longitude (decimal degrees)"), editable=False)
    end_latitude = models.FloatField(blank=True, null=True, verbose_name=_("end latitude (decimal degrees)"), editable=False)
    end_longitude = models.FloatField(blank=True, null=True, verbose_name=_("end longitude (decimal degrees)"), editable=False)

    def save(self, *args, **kwargs):
        self.start_latitude = dm2decdeg(self.start_latitude_d, self.start_latitude_mm)
        self.start_longitude = dm2decdeg(self.start_longitude_d, self.start_longitude_mm)
        self.end_latitude = dm2decdeg(self.end_latitude_d, self.end_latitude_mm)
        self.end_longitude = dm2decdeg(self.end_longitude_d, self.end_longitude_mm)

        super().save(*args, **kwargs)

    class Meta:
        unique_together = (("name", "site"),)

    def get_starting_coordinates(self):
        if self.start_latitude and self.start_longitude:
            return dict(x=self.start_latitude, y=self.start_longitude)

    def get_ending_coordinates(self):
        if self.end_latitude and self.end_longitude:
            return dict(x=self.end_latitude, y=self.end_longitude)

    @property
    def transect_distance(self):
        if self.get_starting_coordinates() and self.get_ending_coordinates():
            dist = calc_nautical_dist(self.get_starting_coordinates(), self.get_ending_coordinates())
            return round(dist * 1852, 2)

    @property
    def starting_coordinates_ddmm(self):
        coords = self.get_starting_coordinates()
        if coords:
            dmx = decdeg2dm(coords.get("x"))
            dmy = decdeg2dm(coords.get("y"))
            return mark_safe(f"lat: {int(dmx[0])}° {format(dmx[1], '4f')}'<br>lng: {int(dmy[0])}° {format(dmy[1], '4f')}'")

    @property
    def ending_coordinates_ddmm(self):
        coords = self.get_ending_coordinates()
        if coords:
            dmx = decdeg2dm(coords.get("x"))
            dmy = decdeg2dm(coords.get("y"))
            return mark_safe(f"lat: {int(dmx[0])}° {format(dmx[1], '4f')}'<br>lng: {int(dmy[0])}° {format(dmy[1], '4f')}'")

    @property
    def has_coordinates(self):
        return self.get_starting_coordinates() and self.get_ending_coordinates()


class Diver(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("last name"))

    def __str__(self):
        mystr = f"{self.last_name}"
        if self.first_name:
            mystr += f', {self.first_name}'
        return mystr

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = [("first_name", 'last_name'), ]

    @property
    def dive_count(self):
        return self.dives.count()


class Sample(models.Model):
    site = models.ForeignKey(Site, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("site"))
    datetime = models.DateTimeField(verbose_name="date")
    weather_notes = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("weather notes"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    @property
    def site_region(self):
        return f"{self.site}, {self.site.region}"

    def __str__(self):
        return _("Sample #") + f"{self.id} - {self.site}, {self.site.region}"

    class Meta:
        ordering = ["-datetime", "site"]

    @property
    def dive_count(self):
        return self.dives.count()

    def get_absolute_url(self):
        return reverse("scuba:sample_detail", args=[self.pk])


class Dive(MetadataFields):
    heading_choices = (
        ('n', _("North")),
        ('ne', _("Northeast")),
        ('e', _("East")),
        ('se', _("Southeast")),
        ('s', _("South")),
        ('sw', _("Southwest")),
        ('w', _("West")),
        ('nw', _("Northwest")),

    )
    side_choices = (
        ('l', _("Left")),
        ('r', _("Right")),
    )
    sample = models.ForeignKey(Sample, related_name='dives', on_delete=models.CASCADE, verbose_name=_("sample"), editable=False)
    transect = models.ForeignKey(Transect, related_name='dives', on_delete=models.DO_NOTHING, verbose_name=_("transect"), blank=True, null=True,
                                 help_text=_("Leave blank if training"))
    diver = models.ForeignKey(Diver, related_name='dives', on_delete=models.DO_NOTHING, verbose_name=_("diver"))
    is_training = models.BooleanField(default=False, verbose_name=_("Was this a training dive?"), choices=YES_NO_CHOICES)
    start_descent = models.DateTimeField(verbose_name=_("start descent"), blank=True, null=True)
    bottom_time = models.FloatField(verbose_name=_("bottom time (min)"), blank=True, null=True)
    max_depth_ft = models.FloatField(verbose_name=_("max depth (ft)"), blank=True, null=True)
    psi_in = models.IntegerField(verbose_name=_("PSI in"), blank=True, null=True)
    psi_out = models.IntegerField(verbose_name=_("PSI out"), blank=True, null=True)

    heading = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("heading"), choices=heading_choices)
    side = models.CharField(max_length=1, blank=True, null=True, verbose_name=_("side"), choices=side_choices)
    width_m = models.FloatField(verbose_name=_("width (m)"), blank=True, null=True)
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["sample", "transect", "diver"]

    def __str__(self):
        return f"Dive #{self.id}"

    @property
    def observation_count(self):
        return Observation.objects.filter(section__dive=self).count()

    @property
    def dive_distance(self):
        if self.transect.get_starting_coordinates() and self.transect.get_ending_coordinates():
            dist = calc_nautical_dist(self.transect.get_starting_coordinates(), self.transect.get_ending_coordinates())
            return round(dist * 1852, 2)


class Section(MetadataFields):
    interval_choices = (
        (1, "1 (0-5m)"),
        (2, "2 (5-10m)"),
        (3, "3 (10-15m)"),
        (4, "4 (15-20m)"),
        (5, "5 (20-25m)"),
        (6, "6 (25-30m)"),
        (7, "7 (30-35m)"),
        (8, "8 (35-40m)"),
        (9, "9 (40-45m)"),
        (10, "10 (45-50m)"),
        (11, "11 (50-55m)"),
        (12, "12 (55-60m)"),
        (13, "13 (60-65m)"),
        (14, "14 (65-70m)"),
        (15, "15 (70-75m)"),
        (16, "16 (75-80m)"),
        (17, "17 (80-85m)"),
        (18, "18 (85-90m)"),
        (19, "19 (90-95m)"),
        (20, "20 (95-100m)"),
    )

    dive = models.ForeignKey(Dive, related_name='sections', on_delete=models.CASCADE, verbose_name=_("dive"))
    interval = models.IntegerField(verbose_name=_("5m interval [1-20]"), validators=(MinValueValidator(1), MaxValueValidator(20)), choices=interval_choices)
    depth_ft = models.FloatField(verbose_name=_("depth (ft)"), blank=True, null=True)
    percent_algae = models.FloatField(default=0, verbose_name=_("algae [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_sand = models.FloatField(default=0, verbose_name=_("sand [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_mud = models.FloatField(default=0, verbose_name=_("mud [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_hard = models.FloatField(default=0, verbose_name=_("hard [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_gravel = models.FloatField(default=0, verbose_name=_("gravel [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_cobble = models.FloatField(default=0, verbose_name=_("cobble [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_pebble = models.FloatField(default=0, verbose_name=_("pebble [0-1]"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    class Meta:
        ordering = ["interval", ]
        unique_together = (("dive", "interval"),)

    @property
    def substrate_profile(self):
        my_str = ""
        substrates = [
            "sand",
            "mud",
            "hard",
            "algae",
            "gravel",
            "cobble",
            "pebble",
        ]
        substrates_string = [
            gettext("sand"),
            gettext("mud"),
            gettext("hard"),
            gettext("algae"),
            gettext("gravel"),
            gettext("cobble"),
            gettext("pebble"),
        ]
        for substrate in substrates:
            attr = getattr(self, f"percent_{substrate}")
            substrate = gettext(substrate)
            if attr and attr > 0:
                my_str += f"{int(attr * 100)}% {substrate}<br> "

        return mark_safe(my_str)


class Observation(MetadataFields):
    sex_choices = (
        ('u', _("0 - unknown")),
        ('m', _("1 - male")),
        ('f', _("2 - female")),
    )
    egg_status_choices = (
        ("0", _("0 - no eggs")),
        ("b", _("b - berried")),
        ("b1", _("b1 - berried with new eggs")),
        ("b2", _("b2 - berried with black eggs")),
        ("b3", _("b3 - berried with developed eggs")),
    )
    certainty_rating_choices = (
        (1, _("1 - certain")),
        (0, _("0 - uncertain")),
    )
    section = models.ForeignKey(Section, related_name='observations', on_delete=models.CASCADE, verbose_name=_("section"))
    carapace_length_mm = models.FloatField(verbose_name=_("carapace length (mm)"), blank=True, null=True)
    sex = models.CharField(max_length=2, verbose_name=_("sex"), choices=sex_choices)
    egg_status = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("egg status"), choices=egg_status_choices)
    certainty_rating = models.IntegerField(verbose_name=_("length certainty"), default=1, choices=certainty_rating_choices)
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='scuba_obs_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False, related_name='scuba_obs_updated_by')

    @property
    def sex_special_display(self):
        try:
            return self.get_sex_display().split("-")[1].strip()
        except Exception as e:
            pass

    @property
    def egg_status_special_display(self):
        try:
            if self.get_egg_status_display():
                return self.get_egg_status_display().split("-")[1].strip()
        except:
            pass

    @property
    def certainty_rating_special_display(self):
        try:
            return self.get_certainty_rating_display().split("-")[1].strip()
        except:
            pass
