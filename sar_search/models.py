from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _
from shared_models import models as shared_models


class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    life_stage_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="life stage name (English)")
    life_stage_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="life stage name (French)")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    province_range = models.ManyToManyField(shared_models.Province)
    notes = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        if getattr(self, str(_("life_stage_eng"))):
            return "{} ({})".format(
                getattr(self, str(_("common_name_eng"))),
                getattr(self, str(_("life_stage_eng"))).lower(),
            )
        else:
            return getattr(self, str(_("common_name_eng")))

    @property
    def full_name(self):
        if getattr(self, str(_("life_stage_eng"))):
            return "{} ({})".format(
                getattr(self, str(_("common_name_eng"))),
                getattr(self, str(_("life_stage_eng"))).lower(),
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

    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name='sar_sites', blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name=_("site name"))
    range_type = models.IntegerField(verbose_name="range type", choices=RANGE_TYPE_CHOICES)
    source = models.CharField(max_length=1000, verbose_name=_("source"))

    class Meta:
        ordering = ['species', 'name']


class RangePoints(models.Model):
    range = models.ForeignKey(Range, on_delete=models.DO_NOTHING, related_name='points', blank=True, null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['range',]


