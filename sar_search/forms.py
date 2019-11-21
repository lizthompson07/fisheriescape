from django import forms
from django.core import validators
from django.forms import modelformset_factory

from shared_models import models as shared_models

from . import models

attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prov_choices = [(obj.id, str(obj)) for obj in shared_models.Province.objects.filter(id__in=[7,1,3,4])]
        self.fields.get("province_range").choices = prov_choices


class RecordForm(forms.ModelForm):
    class Meta:
        model = models.Record
        exclude = ["date_last_modified"]
        widgets = {
            # "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            # "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            # "directions": forms.Textarea(attrs={"rows": "3", }),
            "regions": forms.SelectMultiple(attrs=multi_select_js),
            "last_modified_by": forms.HiddenInput(),
            "species": forms.HiddenInput(),

        }

class RegionPolygonForm(forms.ModelForm):
    class Meta:
        model = models.RegionPolygon
        exclude = ["date_last_modified"]
        widgets = {
            "last_modified_by": forms.HiddenInput(),
            "region": forms.HiddenInput(),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if kwargs.get("instance") or kwargs.get("initial"):
    #         self.fields["river"].widget = forms.HiddenInput()


class MapForm(forms.Form):
    north = forms.FloatField(required=False)
    south = forms.FloatField(required=False)
    east = forms.FloatField(required=False)
    west = forms.FloatField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        north = cleaned_data.get("north")
        south = cleaned_data.get("south")
        east = cleaned_data.get("east")
        west = cleaned_data.get("west")

        if not north or not south or not east or not west:
            raise forms.ValidationError("You must enter valid values for all directions.")


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

class CITESAppendixForm(forms.ModelForm):
    class Meta:
        model = models.CITESAppendix
        fields = "__all__"


CITESAppendixFormSet = modelformset_factory(
    model=models.CITESAppendix,
    form=CITESAppendixForm,
    extra=1,
)


class ResponsibleAuthorityForm(forms.ModelForm):
    class Meta:
        model = models.ResponsibleAuthority
        fields = "__all__"


ResponsibleAuthorityFormSet = modelformset_factory(
    model=models.ResponsibleAuthority,
    form=ResponsibleAuthorityForm,
    extra=1,
)


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        exclude = ["temp_file",]


RegionFormSet = modelformset_factory(
    model=models.Region,
    form=RegionForm,
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


class RPCoordForm(forms.ModelForm):
    class Meta:
        model = models.RegionPolygonPoint
        fields = "__all__"
        widgets = {
            "region_polygon": forms.HiddenInput(),
        }

RPCoordFormSet = modelformset_factory(
    model=models.RegionPolygonPoint,
    form=RPCoordForm,
    extra=1,
)
