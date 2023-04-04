import os

from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from shared_models.models import MetadataFields


class NAFOArea(models.Model):
    layer_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("layer id"))
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("nafo area name"))
    polygon = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        unique_together = (('name', 'layer_id'),)
        ordering = ["name", ]


REGION_CHOICES = (
    ("Gulf", "Gulf"),
    ("Mar", "Maritimes"),
    ("NL", "Newfoundland"),
    ("QC", "Quebec"),
)


class FisheryArea(models.Model):
    layer_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("layer id"))
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("fisheries area name"))
    nafo_area = models.ManyToManyField(NAFOArea, blank=True, related_name="nafoareas", verbose_name=_("nafo area name"))
    region = models.CharField(max_length=255, null=True, blank=True, choices=REGION_CHOICES,
                              verbose_name=_("DFO region"))
    polygon = models.MultiPolygonField(srid=4326)

    class Meta:
        unique_together = (('name', 'layer_id'),)
        ordering = ["layer_id", "name", ]
        indexes = [
            models.Index(["layer_id"], name="layer_id"),
        ]

    def __str__(self):
        my_str = "{}".format(self.name)

        # if self.layer_id:
        #     my_str += f' ({self.layer_id})'
        return my_str

    def get_absolute_url(self):
        return reverse("fisheriescape:fishery_area_detail", kwargs={"pk": self.id})


class Species(models.Model):
    english_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("english name"))
    french_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("french name"))
    latin_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("scientific name"))
    website = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("website"))

    class Meta:
        ordering = ["english_name"]
        indexes = [
            models.Index(["english_name"], name="%(class)s_english_name"),
        ]

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("english_name"))):

            return "{}".format(getattr(self, str(_("english_name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.english_name)

    def get_absolute_url(self):
        return reverse("fisheriescape:species_detail", kwargs={"pk": self.id})


class VulnerableSpecies(models.Model):
    english_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("english name"))
    french_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("french name"))
    latin_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("scientific name"))
    website = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("website"))

    class Meta:
        ordering = ["english_name"]
        indexes = [
            models.Index(["english_name"], name="%(class)s_english_name"),
        ]

    def __str__(self):
        # check to see if a French value is given
        if getattr(self, str(_("english_name"))):
            return getattr(self, str(_("english_name")))
        # if there is no translated term, just pull from the english field
        else:
            return self.english_name

    def get_absolute_url(self):
        return reverse("fisheriescape:vulnerable_species_detail", kwargs={"pk": self.id})


RISK_STATUS_CHOICES = (
    ("No Status", "No Status"),
    ("Not at Risk", "Not at Risk"),
    ("Special Concern", "Special Concern"),
    ("Threatened", "Threatened"),
    ("Endangered", "Endangered"),
    ("Extirpated", "Extirpated"),
    ("Extinct", "Extinct"),
)


class MarineMammal(models.Model):
    english_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("english name"))
    english_name_short = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("short english name"))
    french_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("french name"))
    french_name_short = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("short french name"))
    latin_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("scientific name"))
    population = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("population"))
    sara_status = models.CharField(max_length=255, null=True, blank=True, choices=RISK_STATUS_CHOICES,
                                   verbose_name=_("sara status"))
    cosewic_status = models.CharField(max_length=255, null=True, blank=True, choices=RISK_STATUS_CHOICES,
                                      verbose_name=_("cosewic assessed"))
    website = models.URLField(max_length=250, blank=True, null=True, verbose_name=_("website"))

    class Meta:
        ordering = ["english_name"]

    def __str__(self):
        if self.english_name_short:

            my_str = "{}".format(self.english_name_short)
        else:
            my_str = "{}".format(self.english_name)

        return my_str

    #
    # def get_absolute_url(self):
    #     return reverse("fisheriescape:species_detail", kwargs={"pk": self.id})


class Mitigation(models.Model):
    mitigation_type = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("mitigation type"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("description"))

    class Meta:
        ordering = ["mitigation_type"]

    def __str__(self):
        return "{}".format(self.mitigation_type)


STATUS_CHOICES = (
    ("Active", "Active"),
    ("Experimental", "Experimental"),
    ("Inactive", "Inactive"),
    ("Unknown", "Unknown"),
)

