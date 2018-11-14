from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth


class Province(models.Model):
    province_eng = models.CharField(max_length=255, blank=True, null=True)
    province_fre = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.province_eng, self.abbrev)

class Site(models.Model):
    site = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    province = models.ForeignKey('Province', on_delete=models.DO_NOTHING, related_name='sites', blank=True,
                                 null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.site, self.province.abbrev)

    class Meta:
        ordering = ['province', 'site']

    def get_absolute_url(self):
        return reverse("camp:site_detail", kwargs={"pk": self.id})

class Station(models.Model):
    name = models.CharField(max_length=255)
    site = models.ForeignKey('Site', on_delete=models.DO_NOTHING, related_name='stations', blank=True,
                                 null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    station_number = models.IntegerField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("camp:station_detail", kwargs={"pk": self.id})


    def __str__(self):
        return "{}".format(self.name)



class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name="english name")
    common_name_fre = models.CharField(max_length=255, blank=True, null=True, verbose_name="french name")
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    notes = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.common_name_eng

    class Meta:
        ordering = ['common_name_eng']

    def get_absolute_url(self):
        return reverse("camp:species_detail", kwargs={"pk": self.id})


class Sample(models.Model):
    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    sample_start_date = models.DateTimeField()
    sample_end_date = models.DateTimeField(blank=True, null=True)
    temperature_c = models.FloatField(null=True,blank=True, verbose_name="Temperature (°C)")
    salinity = models.FloatField(null=True,blank=True, verbose_name="Salinity (ppt)")
    disolved_o2 = models.FloatField(null=True,blank=True, verbose_name="dissolved oxygen (?mgl?)")
    per_sediment_water_cont = models.FloatField(null=True,blank=True, verbose_name="sediment water content (%)")
    per_sediment_organic_cont = models.FloatField(null=True,blank=True, verbose_name="sediment organic content (%)")
    mean_sediment_grain_size = models.FloatField(null=True,blank=True, verbose_name="Mean sediment grain size (??)") # where 9999 means >2000
    silicate = models.FloatField(null=True,blank=True, verbose_name="Silicate (µM)")
    phosphate = models.FloatField(null=True,blank=True, verbose_name="Phosphate (µM)")
    nitrates = models.FloatField(null=True,blank=True, verbose_name="NO3 + NO2(µM)")
    nitrite = models.FloatField(null=True,blank=True, verbose_name="Nitrite (µM)")
    ammonia = models.FloatField(null=True,blank=True, verbose_name="Ammonia (µM)")
    notes = models.TextField(blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    species = models.ManyToManyField(Species, through="SpeciesObservations")

    def save(self, *args, **kwargs):
        self.year = self.sample_start_date.year
        self.month = self.sample_start_date.month
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-sample_start_date', 'station']
        unique_together = [["sample_start_date","station"],]


class SpeciesObservations(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="sample_spp")
    sample = models.ForeignKey(Sample, on_delete=models.DO_NOTHING, related_name="sample_spp")
    adults = models.FloatField(default=0)
    yoy = models.FloatField(default=0)
    unknown = models.FloatField(default=0)
    total = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total = self.adults + self.yoy + self.unknown
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = [["sample","species"],]
        # ordering = ["-sample__year"] THIS IS WAY TOO SLOW!