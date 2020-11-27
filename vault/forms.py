from django import forms
from . import models
from shared_models import models as shared_models

attr_fp_date_time = {"class": "fp-date-time-with-seconds", "placeholder": "Select Date and Time.."}


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class ObservationPlatformForm(forms.ModelForm):
    class Meta:
        model = models.ObservationPlatform
        fields = "__all__"


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = models.Instrument
        fields = "__all__"


class OutingForm(forms.ModelForm):
    class Meta:
        model = models.Outing
        fields = "__all__"
        widgets = {
            "start_date": forms.TextInput(attrs=attr_fp_date_time)
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = "__all__"


class ObservationForm(forms.ModelForm):
    class Meta:
        model = models.Observation
        fields = "__all__"
