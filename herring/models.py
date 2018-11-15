from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
import markdown
import os
# Create your models here.

# Choices for YesNo
YESNO_CHOICES = (
    (1,"Yes"),
    (0,"No"),
)


class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        if not self.first_name:
            return "{}".format(self.last_name)
        else:
            return "{}, {}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name','first_name']

class District(models.Model):
    # Choices for province
    NS = 1
    NB = 2
    PE = 3
    QC = 4
    NL = 5
    PROVINCE_CHOICES = (
        (NS,'Nova Scotia'),
        (NB,'New Brunswick'),
        (PE,'Prince Edward Island'),
        (QC,'Quebec'),
        (NL,'Newfoundland'),
    )

    district_id = models.IntegerField()
    province_id = models.IntegerField(choices=PROVINCE_CHOICES)
    locality_list = models.TextField()

    def __str__(self):
        return "{}{} | {} | {}".format(self.province_id, self.district_id,self.get_province_id_display(),self.locality_list)

    class Meta:
        ordering = ['province_id','district_id' ]

    @property
    def district_code(self):
        return "{}{}".format(self.province_id, self.district_id)


class SamplingProtocol(models.Model):
    # Choices for sampling_type
    PORT = 1
    SEA = 2

    SAMPLING_TYPE_CHOICES = (
        (PORT,'Port'),
        (SEA,'At-sea'),
    )
    protocol = models.CharField(max_length=255)
    sampling_type = models.IntegerField(choices=SAMPLING_TYPE_CHOICES, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.protocol)

class FishingArea(models.Model):
    nafo_area_name = models.CharField(max_length=255)
    nafo_area_code = models.CharField(max_length=25, null=True, blank=True)
    herring_area_code = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        if self.herring_area_code:
            return "{} (herring code = {})".format(self.nafo_area_code,self.herring_area_code)
        else:
            return self.nafo_area_code

    class Meta:
        ordering = ['nafo_area_code']

# class Vessel(models.Model):
#     cfvn = models.IntegerField(primary_key=True)
#     vessel_name = models.CharField(max_length=255, null=True, blank=True)
#
#     def __str__(self):
#         return "{} ({})".format(self.cfvn, self.vessel_name)
#
#     class Meta:
#         ordering = ['cfvn']

class Gear(models.Model):
    gear = models.CharField(max_length=255)
    gear_code = models.CharField(max_length=255)
    isscfg_code = models.CharField(max_length=255, null=True, blank=True)
    nafo_code = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.gear_code, self.gear)

    class Meta:
        ordering = ['gear_code']

class MeshSize(models.Model):
    size_mm = models.CharField(max_length=55, null=True, blank=True)
    size_inches = models.CharField(max_length=55, null=True, blank=True)
    size_inches_decimal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "{} / {}".format(self.size_inches, self.size_mm)

    class Meta:
        ordering = ['size_mm']

class LengthBin(models.Model):
    bin_length_cm = models.FloatField(primary_key=True)

    def __str__(self):
        return "{} cm".format(self.bin_length_cm)

class Test(models.Model):
    # Choices for sampling_type
    POINT = 'single_measurement'
    LAB = 'lab_detail'
    OTOLITH = 'otolith_detail'

    SCOPE_CHOICES = (
        (LAB,'lab detail'),
        (POINT,'single measurement'),
        (OTOLITH,'otolith detail'),
    )
    scope = models.CharField(max_length=25, choices=SCOPE_CHOICES)
    description = models.CharField(max_length=255)
    notes = models.CharField(max_length=1000, null=True, blank=True )

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['scope', 'id']

