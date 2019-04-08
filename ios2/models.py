from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from textile import textile
from lib.functions.fiscal_year import fiscal_year
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from datetime import date, timedelta, datetime


class Instrument(models.Model):
    TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP'), ('OXY', 'OXY')]
    # fiscal_year = models.CharField(max_length=50, default="2019-2020", verbose_name=_("fiscal year"))
    # year = models.TextField(verbose_name=("Instrument title"))
    instrument_type = models.CharField(max_length=20, default='CTD', verbose_name=_("Instrument Type"), choices=TYPE_CHOICES)
    serial_number = models.CharField(max_length=20, default='0000', verbose_name=_("Serial ID"))
    purchase_date = models.DateField(blank=True, null=True, verbose_name=_("Purchase Date"))
    project_title = models.TextField(blank=True, null=True, verbose_name=_("Project title"))
    scientist = models.TextField(blank=True, null=True, verbose_name=_("Scientist"))
    # location = models..... (default=..)

    date_of_last_service = models.DateField(blank=True, null=True,
                                            verbose_name=_("Last Service Date"))
    date_of_next_service = models.DateField(blank=True, null=True,
                                            verbose_name=_("Next Service Date"))
    # last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
    #                                      verbose_name=_("last modified by"))
    submitted = models.BooleanField(default=False, verbose_name=_("Submit instrument for review"))

    class Meta:
        ordering = ['instrument_type', 'serial_number', 'purchase_date', 'project_title']
        unique_together = ['instrument_type', 'serial_number']

    def __str__(self):
        # return "{}".format(self.project_title)

        return "{}".format(self.instrument_type) + " {}".format(self.serial_number)


    def get_absolute_url(self):
        return reverse('ios2:instrument_detail', kwargs={'pk': self.pk})


class Mooring(models.Model):

    # instruments = models.ManyToManyField(Instrument, through='InstrumentMooring')

    mooring = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("mooring name"))
    mooring_number = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("mooring number"))
    deploy_time = models.DateTimeField(blank=True, null=True,
                                       verbose_name=_("deploy time (UTC)"))
    recover_time = models.DateTimeField(blank=True, null=True,
                                        verbose_name=_("recover time (UTC)"))

    lat = models.TextField(blank=True, null=True, verbose_name=_("lat"))
    lon = models.TextField(blank=True, null=True, verbose_name=_("lon"))
    depth = models.TextField(blank=True, null=True, verbose_name=_("depth"))
    # comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))
    submitted = models.BooleanField(default=False, verbose_name=_("Submit moorings for review"))

    def __str__(self):
        return "{}".format(self.mooring) + " {}".format(self.mooring_number)

    class Meta:
        ordering = ['mooring', 'mooring_number']
        unique_together = ['mooring', 'mooring_number']


class InstrumentMooring(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.DO_NOTHING,
                                   related_name="instrudeploy", verbose_name=_("instrument"))
    mooring = models.ForeignKey(Mooring, on_delete=models.DO_NOTHING,
                                related_name="instrudeploy", verbose_name=_("mooring"))
    depth = models.TextField(blank=True)

    def __str__(self):

        return "{}".format(self.instrument) + " {}".format(self.mooring)
    class Meta:
        # ordering = ['mooring', 'mooring_number']
        # auto_created = True
        unique_together = ['instrument', 'mooring']




