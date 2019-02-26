from django import forms
from django.core import validators
from . import models


class CruiseForm(forms.ModelForm):
    class Meta:
        model = models.Cruise
        fields = "__all__"


class DigestionForm(forms.ModelForm):
    class Meta:
        model = models.DigestionLevel
        fields = "__all__"


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class PredatorForm(forms.ModelForm):
    class Meta:
        model = models.Predator
        exclude = ["old_seq_num", ]
        widgets = {
            "processing_date": forms.DateInput(attrs={"type": "date"}),
        }


class PreyForm(forms.ModelForm):
    class Meta:
        model = models.Prey
        exclude = ["stomach_wt_g", "sensor_used"]
        widgets = {
            'species': forms.HiddenInput(),
            'predator': forms.HiddenInput(),
            'comments': forms.Textarea(attrs={"rows": "3"}),
        }


class SearchForm(forms.Form):
    CRUISE_CHOICES = [(obj.id, str(obj)) for obj in models.Cruise.objects.all()]
    SPECIES_CHOICES = [(obj.id, str(obj)) for obj in models.Species.objects.all()]

    cruise = forms.ChoiceField(required=False, choices=CRUISE_CHOICES)
    species = forms.ChoiceField(required=False, choices=SPECIES_CHOICES)

    field_order = ["cruise", "species"]
