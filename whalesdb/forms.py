from django import forms
from whalesdb import models
import datetime

class DepForm(forms.ModelForm):
    class Meta:
        model = models.DepDeployment
        fields = ["stn", "dep_year", "dep_month", "dep_name", "prj", "mor"]


class MorForm(forms.ModelForm):
    class Meta:
        model = models.MorMooringSetup
        exclude = []
        widgets = {
            'mor_additional_equipment': forms.Textarea(attrs={"rows": 2}),
            'mor_general_moor_description': forms.Textarea(attrs={"rows": 2}),
            'mor_notes': forms.Textarea(attrs={"rows": 2}),
        }


class PrjForm(forms.ModelForm):

    class Meta:
        model = models.PrjProject
        exclude = []
        widgets = {
            'prj_description': forms.Textarea(attrs={"rows": 2}),
        }


class StnForm(forms.ModelForm):
    class Meta:
        model = models.StnStation
        exclude = []
        widgets = {
            'stn_notes': forms.Textarea(attrs={"rows": 2}),
        }


class SteForm(forms.ModelForm):

    class Meta:
        model = models.SteStationEvent
        exclude = []
        widgets = {
            'ste_date': forms.SelectDateWidget()
        }