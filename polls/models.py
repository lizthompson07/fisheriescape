from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from textile import textile
from lib.functions.fiscal_year import fiscal_year
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from datetime import date, timedelta, datetime



class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING,)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Instrument(models.Model):
    TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP')]
    # fiscal_year = models.CharField(max_length=50, default="2019-2020", verbose_name=_("fiscal year"))
    # year = models.TextField(verbose_name=("Instrument title"))
    purchase_date = models.DateField(blank=True, null=True, default=date.today, verbose_name=_("Purchase Date"))
    project_title = models.TextField(verbose_name=_("Project title"))
    instrument_type = models.CharField(max_length=20, default='CTD', verbose_name=_("Instrument Type"), choices=TYPE_CHOICES)
    serial_number = models.CharField(max_length=20, default='0000', verbose_name=_("Serial ID"))
    date_of_last_service = models.DateField(blank=True, null=True, default=date.today,
                                            verbose_name=_("Last Service Date"))
    date_of_next_service = models.DateField(blank=True, null=True, default=(datetime.now() + timedelta(days=365)),
                                            verbose_name=_("Next Service Date"))
    # last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
    #                                      verbose_name=_("last modified by"))
    submitted = models.BooleanField(default=False, verbose_name=_("Submit instrument for review"))

    class Meta:
        ordering = ['instrument_type', 'serial_number', 'purchase_date', 'project_title']

    def __str__(self):
        # return "{}".format(self.project_title)

        return "{}".format(self.instrument_type) + " {}".format(self.serial_number)


    def get_absolute_url(self):
        return reverse('polls:instrument_detail', kwargs={'pk': self.pk})


class Deployment(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE,
                                   related_name="deployments", verbose_name=_("instrument"))
    # om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs", verbose_name=_("category"))
    # funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, related_name="om_costs",
    #                                    verbose_name=_("funding source"), default=1)
    deploy_time = models.DateTimeField(blank=True, null=True, default=datetime.now(tz=timezone.utc),
                                       verbose_name=_("deploy_time"))
    recover_time = models.DateTimeField(blank=True, null=True, default=(datetime.now(tz=timezone.utc) + timedelta(days=365)),
                                        verbose_name=_("recover_time"))
    mooring = models.TextField(blank=True, null=True, verbose_name=_("mooring_name"))
    mooring_number = models.TextField(blank=True, null=True, verbose_name=_("mooring_number"))
    lat = models.TextField(blank=True, null=True, verbose_name=_("lat"))
    lon = models.TextField(blank=True, null=True, verbose_name=_("lon"))
    depth = models.TextField(blank=True, null=True, verbose_name=_("depth"))
    # comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))
    # budget_requested = models.FloatField(default=0, verbose_name=_("budget requested"))

    def __str__(self):
        return "{}".format(self.mooring)

    class Meta:
        ordering = ['instrument', 'mooring']
