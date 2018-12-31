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
        return "{} - {}".format(self.id, self.common_name_eng)

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('diets:species_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        self.last_modified_date = timezone.now()
        return super().save(*args, **kwargs)


class Predator(models.Model):
    sequence_number = models.IntegerField(blank=True, null=True)
    fish_number = models.IntegerField(blank=True, null=True)
    species = models.ForeignKey(Species, related_name='predators', on_delete=models.DO_NOTHING)
    processing_date = models.DateTimeField(verbose_name="processing date (yyyy-mm-dd)", blank=True, null=True)
    sampler = models.CharField(max_length=500, blank=True, null=True)
    cruise = models.ForeignKey(Cruise, related_name='predators', on_delete=models.DO_NOTHING, blank=True, null=True)
    set = models.IntegerField(blank=True, null=True)
    stratum = models.IntegerField(blank=True, null=True)
    collection_date = models.DateTimeField(verbose_name="collection date (yyyy-mm-dd)", blank=True, null=True)
    collection_year = models.IntegerField(blank=True, null=True)
    collection_month = models.IntegerField(blank=True, null=True)
    collection_day = models.IntegerField(blank=True, null=True)
    somatic_length_mm = models.FloatField(null=True, blank=True, verbose_name="somatic length (mm)")
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="somatic weight (g)")
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")
    comments = models.TextField(blank=True, null=True)
    old_seq_num = models.IntegerField(blank=True, null=True)
    prey_items = models.ManyToManyField(Species, through="Prey")

    class Meta:
        ordering = ['cruise', 'species']

    def __str__(self):
        return "{}".format(self.species)


class Prey(models.Model):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, )
    predator = models.ForeignKey(Predator, on_delete=models.DO_NOTHING, )
    digestion_level = models.IntegerField(blank=True, null=True)
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="somatic weight (g)")
    somatic_length_mm = models.FloatField(null=True, blank=True, verbose_name="somatic length (mm)")
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")

    class Meta:
        unique_together = [["species", "predator"], ]
