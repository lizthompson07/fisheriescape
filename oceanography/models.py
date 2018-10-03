from django.db import models
from django.utils import timezone

# Create your models here.

def img_file_name(instance, filename):
    img_name = 'oceanography/{}'.format(filename)
    return img_name

class Doc(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    # url = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to=img_file_name)
    date_modified = models.DateTimeField(default = timezone.now )

    def save(self,*args,**kwargs):
        self.date_modified  = timezone.now()
        return super().save(*args,**kwargs)


    def __str__(self):
        return self.item_name

class Probe(models.Model):
    probe_name = models.CharField(max_length=255)

class Mission(models.Model):
    mission_name = models.CharField(max_length=255)
    mission_number = models.CharField(max_length=255)
    vessel_name = models.CharField(max_length=255)
    chief_scientist = models.CharField(max_length=255)
    samplers = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    probe = models.ForeignKey(Probe, null=True, blank=True, on_delete=models.DO_NOTHING)
    area_of_operation = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    season  = models.IntegerField(null=True, blank=True)

    def save(self,*args,**kwargs):
        if self.start_date:
            self.season = self.start_date.year
        return super().save(*args,**kwargs)


class Bottle(models.Model):
    # Choices for timezone
    TIMEZONE_CHOICES = (
        ("AST","Atlantic Standard Time"),
        ("ADT","Atlantic Daylight Time"),
        ("UTC","Coordinated Universal Time"),
    )

    mission = models.ForeignKey(Mission, related_name="bottles", on_delete=models.CASCADE)
    bottle_uid = models.CharField(max_length=10)
    station = models.IntegerField(null=True, blank=True, verbose_name="Station #")
    set = models.IntegerField(null=True, blank=True, verbose_name="Set #")
    event = models.IntegerField(null=True, blank=True, verbose_name="Event #")
    date_time = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=3, choices=TIMEZONE_CHOICES)
    date_time_UTC = models.DateTimeField(null=True, blank=True, verbose_name="Date / time (UTC)")
    sounding_m = models.FloatField(null=True, blank=True, verbose_name="Sounding (m)")
    bottle_depth_m = models.FloatField(null=True, blank=True, verbose_name="Bottle depth (m)")
    temp_c = models.FloatField(null=True, blank=True, verbose_name="Temperature (°C)")
    sal_ppt = models.FloatField(null=True, blank=True, verbose_name="Salinity (ppt)")
    ph = models.FloatField(null=True, blank=True, verbose_name="pH")
    lat_DDdd = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    long_DDdd = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    ctd_filename = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=510, null=True, blank=True)

    def save(self,*args,**kwargs):
        if self.date_time and self.timezone:
            if self.timezone == "UTC":
                self.date_time_UTC  = self.date_time
            elif self.timezone == "AST":
                self.date_time_UTC  = self.date_time.replace(hour=self.date_time.hour+4)
            elif self.timezone == "ADT":
                self.date_time_UTC  = self.date_time.replace(hour=self.date_time.hour+3)
        return super().save(*args,**kwargs)
