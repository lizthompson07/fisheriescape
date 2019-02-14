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
    telephone1 = models.CharField(max_length=25, blank=True, null=True)
    telephone2 = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name', 'first_name']


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

class OrganizationMember(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name="members")
    position_title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['position_title']

    def __str__(self):
        return "{} ({})".format(self.person, self.position_title)

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
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")
    status = models.ForeignKey(Status, default=1, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("status"), related_name="entries")
    sector = models.ForeignKey(Sector, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")
    entry_type = models.ForeignKey(EntryType, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")
    initial_date = models.DateTimeField(verbose_name=_("initial date"))
    # leads = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("lead / contact"))
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="entries")

    # funding
    funding_needed = models.NullBooleanField(verbose_name=_("is funding needed?"))
    funding_requested = models.NullBooleanField(verbose_name=_("was funding requested?"))
    amount_expected = models.FloatField(blank=True, null=True, verbose_name=_("How much funding is expected?"))
    transferred = models.NullBooleanField(verbose_name=_("has any funding been transferred?"))
    amount_transferred = models.FloatField(blank=True, null=True, verbose_name=_("If yes, how much funding was transferred?"))
    fiscal_year = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("fiscal year/multiyear"))
    funding_purpose = models.ForeignKey(FundingPurpose, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("funding purpose"), related_name="entries")
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                              verbose_name=_("date last modified"))
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_("date created"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("last modified by"))
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
                                   verbose_name=_("created by"), related_name="user_entries")

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
