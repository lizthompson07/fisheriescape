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
    name_eng = models.CharField(max_length=1000, blank=True, null=True)
    name_fre = models.CharField(max_length=1000, blank=True, null=True)
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


class Organization(models.Model):
    name_eng = models.CharField(max_length=1000)
    name_fre = models.CharField(max_length=1000, blank=True, null=True)
    abbrev = models.CharField(max_length=30)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=7, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING, blank=True, null=True)
    grouping = models.ManyToManyField(Grouping)

    def __str__(self):
        return "{}".format(self.name_eng)

    class Meta:
        ordering = ['name_eng']


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
    leads = models.CharField(max_length=1000, blank=True, null=True)
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
