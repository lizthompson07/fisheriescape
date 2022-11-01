from django.contrib import auth
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from herring import flag_definitions
from shared_models import models as shared_models
from shared_models.models import MetadataFields, SimpleLookup
from shared_models.utils import get_metadata_string

# Choices for YesNo
YESNO_CHOICES = (
    (1, "Yes"),
    (0, "No"),
)
YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


class HerringUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="herring_user", verbose_name=_("DM Apps user"))
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)
    is_crud_user = models.BooleanField(default=False, verbose_name=_("CRUD permissions?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class Species(SimpleLookup):
    length_type_choices = (
        (1, "total"),
        (2, "fork"),
    )
    aphia_id = models.IntegerField(verbose_name="WoRMS AphiaID", unique=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    length_type = models.IntegerField(verbose_name="length type", choices=length_type_choices, default=1)
    a = models.FloatField(blank=True, null=True, verbose_name=_("length-weight A"),
                          help_text=_("The A regression coefficient in the relationship between length and weight for unspecified sex."), )
    b = models.FloatField(blank=True, null=True, verbose_name=_("length-weight B"),
                          help_text=_("The A regression coefficient in the relationship between length and weight for unspecified sex."), )
    max_length = models.IntegerField(verbose_name="maximum length", help_text=_("Any observations beyond this mark will prompt a warning"), blank=True,
                                     null=True)
    max_weight = models.IntegerField(verbose_name="maximum fish weight", help_text=_("Any observations beyond this mark will prompt a warning"), blank=True,
                                     null=True)
    max_gonad_weight = models.IntegerField(verbose_name="maximum gonad weight", help_text=_("Any observations beyond this mark will prompt a warning"),
                                           blank=True, null=True)
    max_annulus_count = models.IntegerField(verbose_name="maximum annulus count", help_text=_("Any observations beyond this mark will prompt a warning"),
                                            blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("species")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


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
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        return str(self)

    @property
    def sample_count(self):
        return self.samples.count()


class District(models.Model):
    # Choices for province
    NS = 1
    NB = 2
    PE = 3
    QC = 4
    NL = 5
    PROVINCE_CHOICES = (
        (NS, 'Nova Scotia'),
        (NB, 'New Brunswick'),
        (PE, 'Prince Edward Island'),
        (QC, 'Quebec'),
        (NL, 'Newfoundland'),
    )

    district_id = models.IntegerField()
    province_id = models.IntegerField(choices=PROVINCE_CHOICES)
    locality_list = models.TextField()

    def __str__(self):
        return "{}{} | {} | {}".format(self.province_id, self.district_id, self.get_province_id_display(),
                                       self.locality_list)

    class Meta:
        ordering = ['province_id', 'district_id']

    @property
    def district_code(self):
        return "{}{}".format(self.province_id, self.district_id)


class FishingArea(models.Model):
    nafo_area_name = models.CharField(max_length=255)
    nafo_area_code = models.CharField(max_length=25, null=True, blank=True)
    herring_area_code = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        if self.herring_area_code:
            return "{} (herring code = {})".format(self.nafo_area_code, self.herring_area_code)
        else:
            return self.nafo_area_code

    class Meta:
        ordering = ['nafo_area_code']


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
    size_mm = models.IntegerField(null=True)
    size_inches = models.CharField(max_length=55, null=True, blank=True)
    size_inches_decimal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "{} / {} mm".format(self.size_inches, self.size_mm)

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
        (LAB, 'lab detail'),
        (POINT, 'single measurement'),
        (OTOLITH, 'otolith detail'),
    )
    scope = models.CharField(max_length=25, choices=SCOPE_CHOICES)
    description = models.CharField(max_length=255)
    notes = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['scope', 'id']


class Sample(models.Model):
    # Choices for sample_type
    PORT = 1
    SEA = 2

    SAMPLE_TYPE_CHOICES = (
        (PORT, 'Port'),
        (SEA, 'Sea'),
    )

    season_type_choices = (
        (1, "spring"),
        (2, "fall"),
    )

    type = models.IntegerField(blank=True, null=True, choices=SAMPLE_TYPE_CHOICES, verbose_name=_("Sample type"))

    # TODO this should be made mandatory ASAP !!!
    species = models.ForeignKey(Species, related_name="samples", on_delete=models.DO_NOTHING, blank=True, null=True)
    sample_date = models.DateTimeField()
    sampler_ref_number = models.IntegerField(verbose_name="field reference number", blank=True, null=True,
                                             help_text="This might be a sampler's reference number or a set number from a survey")
    sampler = models.ForeignKey(Sampler, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)

    port = models.ForeignKey(shared_models.Port, related_name="herring_samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    survey_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="survey identifier",
                                 help_text="Usually the mission number of the survey from which the sample came.")
    latitude_n = models.FloatField(null=True, blank=True, verbose_name="Latitude", help_text="In decimal degrees, e.g., 48.67789")
    longitude_w = models.FloatField(null=True, blank=True, verbose_name="Longitude", help_text="In decimal degrees, e.g., -64.57819")
    fishing_area = models.ForeignKey(FishingArea, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    gear = models.ForeignKey(Gear, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    experimental_net_used = models.IntegerField(choices=YESNO_CHOICES, null=True, blank=True)
    vessel_cfvn = models.IntegerField(null=True, blank=True, verbose_name=_("vessel CFVN"))
    mesh_size = models.ForeignKey(MeshSize, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True)
    catch_weight_lbs = models.FloatField(null=True, blank=True, verbose_name="Catch weight (lbs)",
                                         help_text="Total weight of the catch from which the sample was collected")
    sample_weight_lbs = models.FloatField(null=True, blank=True, verbose_name="Sample weight (lbs)", help_text="Total weight of the sample collected")
    total_fish_measured = models.IntegerField(null=True, blank=True, help_text="How many specimens were measured?")
    total_fish_preserved = models.IntegerField(null=True, blank=True, help_text="How many specimens were collected?")
    remarks = models.TextField(null=True, blank=True)

    # not editable
    district = models.ForeignKey(District, related_name="samples", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 editable=False)  # this field should be deleted
    old_id = models.CharField(max_length=100, null=True, blank=True, editable=False)
    season = models.IntegerField(null=True, blank=True, verbose_name=_("year"), editable=False)
    season_type = models.IntegerField(null=True, blank=True, choices=season_type_choices, editable=False, verbose_name=_("season"))
    length_frequencies = models.ManyToManyField(to=LengthBin, through='LengthFrequency', editable=False)
    lab_processing_complete = models.BooleanField(default=False, editable=False)
    otolith_processing_complete = models.BooleanField(default=False, editable=False)

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="created_by_samples", editable=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="last_modified_by_samples", editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def lf_count(self):
        return sum([lf.count for lf in self.length_frequency_objects.all()])

    class Meta:
        ordering = ['-sample_date']

    def get_absolute_url(self):
        return reverse('herring:sample_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if self.sample_date:
            self.season = self.sample_date.year
            if self.sample_date.month < 7:
                self.season_type = 1  # spring
            else:
                self.season_type = 2  # fall

        self.last_modified_date = timezone.now()

        # set lab_processing_complete
        ## first test if there are enough or too many fish...
        if self.fish_details.exists() and not self.fish_details.count() >= self.total_fish_preserved:
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

        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} {} {} - {}".format(self.get_type_display(), _("Sample"), self.id, self.species)


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
    fish_length = models.FloatField(null=True, blank=True, verbose_name=_("length (mm)"), validators=(MinValueValidator(0),))
    fish_weight = models.FloatField(null=True, blank=True, verbose_name=_("fish weight (g)"), validators=(MinValueValidator(0),))
    sex = models.ForeignKey(Sex, related_name="fish_details", on_delete=models.DO_NOTHING, null=True, blank=True)
    maturity = models.ForeignKey(Maturity, related_name="fish_details", on_delete=models.DO_NOTHING, null=True, blank=True)
    gonad_weight = models.FloatField(null=True, blank=True, verbose_name=_("gonad weight (g)"), validators=(MinValueValidator(0),))
    parasite = models.IntegerField(choices=YESNO_CHOICES, null=True, blank=True)

    annulus_count = models.IntegerField(null=True, blank=True, validators=(MinValueValidator(0),))
    otolith_season = models.ForeignKey(OtolithSeason, related_name="fish_details", on_delete=models.DO_NOTHING,
                                       null=True, blank=True)
    otolith_image_remote_filepath = models.CharField(max_length=2000, blank=True, null=True)

    test_204_accepted = models.CharField(max_length=5, null=True, blank=True)  # ligh_length:fish_weight
    test_207_accepted = models.CharField(max_length=5, null=True,
                                         blank=True)  # gonad weight : somatic weight : maturity level
    test_209_accepted = models.CharField(max_length=5, null=True, blank=True)  # number of annuli : fish length

    # these four fields are deprecated and should be deleted; be sure to delete corresponding tests in the Test table
    test_302_accepted = models.CharField(max_length=5, null=True, blank=True)  # fish length within probable range
    test_305_accepted = models.CharField(max_length=5, null=True, blank=True)  # somatic weight within probable range
    test_308_accepted = models.CharField(max_length=5, null=True, blank=True)  # gonad weight within probable range
    test_311_accepted = models.CharField(max_length=5, null=True, blank=True)  # annulus count within probable range

    remarks = models.TextField(null=True, blank=True)

    # non-editable
    otolith_sampler = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="otolith_sampler_fish_details",
                                        editable=False)
    lab_sampler = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="lab_sampler_fish_details",
                                    editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True, editable=False)

    created_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="created_by_details", editable=False)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="last_modified_by_details",
                                         editable=False)

    # calc
    is_empty = models.BooleanField(default=True, editable=False)
    lab_processed_date = models.DateTimeField(blank=True, null=True)
    otolith_processed_date = models.DateTimeField(blank=True, null=True)

    @property
    def get_is_empty(self):
        return not (
                self.fish_length or self.fish_weight or self.sex or self.maturity or self.gonad_weight or self.parasite or self.annulus_count or self.otolith_season)

    @property
    def metadata(self):
        return get_metadata_string(self.creation_date, self.created_by, self.last_modified_date, self.last_modified_by)

    def __str__(self):
        return f"Fish detail {self.id}"

    class Meta:
        unique_together = (('sample', 'fish_number'),)
        ordering = ('sample', 'fish_number')

    def get_absolute_url(self):
        return reverse('herring:fish_detail', kwargs={'sample': self.sample.id, 'pk': self.id})

    def save(self, *args, **kwargs):
        self.last_modified_date = timezone.now()
        if None not in (self.fish_length, self.fish_weight, self.sex, self.maturity, self.gonad_weight, self.lab_sampler):
            if not self.lab_processed_date:
                self.lab_processed_date = timezone.now()
        else:
            self.lab_processed_date = None
        if None not in (self.otolith_sampler, self.annulus_count, self.otolith_season):
            if not self.otolith_processed_date:
                self.otolith_processed_date = timezone.now()
        else:
            self.otolith_processed_date = None

        self.is_empty = self.get_is_empty
        super().save(*args, **kwargs)


class LengthFrequency(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='length_frequency_objects')
    length_bin = models.ForeignKey(LengthBin, on_delete=models.DO_NOTHING)
    count = models.IntegerField(null=True)

    class Meta:
        unique_together = (('sample', 'length_bin'),)
        ordering = ('sample', 'length_bin')


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'temp_file/{0}'.format(filename)


class FishDetailFlag(MetadataFields):
    fish_detail = models.ForeignKey(FishDetail, on_delete=models.CASCADE, related_name='flags')
    flag_definition = models.IntegerField(choices=flag_definitions.as_choices())
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = (('fish_detail', 'flag_definition'),)
        ordering = ('fish_detail', 'flag_definition')
