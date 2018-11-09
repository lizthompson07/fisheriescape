from django.db import models
# from django.urls import reverse
from django.utils import timezone
from django.contrib import auth


class Province(models.Model):
    province_eng = models.CharField(max_length=255, blank=True, null=True)
    province_fre = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.province, self.abbrev)

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


class Station(models.Model):
    name = models.CharField(max_length=56)
    site = models.ForeignKey('Site', on_delete=models.DO_NOTHING, related_name='stations', blank=True,
                                 null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Site #{} @ {}".format(self.id, self.site.code)



class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True)
    common_name_fre = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    notes = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.common_name_eng

    class Meta:
        ordering = ['common_name_eng']


class Sample(models.Model):
    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    sample_start_date = models.DateTimeField(blank=True, null=True)
    sample_end_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="camp_sample_last_modified_by")

    def save(self, *args, **kwargs):
        self.year = self.sample_start_date.year
        self.month = self.sample_start_date.month
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-sample_start_date']


# class Stage(models.Model):
#     code = models.TextField(max_length=5)
#     desc_eng = models.TextField(max_length=5)
#     desc_fre = models.TextField(max_length=5, null=True, blank=True)


class SpeciesObservations(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="sample_spp")
    sample = models.ForeignKey(Sample, on_delete=models.DO_NOTHING, related_name="sample_spp")
    count_adults = models.IntegerField(default=0)
    count_yoy = models.IntegerField(default=0)
    count_unknown = models.IntegerField(default=0)
    count_total = models.IntegerField(null=True, blank=True)

    def save(self):
        self.count_total = self.count_adults + self.count_yoy + self.count_unknown
        return super().save()
