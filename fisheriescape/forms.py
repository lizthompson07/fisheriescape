# from django import forms
from django.contrib.gis import forms
from django.forms import modelformset_factory

from . import models
from .models import ROPE_CHOICES

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}


class MarineMammalForm(forms.ModelForm):
    class Meta:
        model = models.MarineMammal
        fields = "__all__"
        widgets = {

        }


MarineMammalFormSet = modelformset_factory(
    model=models.MarineMammal,
    form=MarineMammalForm,
    extra=1,
)


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"
        widgets = {

        }


SpeciesFormSet = modelformset_factory(
    model=models.Species,
    form=SpeciesForm,
    extra=1,
)


class FisheryForm(forms.ModelForm):
    class Meta:
        model = models.Fishery
        fields = "__all__"
        widgets = {
            'fishery_area': forms.SelectMultiple(attrs=chosen_js),
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
            'marine_mammals': forms.SelectMultiple(attrs=chosen_js),
            'mitigation': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(FisheryForm, self).__init__(*args, **kwargs)
        SORTED_ROPES = sorted(ROPE_CHOICES, key=lambda x: x[1])  # lambda needed to sort by second item in tuple
        self.fields['gear_primary_colour'].choices = SORTED_ROPES
        self.fields['gear_secondary_colour'].choices = SORTED_ROPES
        self.fields['gear_tertiary_colour'].choices = SORTED_ROPES


class FisheryAreaForm(forms.ModelForm):
    # polygon = forms.MultiPolygonField(widget=forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))

    class Meta:
        model = models.FisheryArea
        fields = "__all__"
        # polygon = forms.MultiPolygonField(widget=forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}))
        widgets = {
            'polygon': forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500})
        }


class FisheryAreaForm2(forms.ModelForm):
    class Meta:
        model = models.FisheryArea
        fields = "__all__"
        widgets = {
        }


class AnalysesForm(forms.ModelForm):
    class Meta:
        model = models.Analyses
        fields = "__all__"
        widgets = {
        }


class VulnerableSpeciesSpotForm(forms.Form):
    file = forms.FileField()

    class Meta:
        fields = ['file']
