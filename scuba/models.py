from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

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


class Sample(models.Model):
    site = models.ForeignKey(Site, related_name='samples', on_delete=models.DO_NOTHING, verbose_name=_("site"))
    datetime = models.DateTimeField(verbose_name="date / time (yyyy-mm-dd hh:mm)")
    weather_notes = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("weather notes"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    @property
    def site_region(self):
        return f"{self.site}, {self.site.region}"

    def __str__(self):
        return f"Sample #{self.id} - {self.site}, {self.site.region}"

    class Meta:
        ordering = ["-datetime", "site"]


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
    heading = models.CharField(max_length=1, blank=True, null=True, verbose_name=_("heading"), choices=heading_choices)
    side = models.CharField(max_length=1, blank=True, null=True, verbose_name=_("side"), choices=side_choices)
    width_m = models.FloatField(verbose_name=_("width (m)"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    class Meta:
        ordering = ["sample", "transect", "diver"]

    def __str__(self):
        return f"Dive #{self.id}"

class Section(models.Model):
    dive = models.ForeignKey(Dive, related_name='sections', on_delete=models.CASCADE, verbose_name=_("dive"))
    interval = models.IntegerField(verbose_name=_("5m interval (1-20)"), validators=(MinValueValidator(1), MaxValueValidator(20)))
    depth_ft = models.FloatField(verbose_name=_("depth (ft)"), blank=True, null=True)
    percent_sand = models.FloatField(default=0, verbose_name=_("% sand"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_mud = models.FloatField(default=0, verbose_name=_("% mud"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_solid = models.FloatField(default=0, verbose_name=_("% rock"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_algae = models.FloatField(default=0, verbose_name=_("% algae"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_gravel = models.FloatField(default=0, verbose_name=_("% gravel"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_cobble = models.FloatField(default=0, verbose_name=_("% cobble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    percent_pebble = models.FloatField(default=0, verbose_name=_("% pebble"), validators=(MinValueValidator(0), MaxValueValidator(1)))
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))

    @property
    def substrate_profile(self):
        my_str = ""
        substrates = [
            "sand",
            "mud",
            "solid",
            "algae",
            "gravel",
            "cobble",
            "pebble",
        ]
        for substrate in substrates:
            attr = getattr(self, f"percent_{substrate}")
            if attr and attr > 0:
                my_str += f"{int(attr*100)}% {substrate}<br> "

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
    section = models.ForeignKey(Section, related_name='observations', on_delete=models.CASCADE, verbose_name=_("section"))
    sex = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("sex"), choices=sex_choices)
    egg_status = models.CharField(max_length=2, blank=True, null=True, verbose_name=_("eggs status"), choices=egg_status_choices)
    carapace_length_mm = models.FloatField(verbose_name=_("carapace length (mm)"), blank=True, null=True)
    comment = models.TextField(null=True, blank=True, verbose_name=_("comment"))
