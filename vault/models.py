from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from shared_models import models as shared_models


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

    @property
    def full_name(self):
        return "{} (<em>{}</em>)".format(self.common_name_eng, self.scientific_name)


class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        ordering = ['first_name', 'last_name']


class Predator(models.Model):
    cruise = models.ForeignKey(shared_models.Cruise, related_name='predators', on_delete=models.DO_NOTHING, blank=True, null=True)
    samplers = models.ManyToManyField(Sampler, blank=True)
    stomach_id = models.CharField(max_length=10, blank=True, null=True, verbose_name="stomach ID", unique=True)
    processing_date = models.DateTimeField(verbose_name="processing date", default=timezone.now, blank=True, null=True)
    set = models.IntegerField(blank=True, null=True)
    species = models.ForeignKey(Species, related_name='predators', on_delete=models.DO_NOTHING, verbose_name="predator species")
    fish_number = models.IntegerField(blank=True, null=True)
    somatic_length_cm = models.FloatField(null=True, blank=True, verbose_name="body length (cm)")
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")
    content_wt_g = models.FloatField(null=True, blank=True, verbose_name="content weight (g)")
    comments = models.TextField(blank=True, null=True)

    # not actively used
    stratum = models.IntegerField(blank=True, null=True)
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="body weight (g)")
    old_seq_num = models.IntegerField(blank=True, null=True)
    # meta
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    # TODO: IN FUTURE YEARS COMBO OF YEAR AND STOMACH ID SHOULD BE UNIQUE

    class Meta:
        ordering = ['-processing_date', ]

    def __str__(self):
        return " Predator {}".format(self.id)

    def get_absolute_url(self):
        return reverse('diets:predator_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        if self.stomach_id:
            self.stomach_id = self.stomach_id.upper()
        return super().save(*args, **kwargs)

    @property
    def season(self):
        return self.processing_date.year


class DigestionLevel(models.Model):
    code = models.IntegerField(unique=True)
    level = models.CharField(max_length=150)
    interpretation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{}-{}".format(self.code, self.level)


class Prey(models.Model):
    predator = models.ForeignKey(Predator, on_delete=models.DO_NOTHING, related_name="prey_items")
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="prey_items")
    digestion_level = models.ForeignKey(DigestionLevel, on_delete=models.DO_NOTHING, blank=True, null=True)
    somatic_length_mm = models.FloatField(null=True, blank=True, verbose_name="body length (mm)")
    length_comment = models.CharField(max_length=250, blank=True, null=True)
    number_of_prey = models.IntegerField(blank=True, null=True, verbose_name="number of prey")
    somatic_wt_g = models.FloatField(null=True, blank=True, verbose_name="body weight (g)")
    comments = models.TextField(blank=True, null=True)

    # not used
    censored_length = models.BooleanField(default=False)
    stomach_wt_g = models.FloatField(null=True, blank=True, verbose_name="stomach weight (g)")

    # meta
    old_id = models.IntegerField(blank=True, null=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now)

