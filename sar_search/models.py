from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from shared_models import models as shared_models
from shapely.geometry import Polygon


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
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"),
                                         related_name="sar_spp")

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


class Record(models.Model):
    # choice for record type:
    POINT = 1
    LINE = 2
    POLYGON = 3
    RANGE_TYPE_CHOICES = (
        (POINT, "point"),
        (LINE, "line"),
        (POLYGON, "polygon"),
    )

    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name='records', blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name=_("record name"))
    counties = models.ManyToManyField(County, blank=True)
    record_type = models.IntegerField(verbose_name=_("record type"), choices=RANGE_TYPE_CHOICES)
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

    def get_polygon(self):
        if self.record_type in [2, 3] and self.points.count() > 0:
            point_list = [(point.latitude_n, point.longitude_w) for point in self.points.all()]
            return Polygon(point_list)

    def coords(self):
        if self.record_type == 1 and self.points.count() > 0:
            return {"x": self.points.first().latitude_n,
                    "y": self.points.first().longitude_w}
        elif self.record_type in [2, 3] and self.points.count() > 0:
            my_polygon = self.get_polygon()
            return {"x": my_polygon.centroid.coords[0][0],
                    "y": my_polygon.centroid.coords[0][1]}


class RecordPoints(models.Model):
    record = models.ForeignKey(Record, on_delete=models.DO_NOTHING, related_name='points', blank=True, null=True)
    # record = models.IntegerField(blank=True, null=True)
    latitude_n = models.FloatField()
    longitude_w = models.FloatField()

    class Meta:
        ordering = ['record', ]

    def save(self, *args, **kwargs):
        if self.longitude_w and self.longitude_w > 0:
            self.longitude_w = -self.longitude_w
        return super().save(*args, **kwargs)