LICENSE_CHOICES = (
    ("Multi", "Multi Species"),
    ("Single", "Single Species"),
)

GEAR_CHOICES = (
    ("Gillnets", "Gillnets"),
    ("Longlines", "Longlines"),
    ("Pots / Traps", "Pots / Traps"),
    ("Set Gillnet", "Set Gillnet"),
)

MGMT_CHOICES = (
    ("Effort Control", "Effort Control"),
    ("Quota - Competitive", "Quota - Competitive"),
    ("Quota - Individual", "Quota - Individual"),
)

ROPE_CHOICES = (
    ("", "---------"),
    ("Blue", "Blue"),
    ("Black", "Black"),
    ("Red", "Red"),
    ("Yellow", "Yellow"),
    ("White", "White"),
    ("Purple", "Purple"),
    ("Orange", "Orange"),
    ("Green", "Green"),
    ("Grey", "Grey"),
    ("Brown", "Brown"),
    ("Pink", "Pink"),
    ("Red/White Pattern", "Red/White Pattern"),
)


class Fishery(MetadataFields):
    # fisheries info
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="fisherys",
                                verbose_name=_("species"))
    fishery_areas = models.ManyToManyField(FisheryArea, related_name="fisherys", verbose_name=_("fishery areas"))
    participants = models.IntegerField(null=True, blank=True, verbose_name=_("participants"))
    participant_detail = models.TextField(null=True, blank=True, verbose_name=_("participant detail"))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_("start date of season"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("end date of season"))
    fishery_status = models.CharField(max_length=255, null=True, blank=True, choices=STATUS_CHOICES,
                                      verbose_name=_("fishery status"))
    license_type = models.CharField(max_length=255, null=True, blank=True, choices=LICENSE_CHOICES,
                                    verbose_name=_("type of license"))
    management_system = models.CharField(max_length=255, null=True, blank=True, choices=MGMT_CHOICES,
                                         verbose_name=_("management system"))
    fishery_comment = models.TextField(blank=True, null=True, verbose_name=_("general comments"))
    # gear information
    gear_type = models.CharField(max_length=255, null=True, blank=True, choices=GEAR_CHOICES,
                                 verbose_name=_("gear type"))
    gear_amount = models.CharField(max_length=255, null=True, blank=True,
                                   verbose_name=_("avg gear amount per participant"))
    gear_config = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("gear configuration"))
    gear_soak = models.FloatField(max_length=255, null=True, blank=True, verbose_name=_("avg rope soak time"))
    gear_primary_colour = models.CharField(max_length=255, null=True, blank=True, choices=ROPE_CHOICES,
                                           verbose_name=_("gear primary colour"))
    gear_secondary_colour = models.CharField(max_length=255, null=True, blank=True, choices=ROPE_CHOICES,
                                             verbose_name=_("gear secondary colour"))
    gear_tertiary_colour = models.CharField(max_length=255, null=True, blank=True, choices=ROPE_CHOICES,
                                            verbose_name=_("gear tertiary colour"))
    gear_comment = models.TextField(blank=True, null=True, verbose_name=_("gear comments"))
    # monitoring information
    monitoring_aso = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], null=True,
                                         blank=True, verbose_name=_("at sea observer (ASO)"))
    monitoring_dockside = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], null=True,
                                              blank=True, verbose_name=_("dockside monitoring"))
    monitoring_logbook = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], null=True,
                                             blank=True, verbose_name=_("logbook"))
    monitoring_vms = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], null=True,
                                         blank=True, verbose_name=_("vessel monitoring system (VMS)"))
    monitoring_comment = models.TextField(blank=True, null=True, verbose_name=_("monitoring comments"))
    # mitigation
    mitigation = models.ManyToManyField(Mitigation, blank=True, related_name="fisherys",
                                        verbose_name=_("mitigation type"))
    mitigation_comment = models.TextField(blank=True, null=True, verbose_name=_("mitigation comments"))
    # marine mammals
    marine_mammals = models.ManyToManyField(MarineMammal, blank=True, related_name="fisherys",
                                            verbose_name=_("marine mammals"))

    class Meta:
        ordering = ["start_date", "species", ]

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("species"))):

            my_str = "{}".format(getattr(self, str(_("species"))))
            # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.species)

        if self.start_date:
            my_str += f' (record: {self.id})'
        return my_str

    @property
    def nafo_fishery_areas(self):
        # nafo = Fishery.objects.all()[0].fishery_areas.all()[0].nafo_area.all()
        fishery = self.id
        nafo = NAFOArea.objects.filter(nafoareas__fisherys__id=fishery)
        list_result = list(nafo.values("name"))
        nafo_list = []

        for i in list_result:
            # nafo_list = nafo_list + ", " + (i["name"])
            nafo_list.append(i["name"])

        nafo_set = set(nafo_list)
        string = ", ".join(nafo_set)
        return string

    def get_absolute_url(self):
        return reverse("fisheriescape:fishery_detail", kwargs={"pk": self.id})


