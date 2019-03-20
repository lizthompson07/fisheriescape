from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


# CONNECTED APPS: dm_tickets, travel, projects, sci_fi
# STILL NEED TO CONNECT:
class FiscalYear(models.Model):
    full = models.TextField(blank=True, null=True)
    short = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.full)

    class Meta:
        ordering = ['id', ]

# CONNECTED APPS: masterlist
# STILL NEED TO CONNECT: camp (needs remapping), grais (needs remapping)
class Province(models.Model):
    # Choices for surface_type
    CAN = 'Canada'
    US = 'United States'
    COUNTRY_CHOICES = (
        (CAN, _('Canada')),
        (US, _('United States')),
    )
    name = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("name (French)"))
    abbrev_eng = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("abbreviation (English)"))
    abbrev_fre = models.CharField(max_length=25, blank=True, null=True, verbose_name=_("abbreviation (French)"))
    country = models.CharField(max_length=25, choices=COUNTRY_CHOICES, verbose_name=_("country"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

# CONNECTED APPS: masterlist
# STILL NEED TO CONNECT:
class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))
    abbrev = models.CharField(max_length=10, verbose_name=_("abbreviation"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Branch(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))
    abbrev = models.CharField(max_length=10, verbose_name=_("abbreviation"))
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, verbose_name=_("region"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Division(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (French)"))
    abbrev = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("abbreviation"))
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, verbose_name=_("branch"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


# CONNECTED APPS: dm_tickets, travel, projects
# STILL NEED TO CONNECT: inventory
class Section(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (French)"))
    division = models.ForeignKey(Division, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="sections")
    head = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("section head"),
                             related_name="shared_models_sections")
    abbrev = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("abbreviation"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]

    @property
    def full_name(self):
        my_str = "{} - {} - {} - {}".format(self.division.branch.region, self.division.branch, self.division, self.name)
        return my_str

########################


class Probe(models.Model):
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


class Institute(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, verbose_name=_("abbreviation"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):
            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


class Vessel(models.Model):
    name = models.CharField(max_length=255)
    call_sign = models.CharField(max_length=56, null=True, blank=True)

    def __str__(self):
        if self.call_sign:
            return "{} {}".format(self.name, self.call_sign)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['name', ]


# oceanography
# diets
# snowcrab
class Cruise(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.DO_NOTHING, blank=True, null=True)
    mission_name = models.CharField(max_length=255)
    mission_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    chief_scientist = models.CharField(max_length=255)
    samplers = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    probe = models.ForeignKey(Probe, null=True, blank=True, on_delete=models.DO_NOTHING)
    area_of_operation = models.CharField(max_length=255, null=True, blank=True)
    number_of_profiles = models.IntegerField()
    meds_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="MEDS ID")
    notes = models.CharField(max_length=255, null=True, blank=True)
    season = models.IntegerField(null=True, blank=True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, related_name="missions", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_date:
            self.season = self.start_date.year
        return super().save(*args, **kwargs)

#########################################

# species model
# person
