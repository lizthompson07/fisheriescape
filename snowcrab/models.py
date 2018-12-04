from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth


class Vessel(models.Model):
    # choices for hull_material
    WOOD = 'wood'
    FIBER = 'fiberglass'
    STEEL = 'steel'
    HULL_MATERIAL_CHOICES = (
        (WOOD, WOOD),
        (FIBER, FIBER),
        (STEEL, STEEL),
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    cvrn = models.IntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    horsepower = models.IntegerField(blank=True, null=True)
    hull_material = models.CharField(max_length=25, blank=True, null=True, choices=HULL_MATERIAL_CHOICES )

    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']




class Cruise(models.Model):
    # choices for trawl_type
    NEPH = 'Nephrops'
    TRAWL_TYPE_CHOICES = (
        (NEPH,'Nephrops'),
    )

    # choices for trawl_method
    SIDE = 'side'
    STERN = 'stern'
    TRAWL_METHOD_CHOICES = (
        (SIDE, SIDE),
        (STERN, STERN),
    )

    # choices for season
    SUMMER = 'summer'
    FALL = 'fall'
    SEASON_CHOICES = (
        (FALL, FALL),
        (SUMMER, SUMMER),
    )

    # choices for acoustic_sensor
    SCAN = 'Scanmar'
    NET = 'Netmind'
    ESONAR = 'eSonar'
    ACOUSTIC_SENSOR_CHOICES = (
        (SCAN, SCAN),
        (NET, NET),
        (ESONAR, ESONAR),
    )

    vessel = models.ForeignKey(Vessel, related_name="cruises", on_delete=models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trawl_type = models.CharField(max_length=56, blank=True, null=True,choices=TRAWL_TYPE_CHOICES)
    trawl_method = models.CharField(max_length=56, blank=True, null=True, choices=TRAWL_METHOD_CHOICES)
    acoustic_sensor = models.CharField(max_length=56, blank=True, null=True , choices=ACOUSTIC_SENSOR_CHOICES)
    minilog = models.NullBooleanField(blank=True, null=True)
    star_oddi = models.NullBooleanField(blank=True, null=True)
    chief_scientist = models.CharField(max_length=255, blank=True, null=True)
    season = models.CharField(null=True, blank=True, max_length=25, choices=SEASON_CHOICES)
    year = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        self.year = self.start_date.year
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.season, self.year)

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
    cruise = models.ForeignKey(Cruise, related_name="sets", on_delete=models.DO_NOTHING)
    set_name = models.CharField(blank=True, null=True, max_length=56, verbose_name="Tow ID string")
    set_number = models.IntegerField(blank=True, null=True, verbose_name="Daily tow number")
    year = models.IntegerField(blank=True, null=True, verbose_name="Survey year")
    month = models.IntegerField(blank=True, null=True, verbose_name="Survey month")
    day = models.IntegerField(blank=True, null=True, verbose_name="Survey calendar day")
    zone = models.ForeignKey(Zone, related_name="sets", on_delete=models.DO_NOTHING, blank=True, null=True)
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

    class Meta:
        ordering = ['start_time_logbook']

    def __str__(self):
        return "Set {}".format(self.set_name)

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
    position_type = models.CharField(max_length=2, blank=True, null=True)
    missing_legs = models.CharField(max_length=10, blank=True, null=True)
    durometer = models.FloatField(blank=True, null=True)
    samplers = models.CharField(max_length=1000, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Crab {}".format(self.crab_number)

    class Meta:
        ordering = ['crab_number']