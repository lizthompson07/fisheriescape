from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models


class Species(models.Model):
    code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_(""))
    english_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    french_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    latin_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    vor_code = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("VOR code"))
    quebec_code = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Quebec code"))
    aphia_id = models.IntegerField(null=True, blank=True)


class Role(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Person(models.Model):
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    organisation = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    # m2m
    roles = models.ManyToManyField(Role, verbose_name=_(""))


class Instrument(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


# CHOICES = plane, boat, drone, mooring, glider, land, space
class ObservationPlatformType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class ObservationPlatform(models.Model):
    observation_platform_type = models.ForeignKey(ObservationPlatformType, on_delete=models.DO_NOTHING, related_name="platforms",
                                                  verbose_name=_("type of observation platform"))
    authority = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    owner = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    make_model = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))


class Outing(models.Model):
    observation_platform = models.ForeignKey(ObservationPlatform, on_delete=models.DO_NOTHING, related_name="outings",
                                             verbose_name=_("observation platform"))
    region = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    purpose = models.CharField(max_length=250, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    identifier_string = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.identifier_string


class MetadataField(models.Model):
    DATA_TYPE_CHOICES = (
        (1, _("integer/categorical")),
        (2, _("float")),
        (3, _("string")),
    )
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    nom = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("English description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French description"))
    data_type = models.IntegerField(choices=DATA_TYPE_CHOICES, verbose_name=_("data type"))


# used for defining metadata field categories, when applicable
class MetadataFieldCategory(models.Model):
    metadata_field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, related_name="categories")
    code = models.CharField(max_length=3)
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("English description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French description"))

    @property
    def tname(self):
        # check to see if a french value is given
        if getattr(self, str(_("description_eng"))):
            return "{}".format(getattr(self, str(_("description_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.description_eng)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("description_eng"))):
            return "{}-{}".format(self.code, getattr(self, str(_("description_eng"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}-{}".format(self.code, self.description_eng)

    class Meta:
        ordering = ['code', ]
        unique_together = ['metadata_field', 'code']


class Observation(models.Model):
    outing = models.ForeignKey(Outing, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""))
    instrument = models.ForeignKey(Instrument, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""))
    datetime = models.DateTimeField(null=True, blank=True, verbose_name=_(""))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_(""))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_(""))
    observer = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""), null=True, blank=True)
    metadata = models.ManyToManyField(MetadataField, through="ObservationMetadatum")


class ObservationMetadatum(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, related_name="observation_metadata", verbose_name=_(""))
    metadata_field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, related_name="observation_metadata")
    value = models.CharField(max_length=1000)


class Certainty(models.Model):
    code = models.IntegerField(blank=True, null=True, verbose_name=_(""))
    english_certainty_description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    french_certainty_description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))


class Sex(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class LifeStage(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class HealthStatus(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class ObservationSighting(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, related_name="observation_sightings", verbose_name=_(""))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="observation_sightings", null=True, blank=True)
    certainty = models.ForeignKey(Certainty, on_delete=models.DO_NOTHING, related_name="observation_sightings", null=True, blank=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="observation_sightings", null=True, blank=True)
    life_stage = models.ForeignKey(LifeStage, on_delete=models.DO_NOTHING, related_name="observation_sightings", null=True, blank=True)
    health_status = models.ForeignKey(HealthStatus, on_delete=models.DO_NOTHING, related_name="observation_sightings",
                                      null=True, blank=True)
    verified = models.BooleanField(default=False, verbose_name=_(""))
    # known_individual = models.ForeignKey(Individual)


class OriginalMediafile(models.Model):
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    filename = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    observation = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, related_name="original_mediafiles", verbose_name=_(""))
    metadata = models.ManyToManyField(MetadataField, through="OriginalMediafileMetadatum")


class OriginalMediafileMetadatum(models.Model):
    original_mediafile = models.ForeignKey(OriginalMediafile, on_delete=models.DO_NOTHING, related_name="original_mediafile_metadata",
                                           verbose_name=_(""))
    metadata_field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, related_name="original_mediafile_metadata")
    value = models.CharField(max_length=1000)


class FieldName(models.Model):
    field_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    used_for = models.ManyToManyField(Instrument, verbose_name=_(""), blank=True)


class MediafileSighting(models.Model):
    original_mediafile = models.ForeignKey(OriginalMediafile, on_delete=models.DO_NOTHING, related_name="mediafile_sightings",
                                           verbose_name=_(""))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    certainty = models.ForeignKey(Certainty, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    life_stage = models.ForeignKey(LifeStage, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    health_status = models.ForeignKey(HealthStatus, on_delete=models.DO_NOTHING, related_name="mediafile_sightings",
                                      null=True, blank=True)
    verified = models.BooleanField(default=False, verbose_name=_(""))
    # known_individual = models.ForeignKey(Individual)


class ProcessedMediafile(models.Model):
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    filename = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    original_mediafile = models.ForeignKey(OriginalMediafile, on_delete=models.DO_NOTHING, related_name="processed_mediafiles",
                                           verbose_name=_("original mediafile"))
    species = models.ManyToManyField(Species, verbose_name=_(""), blank=True)
    verified = models.BooleanField(default=False, verbose_name=_(""))
    analyst = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    date_analysed = models.DateTimeField()
    date_created = models.DateTimeField()
