from django import forms
from django.core import validators
from . import models
from django.utils.safestring import mark_safe


class DocForm(forms.ModelForm):
    class Meta:
        model = models.Doc
        fields = "__all__"
        labels={
            'district':mark_safe("District (<a href='#' >search</a>)"),
            'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'description':forms.Textarea(attrs={'rows': '5'}),
            'source':forms.Textarea(attrs={'rows': '5'}),

        }

class MissionForm(forms.ModelForm):
    class Meta:
        model = models.Mission
        exclude = ["season",]
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'start_date':forms.DateInput(attrs={'type': 'date'}),
            'end_date':forms.DateInput(attrs={'type': 'date'}),
        }

class BottleForm(forms.ModelForm):
    class Meta:
        model = models.Bottle
        exclude = ["mission",]
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'start_date':forms.DateInput(attrs={'type': 'date'}),
            'end_date':forms.DateInput(attrs={'type': 'date'}),
        }
