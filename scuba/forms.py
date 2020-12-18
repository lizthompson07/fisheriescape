from django import forms
from django.core import validators
from django.forms import modelformset_factory

from . import models

attr_fp_date_time = {"class": "fp-date-time-with-seconds", "placeholder": "Select Date and Time.."}
chosen_js = {"class": "chosen-select-contains"}
YES_NO_CHOICES = (
        (True, "Yes"),
        (False, "No"),
    )



class DiverForm(forms.ModelForm):
    class Meta:
        model = models.Diver
        fields = "__all__"


DiverFormset = modelformset_factory(
    model=models.Diver,
    form=DiverForm,
    extra=1,
)



class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = "__all__"




class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = "__all__"
