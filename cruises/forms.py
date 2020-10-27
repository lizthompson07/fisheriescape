from django import forms
from django.core import validators
from . import models
from django.utils.safestring import mark_safe
from shared_models import models as shared_models


class CruiseForm(forms.ModelForm):
    class Meta:
        model = shared_models.Cruise
        exclude = ["season",]
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'start_date':forms.DateInput(attrs={'type': 'date'}),
            'end_date':forms.DateInput(attrs={'type': 'date'}),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = ["date_created",]
        # fields = "__all__"
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'mission':forms.HiddenInput(),
            # 'end_date':forms.DateInput(attrs={'type': 'date'}),
        }