class Week(models.Model):
    week_number = models.IntegerField(validators=[MaxValueValidator(53), MinValueValidator(1)], verbose_name="week")
    approx_start = models.DateField(blank=True, null=True, verbose_name="approx start")
    approx_end = models.DateField(blank=True, null=True, verbose_name="approx end")

    class Meta:
        ordering = ["week_number"]
        indexes = [
            models.Index(["week_number"], name="week_number"),
        ]

    def __str__(self):
        my_str = "Week {}".format(self.week_number)
        return my_str

    @property
    def date_range_text(self):
        try:
            string = "{} to {}".format(self.approx_start.strftime("%d-%b"), self.approx_end.strftime("%d-%b"))
            return string
        except AttributeError:
            return None


class Hexagon(models.Model):
    grid_id = models.CharField(max_length=255, null=True, blank=True, unique=True, verbose_name="grid id")
    polygon = models.MultiPolygonField(srid=4326)  # srid 4326 for WGS84 and 4269 for NAD83

    def __str__(self):
        my_str = "Grid {}".format(self.grid_id)
        return my_str

    class Meta:
        indexes = [
            models.Index(["grid_id"], name="grid_id"),
        ]


class Score(models.Model):
    hexagon = models.ForeignKey(Hexagon, on_delete=models.DO_NOTHING, related_name="scores",
                                verbose_name=_("hexagon"))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="scores",
                                verbose_name=_("species"))
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING, related_name="scores",
                             verbose_name=_("week"))
    site_score = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True,
                                     verbose_name=_("site score"))
    ceu_score = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name=_("ceu score"))
    fs_score = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True, verbose_name=_("fs score"))

    def __str__(self):
        my_str = "{}".format(self.hexagon.grid_id)

        if self.species:
            my_str += f' ({self.species.english_name} - {self.week.week_number})'
        return my_str

    class Meta:
        ordering = ['species', 'week', ]
        unique_together = (('hexagon', 'week', 'species'),)
        indexes = [
            models.Index(["species", "week"], name="%(class)s_species_week"),
            models.Index(["week"], name="%(class)s_week"),
            models.Index(["species"], name="%(class)s_species")
        ]


class VulnerableSpeciesSpot(models.Model):
    vulnerable_species = models.ForeignKey(VulnerableSpecies, on_delete=models.DO_NOTHING, related_name="spots",
                                           verbose_name=_("vulnerable_species"))
    week = models.ForeignKey(Week, on_delete=models.DO_NOTHING, related_name="vulnerable_species_spots",
                             verbose_name=_("week"))
    count = models.IntegerField(blank=True, null=True, verbose_name=_("count"))
    point = models.PointField(blank=False, null=False, verbose_name=_("point"))
    date = models.DateField()

    def __str__(self):
        my_str = "{}".format(self.id)

        if self.vulnerable_species:
            my_str += f' ({self.vulnerable_species.english_name} - {self.week.week_number})'

        return my_str

    class Meta:
        ordering = ['vulnerable_species', 'week', ]
        indexes = [
            models.Index(["vulnerable_species", "week"], name="%(class)s_s_w"),
            models.Index(["week"], name="%(class)s_week"),
            models.Index(["species"], name="%(class)s_species")
        ]
