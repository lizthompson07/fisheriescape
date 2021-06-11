from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from . import models

attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}
multi_select_js = {"class": "multi-select"}
chosen_js = {"class": "chosen-select-contains"}


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class RiverForm(forms.ModelForm):
    class Meta:
        model = shared_models.River
        fields = "__all__"


class RiverSiteForm(forms.ModelForm):
    class Meta:
        model = models.RiverSite
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "directions": forms.Textarea(attrs={"rows": "3", }),
        }


class SampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = ["last_modified", 'season']
        widgets = {
            "site": forms.Select(attrs=chosen_js),
            "samplers": forms.Textarea(attrs={"rows": "2", }),
            "notes": forms.Textarea(attrs={"rows": "3", }),
            "arrival_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M:%S"),
            "departure_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M:%S"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        site_choices = [(obj.id, f"{obj.river} --> {obj.name} ({nz(obj.province, 'unknown prov.')})") for obj in models.RiverSite.objects.all()]
        site_choices.insert(0, (None, "-----"))
        self.fields["site"].choices = site_choices

    def clean(self):
        cleaned_data = super().clean()
        arrival_date = cleaned_data.get("arrival_date")
        departure_date = cleaned_data.get("departure_date")
        if departure_date < arrival_date:
            self.add_error('departure_date', gettext(
                "The departure date must be after the arrival date!"
            ))


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        fields = "__all__"
        widgets = {
            'species': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": "3"}),
            "date_tagged": forms.DateTimeInput(attrs=attr_fp_date),
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "---"),
        (1, "List of samples (trap data) (CSV)"),
        (2, "List of entries (fish data) (CSV)"),
        (3, "OPEN DATA - summary by site by year (CSV)"),
        (4, "OPEN DATA - data dictionary (CSV)"),
        (7, "OPEN DATA - species list (CSV)"),
        (5, "OPEN DATA - web mapping service (WMS) report ENGLISH (CSV)"),
        (6, "OPEN DATA - web mapping service (WMS) report FRENCH (CSV)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    year = forms.CharField(required=False, widget=forms.NumberInput(), label="Year (optional)")
    sites = forms.MultipleChoiceField(required=False, label="Sites (optional)")

    # site = forms.ChoiceField(required=False)
    # ais_species = forms.MultipleChoiceField(required=False, label="AIS species")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.count() > 0]
        self.fields['sites'].choices = site_choices


class SampleTypeForm(forms.ModelForm):
    class Meta:
        model = models.SampleType
        fields = "__all__"


SampleTypeFormset = modelformset_factory(
    model=models.SampleType,
    form=SampleTypeForm,
    extra=1,
)


class StatusForm(forms.ModelForm):
    class Meta:
        model = models.Status
        fields = "__all__"


StatusFormset = modelformset_factory(
    model=models.Status,
    form=StatusForm,
    extra=1,
)


class SexForm(forms.ModelForm):
    class Meta:
        model = models.Sex
        fields = "__all__"


SexFormset = modelformset_factory(
    model=models.Sex,
    form=SexForm,
    extra=1,
)


class LifeStageForm(forms.ModelForm):
    class Meta:
        model = models.LifeStage
        fields = "__all__"


LifeStageFormset = modelformset_factory(
    model=models.LifeStage,
    form=LifeStageForm,
    extra=1,
)


class OriginForm(forms.ModelForm):
    class Meta:
        model = models.Origin
        fields = "__all__"


OriginFormset = modelformset_factory(
    model=models.Origin,
    form=OriginForm,
    extra=1,
)
