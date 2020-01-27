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

class PersonType(models.Model):
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
    person_type = models.ForeignKey(PersonType, on_delete=models.DO_NOTHING, related_name="people", verbose_name=_(""))
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    organisation = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))

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

class ObservationPlatform(models.Model):
    type_choices = (
        (1, _("plane")),
        (2, _("boat")),
        (3, _("drone")),
        (4, _("mooring")),
        (5, _("glider")),
        (6, _("land")),
        (7, _("space")),
    )
    type = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""), choices=type_choices)
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

class Observation(models.Model):
    outing = models.ForeignKey(Outing, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""))
    instrument = models.ForeignKey(Instrument, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""))
    datetime = models.DateTimeField(null=True, blank=True, verbose_name=_(""))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_(""))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_(""))
    observer = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name="sightings", verbose_name=_(""), null=True, blank=True)
    beaufort = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    glare_left = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    glare_right = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    cloud_percent = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))

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
    verified = models.BooleanField(default=False, verbose_name=_(""))
    # known_individual = models.ForeignKey(Individual)

class Metadata(models.Model):
    field_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    field_value = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))


class OriginalMediafile(models.Model):
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    filename = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    observation = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, related_name="original_mediafiles", verbose_name=_(""))
    metadata = models.ForeignKey(Metadata, on_delete=models.DO_NOTHING, related_name="original_mediafiles", verbose_name=_(""))

class FieldName(models.Model):
    field_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    used_for = models.ManyToManyField(Instrument, verbose_name=_(""), blank=True)


class MediafileSighting(models.Model):
    mediafile = models.ForeignKey(OriginalMediafile, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", verbose_name=_(""))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    certainty = models.ForeignKey(Certainty, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    sex = models.ForeignKey(Sex, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
    life_stage = models.ForeignKey(LifeStage, on_delete=models.DO_NOTHING, related_name="mediafile_sightings", null=True, blank=True)
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
