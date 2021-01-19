from django import forms
from django.forms import modelformset_factory

from . import models

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"
        widgets = {
            'fishery_area': forms.SelectMultiple(attrs=chosen_js),
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
        }


class FisheryAreaForm(forms.ModelForm):
    class Meta:
        model = models.FisheryArea
        fields = "__all__"
        widgets = {

        }
