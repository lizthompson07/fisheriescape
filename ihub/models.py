from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import os
import uuid
from django.utils.translation import gettext_lazy as _

from lib.functions.fiscal_year import fiscal_year
from lib.functions.nz import nz


class Province(models.Model):
    # Choices for surface_type
    CAN = 'Canada'
    US = 'United States'
    COUNTRY_CHOICES = (
        (CAN, 'Canada'),
        (US, 'United States'),
    )
    name_eng = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Name (EN)"))
    name_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Name (FR)"))
    country = models.CharField(max_length=25, choices=COUNTRY_CHOICES)
    abbrev_eng = models.CharField(max_length=25, blank=True, null=True)
    abbrev_fre = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name_eng"))))


class Grouping(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

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


class Organization(models.Model):
    name_eng = models.CharField(max_length=1000, verbose_name=_("english Name"))
    name_fre = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("french Name"))
    name_ind = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("indigenous Name"))
    abbrev = models.CharField(max_length=30, verbose_name=_("abbreviation"))
    address = models.CharField(max_length=1000, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=7, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, null=True)
    grouping = models.ManyToManyField(Grouping)
    phone = models.CharField(max_length=25, blank=True, null=True)
    fax = models.CharField(max_length=25, blank=True, null=True)
    next_election = models.CharField(max_length=100, blank=True, null=True)
    election_term = models.CharField(max_length=100, blank=True, null=True)
    population_on_reserve = models.IntegerField(blank=True, null=True)
    population_off_reserve = models.IntegerField(blank=True, null=True)
    population_other_reserve = models.IntegerField(blank=True, null=True)
    fin = models.CharField(max_length=100, blank=True, null=True, verbose_name="FIN")
    notes = models.TextField(blank=True, null=True)

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
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

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


class EntryType(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Status(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class FundingPurpose(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Sector(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Region(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("name"))))

    class Meta:
        ordering = ['name', ]


class Entry(models.Model):
    # basic
    title = models.CharField(max_length=1000, blank=True, null=True)
    initial_date = models.DateTimeField(verbose_name=_("initial date"))
    organizations = models.ManyToManyField(Organization, related_name="entries")
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"),
                               related_name="entries")
    sector = models.ForeignKey(Sector, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")
    entry_type = models.ForeignKey(EntryType, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")
    regions = models.ManyToManyField(Region, related_name="entries")

    # funding
    funding_needed = models.NullBooleanField(verbose_name=_("is funding needed"))
    funding_purpose = models.ForeignKey(FundingPurpose, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("funding purpose"), related_name="entries")
    amount_requested = models.FloatField(blank=True, null=True, verbose_name=_("funding requested"))
    amount_approved = models.FloatField(blank=True, null=True, verbose_name=_("funding approved"))
    amount_transferred = models.FloatField(blank=True, null=True, verbose_name=_("amount transferred"))
    amount_lapsed = models.FloatField(blank=True, null=True, verbose_name=_("amount lapsed"))
    fiscal_year = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("fiscal year/multiyear"))

    # meta
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now, verbose_name=_("date last modified"))
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_("date created"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("last modified by"))
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("created by"),
                                   related_name="user_entries")

    class Meta:
        ordering = ['-date_created', ]

    def __str__(self):
        return "{}".format(self.title)

    def save(self, *args, **kwargs):
        self.date_last_modified = timezone.now()
        self.fiscal_year = fiscal_year(date=self.initial_date)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ihub:entry_detail', kwargs={'pk': self.pk})

    @property
    def amount_outstanding(self):
        return nz(self.amount_approved, 0) - nz(self.amount_transferred, 0) - nz(self.amount_lapsed, 0)


class EntryPerson(models.Model):
    # Choices for role
    LEAD = 1
    CONTACT = 2
    ROLE_CHOICES = (
        (LEAD, 'Lead'),
        (CONTACT, 'Contact'),
    )
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="people", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"))
    name = models.CharField(max_length=50, blank=True, null=True)
    organization = models.CharField(max_length=50)
    role = models.IntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        if self.user:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return "{}".format(self.name)

    class Meta:
        ordering = ['role', 'user__first_name', "user__last_name"]


class EntryNote(models.Model):
    # Choices for type
    ACTION = 1
    NEXTSTEP = 2
    COMMENT = 3
    TYPE_CHOICES = (
        (ACTION, 'Action'),
        (NEXTSTEP, 'Next step'),
        (COMMENT, 'Comment'),
    )

    entry = models.ForeignKey(Entry, related_name='notes', on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    note = models.TextField()
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"))

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-date"]


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/entry_<id>/<filename>
    return 'ihub/entry_{0}/{1}'.format(instance.entry.id, filename)


class File(models.Model):
    caption = models.CharField(max_length=255)
    entry = models.ForeignKey(Entry, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_directory_path)
    date_uploaded = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.caption


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
