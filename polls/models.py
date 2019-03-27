from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from textile import textile
from lib.functions.fiscal_year import fiscal_year
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING,)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Instrument(models.Model):
    # fiscal_year = models.CharField(max_length=50, default="2019-2020", verbose_name=_("fiscal year"))
    # year = models.TextField(verbose_name=("Instrument title"))
    purchase_date = models.DateTimeField(blank=True, null=True, verbose_name=("Purchase Date"))
    project_title = models.TextField(verbose_name=("Project title"))
    # instrument_type = models.TextField(verbose_name=("Instrument Type"))
    # last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,
    #                                      verbose_name=_("last modified by"))
    submitted = models.BooleanField(default=False, verbose_name=("Submit project for review"))


    def get_absolute_url(self):
        return reverse('polls:instrument_detail', kwargs={'pk': self.pk})