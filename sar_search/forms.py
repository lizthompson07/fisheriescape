from django import forms
from django.core import validators
from django.forms import modelformset_factory

from shared_models import models as shared_models

from . import models

attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date = {"class": "fp-date", "placeholder": "Select Date.."}
multi_select_js = {"class": "multi-select"}
chosen_js = {"class": "chosen-select-contains"}


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        exclude = ["date_last_modified", "temp_file"]
        widgets = {
            "province_range": forms.SelectMultiple(attrs=multi_select_js),
            "last_modified_by": forms.HiddenInput(),
        }


class RecordForm(forms.ModelForm):
    class Meta:
        model = models.Record
        exclude = ["date_last_modified"]
        widgets = {
            # "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            # "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            # "directions": forms.Textarea(attrs={"rows": "3", }),
            "counties": forms.SelectMultiple(attrs=multi_select_js),
            "last_modified_by": forms.HiddenInput(),
            "species": forms.HiddenInput(),

        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if kwargs.get("instance") or kwargs.get("initial"):
    #         self.fields["river"].widget = forms.HiddenInput()



class TaxonForm(forms.ModelForm):
    class Meta:
        model = models.Taxon
        fields = "__all__"


TaxonFormSet = modelformset_factory(
    model=models.Taxon,
    form=TaxonForm,
    extra=1,
)


class SpeciesStatusForm(forms.ModelForm):
    class Meta:
        model = models.SpeciesStatus
        fields = "__all__"


SpeciesStatusFormSet = modelformset_factory(
    model=models.SpeciesStatus,
    form=SpeciesStatusForm,
    extra=1,
)


class SARAScheduleForm(forms.ModelForm):
    class Meta:
        model = models.SARASchedule
        fields = "__all__"


SARAScheduleFormSet = modelformset_factory(
    model=models.SARASchedule,
    form=SARAScheduleForm,
    extra=1,
)


class CountyForm(forms.ModelForm):
    class Meta:
        model = models.County
        fields = "__all__"


CountyFormSet = modelformset_factory(
    model=models.County,
    form=CountyForm,
    extra=1,
)


class CoordForm(forms.ModelForm):
    class Meta:
        model = models.RecordPoints
        fields = "__all__"
        widgets = {
            "record": forms.HiddenInput(),

        }
    

CoordFormSet = modelformset_factory(
    model=models.RecordPoints,
    form=CoordForm,
    extra=1,
)


CoordFormSetNoExtra = modelformset_factory(
    model=models.RecordPoints,
    form=CoordForm,
    extra=0,
)

#
# class RiverForm(forms.ModelForm):
#     class Meta:
#         model = shared_models.River
#         fields = "__all__"
#
#

#
# class SampleForm(forms.ModelForm):
#     class Meta:
#         model = models.Sample
#         exclude = ["last_modified", 'season']
#         widgets = {
#             "site": forms.HiddenInput(),
#             "last_modified_by": forms.HiddenInput(),
#             "samplers": forms.Textarea(attrs={"rows": "2", }),
#             "notes": forms.Textarea(attrs={"rows": "3", }),
#             "arrival_date": forms.DateTimeInput(attrs=attr_fp_date_time),
#             "departure_date": forms.DateTimeInput(attrs=attr_fp_date_time),
#         }
#
# class EntryForm(forms.ModelForm):
#     class Meta:
#         model = models.Entry
#         fields = "__all__"
#         widgets = {
#             'species': forms.HiddenInput(),
#             'sample': forms.HiddenInput(),
#             'notes': forms.Textarea(attrs={"rows": "3"}),
#             "date_tagged": forms.DateTimeInput(attrs=attr_fp_date),
#         }
#
#
# class ReportSearchForm(forms.Form):
#     REPORT_CHOICES = (
#         (None, "---"),
#         (1, "List of samples (trap data) (.CSV)"),
#         (2, "List of entries (fish data) (.CSV)"),
#         (3, "OPEN DATA - summary by site by year (.CSV)"),
#     )
#
#     report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
#     year = forms.CharField(required=False, widget=forms.NumberInput(), label="Year (optional)")
#     sites = forms.MultipleChoiceField(required=False, label="Sites (optional)")
#
#     # site = forms.ChoiceField(required=False)
#     # ais_species = forms.MultipleChoiceField(required=False, label="AIS species")
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         site_choices = [(obj.id, str(obj)) for obj in models.RiverSite.objects.all() if obj.samples.count() > 0]
#         self.fields['sites'].choices = site_choices
#