class Sample(models.Model):
    sampling_protocol = models.ForeignKey(SamplingProtocol, related_name="samples", on_delete=models.DO_NOTHING)
    sample_date = models.DateTimeField()
    sampler_ref_number = models.IntegerField(verbose_name="Sampler's reference number")
    sampler = models.ForeignKey(Sampler, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    district = models.ForeignKey(District, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True )
    mission_id = models.CharField(max_length=50, null=True, blank=True)
    latitude_n = models.CharField(max_length=50, null=True, blank=True, verbose_name="Latitude (N)")
    longitude_w = models.CharField(max_length=50, null=True, blank=True, verbose_name="Longitude (W)")
    fishing_area = models.ForeignKey(FishingArea, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    gear = models.ForeignKey(Gear, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    experimental_net_used = models.IntegerField(choices=YESNO_CHOICES, null=True, blank=True)
    # vessel = models.ForeignKey(Vessel, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    vessel_cfvn = models.IntegerField(null=True, blank=True)
    mesh_size = models.ForeignKey(MeshSize, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    catch_weight_lbs = models.FloatField(null=True, blank=True, verbose_name="Catch weight (lbs)")
    sample_weight_lbs = models.FloatField(null=True, blank=True, verbose_name="Sample weight (lbs)")
    total_fish_measured = models.IntegerField(null=True, blank=True)
    total_fish_preserved = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    old_id = models.IntegerField(null=True, blank=True)
    season =  models.IntegerField(null=True, blank=True)
    length_frequencies = models.ManyToManyField(to=LengthBin, through='LengthFrequency')
    # tests = models.ManyToManyField(to=Test, through='SampleTest')
    lab_processing_complete = models.BooleanField(default=False)
    otolith_processing_complete = models.BooleanField(default=False)
    creation_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="created_by_samples")
    last_modified_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="last_modified_by_samples")

    class Meta:
        ordering = ['-sample_date']

    def get_absolute_url(self):
        return reverse('herring:sample_detail', kwargs={'pk':self.id})

    def save(self,*args,**kwargs):
        self.season = self.sample_date.year
        self.last_modified_date = timezone.now()

        # set lab_processing_complete
        ## first test if there are enough or two many fish...
        if not self.fish_details.count() == self.total_fish_preserved:
            # then there is no chance for being comeplete
            self.lab_processing_complete = False
            self.otolith_processing_complete = False
        else:
            count = 0
            for fish in self.fish_details.all():
                if fish.lab_processed_date:
                    count = count + 1
            if count == self.total_fish_preserved:
                self.lab_processing_complete = True
            else:
                self.lab_processing_complete = False

            # set otolith_processing_complete
            count = 0
            for fish in self.fish_details.all():
                if fish.otolith_processed_date:
                    count = count + 1
            if count == self.total_fish_preserved:
                self.otolith_processing_complete = True
            else:
                self.otolith_processing_complete = False

        return super().save(*args,**kwargs)



class Maturity(models.Model):
    maturity = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.maturity

class Sex(models.Model):
    sex = models.CharField(max_length=255)
    oracle_code = models.CharField(max_length=1, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.sex


class OtolithSeason(models.Model):
    season = models.CharField(max_length=55)
    oracle_code = models.CharField(max_length=2)

    def __str__(self):
        return self.season

def img_file_name(instance, filename):
    img_name = 'herring/sample_{}/fish_number_{}.jpg'.format(instance.sample.id, instance.fish_number)
    return img_name

class FishDetail(models.Model):
    sample = models.ForeignKey(Sample, related_name="fish_details", on_delete=models.CASCADE)
    fish_number = models.IntegerField()
    fish_length = models.FloatField(null=True, blank=True)
    fish_weight = models.FloatField(null=True, blank=True)
    sex = models.ForeignKey(Sex, related_name="fish_details", on_delete=models.DO_NOTHING, null=True, blank=True)
    maturity = models.ForeignKey(Maturity, related_name="fish_details", on_delete=models.DO_NOTHING, null=True, blank=True)
    gonad_weight = models.FloatField(null=True, blank=True)
    parasite = models.IntegerField(choices=YESNO_CHOICES, null=True, blank=True)
    lab_sampler = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="lab_sampler_fish_details")
    otolith_sampler = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="otolith_sampler_fish_details")
    lab_processed_date = models.DateTimeField(blank=True, null=True)
    annulus_count = models.IntegerField(null=True, blank=True)
    otolith_season = models.ForeignKey(OtolithSeason, related_name="fish_details", on_delete=models.DO_NOTHING, null=True, blank=True)
    otolith_image_remote_filepath = models.CharField(max_length = 2000, blank=True, null=True)
    otolith_processed_date = models.DateTimeField(blank=True, null=True)

    test_204_accepted = models.CharField(max_length = 5, null=True, blank=True) # ligh_length:fish_weight
    test_207_accepted = models.CharField(max_length = 5, null=True, blank=True) # gonad weight : somatic weight : maturity level
    test_209_accepted = models.CharField(max_length = 5, null=True, blank=True) # number of annuli : fish length
    test_302_accepted = models.CharField(max_length = 5, null=True, blank=True) # fish length within probable range
    test_305_accepted = models.CharField(max_length = 5, null=True, blank=True) # somatic weight within probable range
    test_308_accepted = models.CharField(max_length = 5, null=True, blank=True) # gonad weight within probable range
    test_311_accepted = models.CharField(max_length = 5, null=True, blank=True) # annulus count within probable range

    remarks = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="created_by_details")
    last_modified_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="last_modified_by_details")

    class Meta:
        unique_together = (('sample', 'fish_number'),)
        ordering = ('sample', 'fish_number')

    def get_absolute_url(self):
        return reverse('herring:fish_detail', kwargs={'sample':self.sample.id,'pk':self.id})

    def save(self,*args,**kwargs):
        self.last_modified_date = timezone.now()
        if self.fish_length and self.fish_weight and self.sex and self.maturity and self.gonad_weight != None and self.lab_sampler:
            if self.lab_processed_date == None:
                self.lab_processed_date = timezone.now()
        else:
            self.lab_processed_date = None
        if self.otolith_sampler and self.annulus_count and self.otolith_season:
            if self.otolith_processed_date == None:
                self.otolith_processed_date = timezone.now()
        else:
            self.otolith_processed_date = None
        super().save(*args,**kwargs)



