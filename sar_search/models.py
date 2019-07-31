from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from shared_models import models as shared_models


class Taxon(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class SARASchedule(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))
    description_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("english description"))
    description_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("french description"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class SpeciesStatus(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))
    description_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("english description"))
    description_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("french description"))

    def __str__(self):
        return "{} - {}".format(self.code, getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class County(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='counties')

    def __str__(self):
        name = getattr(self, str(_("name"))) if getattr(self, str(_("name"))) else self.name
        return "{}, {}".format(name, self.province.tabbrev)

    class Meta:
        ordering = ['name', ]


class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, verbose_name="name (English)")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="name (French)")
    population_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="population (English)")
    population_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="population (French)")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    taxon = models.ForeignKey(Taxon, on_delete=models.DO_NOTHING, related_name='spp', blank=True, null=True)
    sara_status = models.ForeignKey(SpeciesStatus, on_delete=models.DO_NOTHING, related_name='sara_spp', verbose_name=_("COSEWIC status"),
                                    blank=True, null=True)
    cosewic_status = models.ForeignKey(SpeciesStatus, on_delete=models.DO_NOTHING, related_name='cosewic_spp',
                                       verbose_name=_("SARA status"), blank=True, null=True)
    sara_schedule = models.ForeignKey(SARASchedule, on_delete=models.DO_NOTHING, related_name='spp', verbose_name=_("SARA schedule"),
                                      blank=True, null=True)
    province_range = models.ManyToManyField(shared_models.Province, blank=True)
    notes = models.TextField(max_length=255, null=True, blank=True)

    # metadata
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"), related_name="sar_spp")

    def get_absolute_url(self):
        return reverse("sar_search:species_detail", kwargs={"pk": self.id})

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        if getattr(self, str(_("population_eng"))):
            return "{} ({})".format(
                getattr(self, str(_("common_name_eng"))),
                getattr(self, str(_("population_eng"))).lower(),
            )
        else:
            return getattr(self, str(_("common_name_eng")))

    @property
    def full_name(self):
        if getattr(self, str(_("population_eng"))):
            return "{} ({})".format(
                getattr(self, str(_("common_name_eng"))),
                getattr(self, str(_("population_eng"))).lower(),
            )
        else:
            return getattr(self, str(_("common_name_eng")))

    class Meta:
        ordering = ['common_name_eng']


class Range(models.Model):
    # choice for range type:
    POINT = 1
    LINE = 2
    POLYGON = 3
    RANGE_TYPE_CHOICES = (
        (POINT, "point"),
        (LINE, "line"),
        (POLYGON, "polygon"),
    )

    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name='ranges', blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name=_("range name"))
    county = models.ForeignKey(County, on_delete=models.DO_NOTHING, related_name='ranges', blank=True, null=True)
    range_type = models.IntegerField(verbose_name=_("range type"), choices=RANGE_TYPE_CHOICES)
    source = models.CharField(max_length=1000, verbose_name=_("source"))

    # metadata
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))

    def __str__(self):
        return getattr(self, str(_("name"))) if getattr(self, str(_("name"))) else self.name

    class Meta:
        ordering = ['species', 'name']

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        return super().save(*args, **kwargs)


class RangePoints(models.Model):
    range = models.ForeignKey(Range, on_delete=models.DO_NOTHING, related_name='points', blank=True, null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['range', ]
