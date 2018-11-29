from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth


class Vessel(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    cvrn = models.IntegerField(blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Cruise(models.Model):
    cruise_number = models.CharField(max_length=25)
    mission_number = models.CharField(max_length=25)
    vessel = models.ForeignKey(Vessel, related_name="cruises", on_delete=models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    chief_scientist = models.CharField(max_length=255)
    remarks = models.TextField(null=True, blank=True)
    season = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        self.season = self.start_date.year
        self.cruise_number = self.cruise_number.upper()
        self.mission_number = self.mission_number.upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.mission_number

    def get_absolute_url(self):
        return reverse('fish:cruise_detail', kwargs={'pk': self.id})


class Zone(models.Model):
    zone_name = models.CharField(max_length=255)
    nafo_area_code = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.zone_name

    class Meta:
        ordering = ['zone_name']


class Set(models.Model):
    # Choices for swept area method
    MOD = 'mod'
    AVG = 'avg'
    SWEPT_AREA_METHOD = (
        (MOD, "model"),
        (AVG, "average"),
    )

    cruise = models.ForeignKey(Cruise, related_name="sets", on_delete=models.DO_NOTHING, blank=True, null=True)
    set_name = models.CharField(blank=True, null=True, max_length=56, verbose_name="Tow ID string")
    set_number = models.IntegerField(blank=True, null=True, verbose_name="Daily tow number")
    year = models.IntegerField(blank=True, null=True, verbose_name="Survey year")
    month = models.IntegerField(blank=True, null=True, verbose_name="Survey month")
    day = models.IntegerField(blank=True, null=True, verbose_name="Survey calendar day")
    zone = models.ForeignKey(Zone, related_name="sets", on_delete=models.DO_NOTHING)
    valid = models.NullBooleanField(verbose_name="Tow quality(i.e. is it valid?)", blank=True, null=True)
    latitude_start_logbook = models.FloatField(blank=True, null=True,
                                               verbose_name="Start latitude decimal degrees from logbook")
    latitude_end_logbook = models.FloatField(blank=True, null=True,
                                             verbose_name="End latitude decimal degrees from logbook")
    longitude_start_logbook = models.FloatField(blank=True, null=True,
                                                verbose_name="Start longitude decimal degrees from logbook")
    longitude_end_logbook = models.FloatField(blank=True, null=True,
                                              verbose_name="End longitude decimal degrees from logbook")
    latitude_start = models.FloatField(blank=True, null=True,
                                       verbose_name="Start latitude decimal degrees")
    latitude_end = models.FloatField(blank=True, null=True,
                                     verbose_name="End latitude decimal degrees")
    longitude_start = models.FloatField(blank=True, null=True,
                                        verbose_name="Start longitude decimal degrees")
    longitude_end = models.FloatField(blank=True, null=True,
                                      verbose_name="End longitude decimal degrees")
    start_time_logbook = models.DateTimeField(blank=True, null=True,
                                              verbose_name="Trawl start time from logbook (hh:mm:ss)")
    end_time_logbook = models.DateTimeField(blank=True, null=True,
                                            verbose_name="Trawl end time from logbook (hh:mm:ss)")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="Trawl start time (hh:mm:ss)")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="Trawl end time (hh:mm:ss)")
    depth_logbook = models.FloatField(blank=True, null=True, verbose_name="Observed water depth( in fathoms)")
    bottom_temperature_logbook = models.FloatField(blank=True, null=True, verbose_name="Bottom water temperature")
    warp_logbook = models.IntegerField(blank=True, null=True, verbose_name="Trawl warp length(in fathoms)")
    swept_area = models.FloatField(blank=True, null=True, verbose_name="Tow swept area(square meters)")
    swept_area_method = models.CharField(max_length=255, choices=SWEPT_AREA_METHOD, blank=True, null=True,
                                         verbose_name="Swept-area calculation method")
    comment = models.TextField(blank=True, null=True, verbose_name="Tow comments")


class Sex(models.Model):
    sex = models.CharField(max_length=255)

    def __str__(self):
        return self.sex


class Crab(models.Model):
    set = models.ForeignKey(Set, on_delete=models.DO_NOTHING, related_name="crabs")
    crab_number = models.IntegerField(blank=True, null=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="crabs")
    carapace_width = models.FloatField(blank=True, null=True)
    abdomen_width = models.FloatField(blank=True, null=True)
    chela_height = models.FloatField(blank=True, null=True)
    maturity = models.CharField(max_length=255, blank=True, null=True)
    shell_condition = models.CharField(max_length=2, blank=True, null=True)
    gonad_colour = models.IntegerField(blank=True, null=True)
    egg_colour = models.IntegerField(blank=True, null=True)
    eggs_remaining = models.IntegerField(blank=True, null=True)
    tag_number = models.IntegerField(blank=True, null=True)
    missing_legs = models.CharField(max_length=10, blank=True, null=True)
    durometer = models.FloatField(blank=True, null=True)
    samplers = models.CharField(max_length=1000, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
