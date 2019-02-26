from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Vessel(models.Model):
    name = models.CharField(max_length=255)
    call_sign = models.CharField(max_length=56, null=True, blank=True)

    def __str__(self):
        if self.call_sign:
            return "{} {}".format(self.name, self.call_sign)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Cruise(models.Model):
    cruise_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    chief_scientist = models.CharField(max_length=255)
    samplers = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    season = models.IntegerField(null=True, blank=True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, related_name="missions", blank=True, null=True)

    def __str__(self):
        return "{}".format(self.cruise_number)

    def get_absolute_url(self):
        return reverse('diets:cruise_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if self.start_date:
            self.season = self.start_date.year
        return super().save(*args, **kwargs)


class Species(models.Model):
    common_name_eng = models.CharField(max_length=255, blank=True, null=True)
    common_name_fre = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="ITIS TSN")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")

    def __str__(self):
        if self.common_name_eng:
            return "{}-{}".format(self.id, self.common_name_eng)
        else:
            return "{}-{}".format(self.id, self.scientific_name)

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('diets:species_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        self.last_modified_date = timezone.now()
        return super().save(*args, **kwargs)


class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        ordering = ['first_name', 'last_name']


class Predator(models.Model):
    cruise = models.ForeignKey(Cruise, related_name='predators', on_delete=models.DO_NOTHING)
    processing_date = models.DateTimeField(verbose_name="processing date (yyyy-mm-dd)", default=timezone.now)
    species = models.ForeignKey(Species, related_name='predators', on_delete=models.DO_NOTHING)
    set = models.IntegerField(blank=True, null=True)
    stratum = models.IntegerField(blank=True, null=True)
    fish_number = models.IntegerField(blank=True, null=True)
    samplers = models.ManyToManyField(Sampler)
    # sampler = models.CharField(max_length=500, blank=True, null=True)
    somatic_length_cm = models.FloatField(null=True, blank=True, verbose_name="body length (cm)")
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="body weight (g)")
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")
    content_wt_g = models.FloatField(null=True, blank=True, verbose_name="content weight (g)")
    comments = models.TextField(blank=True, null=True)
    old_seq_num = models.IntegerField(blank=True, null=True)
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['-processing_date', 'species']

    def __str__(self):
        return " Predator {}".format(self.id)

    def get_absolute_url(self):
        return reverse('diets:predator_detail', kwargs={'pk': self.id})


class DigestionLevel(models.Model):
    code = models.IntegerField(unique=True)
    level = models.CharField(max_length=150)
    interpretation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{}-{}".format(self.code, self.level)


class Prey(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, )
    predator = models.ForeignKey(Predator, on_delete=models.DO_NOTHING, related_name="prey_items")
    digestion_level = models.ForeignKey(DigestionLevel, on_delete=models.DO_NOTHING, blank=True, null=True)
    number_of_prey = models.IntegerField(blank=True, null=True, verbose_name="number of prey")
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="body weight (g)")
    somatic_length_mm = models.FloatField(null=True, blank=True, verbose_name="body length (mm)")
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")
    sensor_used = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)