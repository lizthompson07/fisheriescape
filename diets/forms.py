from django import forms
from . import models
from shared_models import models as shared_models


class CruiseForm(forms.ModelForm):
    class Meta:
        model = shared_models.Cruise
        fields = ["mission_number",
                  "description",
                  "chief_scientist",
                  "samplers",
                  "start_date",
                  "end_date",
                  "notes",
                  "season",
                  "vessel", ]


class DigestionForm(forms.ModelForm):
    class Meta:
        model = models.DigestionLevel
        fields = "__all__"


class SamplerForm(forms.ModelForm):
    class Meta:
        model = models.Sampler
        fields = "__all__"


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class PredatorForm(forms.ModelForm):
    class Meta:
        model = models.Predator
        exclude = ["old_seq_num", "date_last_modified", "stratum", "somatic_wt_g"]

        widgets = {
            "processing_date": forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
        }


class PreyForm(forms.ModelForm):
    class Meta:
        model = models.Prey
        exclude = ["stomach_wt_g", "sensor_used", "date_last_modified"]
        widgets = {
            'species': forms.HiddenInput(),
            'predator': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'comments': forms.Textarea(attrs={"rows": "3"}),
        }


class SearchForm(forms.Form):
    CRUISE_CHOICES = [(obj.id, str(obj)) for obj in shared_models.Cruise.objects.all()]
    SPECIES_CHOICES = [(obj.id, str(obj)) for obj in models.Species.objects.all()]

    cruise = forms.ChoiceField(required=False, choices=CRUISE_CHOICES)
    species = forms.ChoiceField(required=False, choices=SPECIES_CHOICES)

    field_order = ["cruise", "species"]
