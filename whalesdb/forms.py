from django import forms
from whalesdb import models


class DepForm(forms.ModelForm):
    class Meta:
        model = models.DepDeployment
        exclude = []


class MorForm(forms.ModelForm):
    class Meta:
        model = models.MorMooringSetup
        exclude = []
        widgets = {
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