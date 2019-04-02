from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from textile import textile
from lib.functions.fiscal_year import fiscal_year
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from datetime import date, timedelta, datetime

#
#
# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#
#
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.DO_NOTHING,)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)


class Instrument(models.Model):
    TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP')]
    # fiscal_year = models.CharField(max_length=50, default="2019-2020", verbose_name=_("fiscal year"))
    # year = models.TextField(verbose_name=("Instrument title"))
    instrument_type = models.CharField(max_length=20, default='CTD', verbose_name=_("Instrument Type"), choices=TYPE_CHOICES)
    serial_number = models.CharField(max_length=20, default='0000', verbose_name=_("Serial ID"))
    purchase_date = models.DateField(blank=True, null=True, verbose_name=_("Purchase Date"))
    project_title = models.TextField(blank=True, null=True, verbose_name=_("Project title"))
    scientist = models.TextField(blank=True, null=True, verbose_name=_("Scientist"))
    # location = models..... (default=..)
    test1 = models.ForeignKey('Deployment', on_delete=models.DO_NOTHING, null=True,
                                   related_name="testa", verbose_name=_("test1"))
    # test2 = models.ManyToManyField('Deployment', on_delete=models.DO_NOTHING,
    #                                related_name="testb", verbose_name=_("test2"))

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


class Deployment(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE,
                                   related_name="deployments", verbose_name=_("instrument"))
    # test2 = models.ManyToManyField(Instrument)
    # instruments = models.ManyToManyField(Instrument,
    #                                related_name="ins2", verbose_name=_("instruments"))
    # om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs", verbose_name=_("category"))
    # funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="om_costs",
    #                                    verbose_name=_("funding source"), default=1)
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
    # budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))

    def __str__(self):
        return "{}".format(self.mooring)

    class Meta:
        ordering = ['mooring']
        unique_together = ['mooring', 'mooring_number']



class InstrumentDeployment(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.DO_NOTHING,
                                   related_name="instrumentdeployments", verbose_name=_("instrument"))
    deployment = models.ForeignKey(Deployment, on_delete=models.DO_NOTHING,
                                   related_name="deploymentinstruments", verbose_name=_("deployment"))


# experiment1 = Experiment (location ='A1', instrument='CTD1')
#instrument.location ='A1'


