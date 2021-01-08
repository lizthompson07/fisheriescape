from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext

from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup


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


class Site(UnilingualLookup):
    abbreviation = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("abbreviation"))
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name='sites', verbose_name=_("region"), editable=False)
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("longitude"))

    def __str__(self):
        return f"Site {self.name}"

    @property
    def transect_count(self):
        return self.transects.count()


class Transect(UnilingualLookup):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    site = models.ForeignKey(Site, related_name='transects', on_delete=models.DO_NOTHING, verbose_name=_("site"), editable=False)

    class Meta:
        unique_together = (("name", "site"),)


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


class Dive(models.Model):
    heading_choices = (
        ('n', _("North")),
        ('s', _("South")),
        ('e', _("East")),
        ('w', _("West")),
    )
    side_choices = (
        ('l', _("Left")),
        ('r', _("Right")),
    )
    sample = models.ForeignKey(Sample, related_name='dives', on_delete=models.CASCADE, verbose_name=_("sample"), editable=False)
    transect = models.ForeignKey(Transect, related_name='dives', on_delete=models.DO_NOTHING, verbose_name=_("transect"))
    diver = models.ForeignKey(Diver, related_name='dives', on_delete=models.DO_NOTHING, verbose_name=_("diver"))
    start_descent = models.DateTimeField(verbose_name=_("start descent"), blank=True, null=True)
    bottom_time = models.FloatField(verbose_name=_("bottom time (min)"), blank=True, null=True)
    max_depth_ft = models.FloatField(verbose_name=_("max depth (ft)"), blank=True, null=True)
    psi_in = models.IntegerField(verbose_name=_("PSI in"), blank=True, null=True)
    psi_out = models.IntegerField(verbose_name=_("PSI out"), blank=True, null=True)
    heading = models.CharField(max_length=1, blank=True, null=True, verbose_name=_("heading"), choices=heading_choices)
    side = models.CharField(max_length=1, blank=True, null=True, verbose_name=_("side"), choices=side_choices)
    width_m = models.FloatField(verbose_name=_("width (m)"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    class Meta:
        ordering = ["sample", "transect", "diver"]

    def __str__(self):
        return f"Dive #{self.id}"

    @property
    def observation_count(self):
        return Observation.objects.filter(section__dive=self).count()


class Section(models.Model):
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
    interval = models.IntegerField(verbose_name=_("5m interval (1-20)"), validators=(MinValueValidator(1), MaxValueValidator(20)), choices=interval_choices)
    depth_ft = models.FloatField(verbose_name=_("depth (ft)"), blank=True, null=True)
    percent_sand = models.FloatField(default=0, verbose_name=_("% sand"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_mud = models.FloatField(default=0, verbose_name=_("% mud"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_hard = models.FloatField(default=0, verbose_name=_("% hard"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_algae = models.FloatField(default=0, verbose_name=_("% algae"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_gravel = models.FloatField(default=0, verbose_name=_("% gravel"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_cobble = models.FloatField(default=0, verbose_name=_("% cobble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_pebble = models.FloatField(default=0, verbose_name=_("% pebble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
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


class Observation(models.Model):
    sex_choices = (
        ('m', _("male")),
        ('f', _("female")),
        ('i', _("immature")),
        ('u', _("unknown")),
    )
    egg_status_choices = (
        (None, _("n/a")),
        ("b", _("b (berried)")),
        ("b1", _("b1 (berried with new eggs)")),
        ("b2", _("b2 (berried with black eggs)")),
        ("b3", _("b3 (berried with developed eggs)")),
    )
    certainty_rating_choices = (
        (1, _("certain")),
        (0, _("uncertain")),
    )
    section = models.ForeignKey(Section, related_name='observations', on_delete=models.CASCADE, verbose_name=_("section"))
    sex = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("sex"), choices=sex_choices)
    egg_status = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("eggs status"), choices=egg_status_choices)
    carapace_length_mm = models.FloatField(verbose_name=_("carapace length (mm)"), blank=True, null=True)
    certainty_rating = models.IntegerField(verbose_name=_("certainty rating"), default=1, choices=certainty_rating_choices)
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))
