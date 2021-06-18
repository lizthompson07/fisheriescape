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
    stay_on_page = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.Sample
        exclude = ['season']
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

        # make sure departure is after arrival
        arrival_date = cleaned_data.get("arrival_date")
        departure_date = cleaned_data.get("departure_date")
        if arrival_date and departure_date and departure_date < arrival_date:
            self.add_error('departure_date', gettext(
                "The departure date must be after the arrival date!"
            ))

        # make sure site characterization is null or 1
        percent_riffle = cleaned_data.get("percent_riffle")
        percent_run = cleaned_data.get("percent_run")
        percent_flat = cleaned_data.get("percent_flat")
        percent_pool = cleaned_data.get("percent_pool")
        if (percent_riffle or percent_run or percent_flat or percent_pool) and (
                nz(percent_riffle, 0) + nz(percent_run, 0) + nz(percent_flat, 0) + nz(percent_pool, 0) != 1):
            raise forms.ValidationError(
                gettext("Either site characterization must be left null or must equal to 1")
            )

        # make sure substrate characterization is null or 1
        percent_fine = cleaned_data.get("percent_fine")
        percent_sand = cleaned_data.get("percent_sand")
        percent_gravel = cleaned_data.get("percent_gravel")
        percent_pebble = cleaned_data.get("percent_pebble")
        percent_cobble = cleaned_data.get("percent_cobble")
        percent_rocks = cleaned_data.get("percent_rocks")
        percent_boulder = cleaned_data.get("percent_boulder")
        percent_bedrock = cleaned_data.get("percent_bedrock")
        if (percent_fine or percent_sand or percent_gravel or percent_pebble or percent_cobble or percent_rocks or percent_boulder or percent_bedrock) and (
                nz(percent_fine, 0) + nz(percent_sand, 0) + nz(percent_gravel, 0) + nz(percent_pebble, 0) + nz(percent_cobble, 0) + nz(percent_rocks, 0) + nz(
                percent_boulder, 0) + nz(percent_bedrock, 0) != 1):
            raise forms.ValidationError(
                gettext("Either substrate characterization must be left null or must equal to 1")
            )


class SweepForm(forms.ModelForm):
    class Meta:
        model = models.Sweep
        exclude = "__all__"

    def clean_sweep_number(self):
        sweep_number = self.cleaned_data['sweep_number']
        if (sweep_number != 0.5) and (sweep_number - int(sweep_number) != 0):
            raise forms.ValidationError("The sweep number must be equal to 0.5 or be a factors of 1!")
        return sweep_number


class ObservationForm(forms.ModelForm):
    class Meta:
        model = models.Observation
        fields = "__all__"
        widgets = {
            'sample': forms.HiddenInput(),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"


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


class MaturityForm(forms.ModelForm):
    class Meta:
        model = models.Maturity
        fields = "__all__"


MaturityFormset = modelformset_factory(
    model=models.Maturity,
    form=MaturityForm,
    extra=1,
)


class ElectrofisherForm(forms.ModelForm):
    class Meta:
        model = models.Electrofisher
        fields = "__all__"


ElectrofisherFormset = modelformset_factory(
    model=models.Electrofisher,
    form=ElectrofisherForm,
    extra=1,
)
