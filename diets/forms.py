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
        exclude = ["old_seq_num",]
        widgets = {
            "processing_date": forms.DateInput(attrs={"type": "date"}),
        }

class PreyForm(forms.ModelForm):
    class Meta:
        model = models.Prey
        fields = "__all__"
        widgets = {
            'species': forms.HiddenInput(),
            'predator': forms.HiddenInput(),
            'comments': forms.Textarea(attrs={"rows": "3"}),
        }


class SearchForm(forms.Form):
    CRUISE_CHOICES = ((None, "---"),)
    for obj in models.Cruise.objects.all():
        CRUISE_CHOICES = CRUISE_CHOICES.__add__(((obj.id, obj),))

    SPECIES_CHOICES = ((None, "---"),)
    for obj in models.Species.objects.all().order_by("id"):
        SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))
    processing_year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all years"}))
    processing_month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all months"}))
    cruise = forms.ChoiceField(required=False, choices=CRUISE_CHOICES)
    species = forms.ChoiceField(required=False, choices=SPECIES_CHOICES)

    field_order = ["processing_year", "processing_month", "cruise", "species"]