class LengthFrequency(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='length_frequency_objects')
    length_bin = models.ForeignKey(LengthBin, on_delete=models.DO_NOTHING)
    count = models.IntegerField()

    class Meta:
        unique_together = (('sample', 'length_bin'),)
        ordering = ('sample', 'length_bin')

# class SampleTest(models.Model):
#     sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_tests')
#     test = models.ForeignKey(Test, on_delete=models.DO_NOTHING)
#     test_passed = models.BooleanField(default = False)
#
#     class Meta:
#         unique_together = (('sample', 'test'),)
#         ordering = ('sample', 'test')
#
# class FishDetailTest(models.Model):
#
#     # Choices for field_name
#     GLOBAL = " global"
#     FISH_LEN = "fish_length"
#     SOMATIC_WT = "fish_weight"
#     GONAD_WT = "gonad_weight"
#     ANNULI = "annulus_count"
#
#     FIELD_NAME_CHOICES = (
#         (GLOBAL,' global'),
#         (SOMATIC_WT,'somatic weight'),
#         (GONAD_WT,'gonad weight'),
#         (FISH_LEN,'fish length'),
#         (ANNULI,'annulus count'),
#     )
#
#     # Choices for scope
#     LAB = 1
#     OTOLITH = 2
#
#     SCOPE_CHOICES = (
#         (LAB,' lab_detail'),
#         (OTOLITH,'otolith detail'),
#     )
#
#     fish_detail = models.ForeignKey(FishDetail, on_delete=models.CASCADE, related_name='sample_tests')
#     test = models.ForeignKey(Test, on_delete=models.DO_NOTHING)
#     field_name = models.CharField(max_length=55, choices=FIELD_NAME_CHOICES)
#     scope = models.IntegerField(choices=SCOPE_CHOICES)
#     test_passed = models.BooleanField(default = False)
#     accepted = models.IntegerField(choices=YESNO_CHOICES, null=True, blank=True)
#
#     class Meta:
#         unique_together = (('fish_detail','field_name','test'),)
#         ordering = ('fish_detail', 'field_name')
