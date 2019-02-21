from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Province(models.Model):
    # Choices for surface_type
    CAN = 'Canada'
    US = 'United States'
    COUNTRY_CHOICES = (
        (CAN, 'Canada'),
        (US, 'United States'),
    )
    name_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Name (English)"))
    name_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Name (French)"))
    country = models.CharField(max_length=25, choices=COUNTRY_CHOICES)
    abbrev_eng = models.CharField(max_length=25, blank=True, null=True)
    abbrev_fre = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name_eng"))))


class Sector(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Grouping(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_1 = models.CharField(max_length=25, blank=True, null=True)
    phone_2 = models.CharField(max_length=25, blank=True, null=True)
    fax = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('ihub:person_detail', kwargs={'pk': self.pk})

    @property
    def contact_card(self):
        my_str = "<b>{first} {last}</b>".format(first=self.first_name, last=self.last_name)
        if self.phone_1:
            my_str += "<br>Phone 1: {}".format(self.phone_1)
        if self.phone_2:
            my_str += "<br>Phone 2: {}".format(self.phone_2)
        if self.fax:
            my_str += "<br>Fax: {}".format(self.fax)
        if self.email:
            my_str += "<br>E-mail: {}".format(self.email)
        return my_str

    @property
    def contact_card_no_name(self):
        my_str = ""
        if self.phone_1:
            my_str += "<br>Phone 1: {}".format(self.phone_1)
        if self.phone_2:
            my_str += "<br>Phone 2: {}".format(self.phone_2)
        if self.fax:
            my_str += "<br>Fax: {}".format(self.fax)
        if self.email:
            my_str += "<br>E-mail: {}".format(self.email)
        return my_str


class Organization(models.Model):
    name_eng = models.CharField(max_length=1000, verbose_name=_("english Name"))
    name_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("french Name"))
    name_ind = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("indigenous Name"))
    abbrev = models.CharField(max_length=30, verbose_name=_("abbreviation"))
    address = models.CharField(max_length=1000, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=7, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    fax = models.CharField(max_length=25, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    grouping = models.ManyToManyField(Grouping)

    # specific for indigenous organizations
    next_election = models.CharField(max_length=100, blank=True, null=True)
    election_term = models.CharField(max_length=100, blank=True, null=True)
    population_on_reserve = models.IntegerField(blank=True, null=True)
    population_off_reserve = models.IntegerField(blank=True, null=True)
    population_other_reserve = models.IntegerField(blank=True, null=True)
    fin = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("FIN"))

    def __str__(self):
        return "{}".format(self.name_eng)

    class Meta:
        ordering = ['name_eng']

    @property
    def full_address(self):
        # initial my_str with either address or None
        if self.address:
            my_str = self.address
        else:
            my_str = ""
        # add city
        if self.city:
            if my_str:
                my_str += ", "
            my_str += self.city
        # add province abbrev.
        if self.province:
            if my_str:
                my_str += ", "
            my_str += self.province.abbrev_eng
        # add postal code
        if self.postal_code:
            if my_str:
                my_str += ", "
            my_str += self.postal_code
        return my_str

    def get_absolute_url(self):
        return reverse('ihub:org_detail', kwargs={'pk': self.pk})


class MemberRole(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name (English)"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name (French)"))

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class OrganizationMember(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    roles = models.ManyToManyField(MemberRole)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["organization", "person"]
        unique_together = ["organization", "person"]

    def __str__(self):
        return "{}".format(self.person)
