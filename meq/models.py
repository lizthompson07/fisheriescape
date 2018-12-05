from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    organization = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('grais:person_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['first_name', 'last_name']

class Province(models.Model):
    province = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.province, self.abbrev)


class Site(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    province = models.ForeignKey('Province', on_delete=models.DO_NOTHING, blank=True, null=True)
    site_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['province', 'name']


class Station(models.Model):
    site = models.ForeignKey('Site', on_delete=models.DO_NOTHING, related_name='stations')
    name = models.CharField(max_length=255, blank=True, null=True)
    latitude_n = models.FloatField(blank=True, null=True)
    longitude_w = models.FloatField(blank=True, null=True)
    depth = models.FloatField(blank=True, null=True)
    site_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['site', 'name']


class Sample(models.Model):
    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    date_deployed = models.DateTimeField()
    date_retrieved = models.DateTimeField(blank=True, null=True)
    days_deployed = models.IntegerField(null=True, blank=True)
    samplers = models.ManyToManyField(Sampler)
    year = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.year = self.date_deployed.year
        if self.date_retrieved != None:
            self.days_deployed = (self.date_retrieved - self.date_deployed).days
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Sample {}".format(self.id)

    class Meta:
        ordering = ['-year', 'station', '-date_deployed']

class Probe(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProbeMeasurement(models.Model):
    # Choices for tide_descriptor
    EBB = 'eb'
    FLOOD = 'fl'
    HIGH = 'hi'
    LOW = 'lo'
    TIDE_DESCRIPTOR_CHOICES = (
        (EBB, 'Ebb'),
        (FLOOD, 'Flood'),
        (HIGH, 'High'),
        (LOW, 'Low'),
    )

    # Choices for timezone
    AST = 'AST'
    ADT = 'ADT'
    UTC = 'UTC'
    TIMEZONE_CHOICES = (
        (AST, 'AST'),
        (ADT, 'ADT'),
        (UTC, 'UTC'),
    )

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="probe_data")
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING)
    time_date = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=5, choices=TIMEZONE_CHOICES, blank=True, null=True)
    tide_descriptor = models.CharField(max_length=2, choices=TIDE_DESCRIPTOR_CHOICES, blank=True, null=True)
    probe_depth = models.FloatField(blank=True, null=True)
    water_temp_c = models.FloatField(blank=True, null=True)
    salinity = models.FloatField(blank=True, null=True)
    pressure = models.FloatField(blank=True, null=True)
    dissolved_o2 = models.FloatField(blank=True, null=True)
    sp_cond_ms = models.FloatField(blank=True, null=True)
    spc_ms = models.FloatField(blank=True, null=True)
    ph = models.FloatField(blank=True, null=True)
    turbidiy = models.FloatField(blank=True, null=True)
    weather_notes = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.time_date



class LoggerDeployment(models.Model):
    # Choices for timezone
    AST = 'AST'
    ADT = 'ADT'
    UTC = 'UTC'
    TIMEZONE_CHOICES = (
        (AST, 'AST'),
        (ADT, 'ADT'),
        (UTC, 'UTC'),
    )

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="logger_deployments")
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING)
    date_deployed = models.DateTimeField()
    date_retrieved = models.DateTimeField(blank=True, null=True)
    days_deployed = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.date_retrieved != None:
            self.days_deployed = (self.date_retrieved - self.date_deployed).days
        self.last_modified = timezone.now()
        return super().save(*args, **kwargs)

class LoggerData(models.Model):
    logger_deployment = models.ForeignKey(LoggerDeployment, on_delete=models.DO_NOTHING, related_name="logger_data")
    time_date = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    water_temp_c = models.FloatField(blank=True, null=True)
    salinity = models.FloatField(blank=True, null=True)
    pressure = models.FloatField(blank=True, null=True)
    dissolved_o2 = models.FloatField(blank=True, null=True)
    sp_cond_ms = models.FloatField(blank=True, null=True)
    spc_ms = models.FloatField(blank=True, null=True)
    ph = models.FloatField(blank=True, null=True)
    turbidiy = models.FloatField(blank=True, null=True)

