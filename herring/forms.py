from django import forms
from django.core import validators
from django.forms import modelformset_factory
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from shared_models.models import Port
from . import models
from django.utils.safestring import mark_safe

chosen_js = {"class": "chosen-select-contains"}


class FileForm(forms.Form):
    file = forms.FileField(label="File to import", required=True)


class HerringUserForm(forms.ModelForm):
    class Meta:
        model = models.HerringUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=chosen_js),
        }


HerringUserFormset = modelformset_factory(
    model=models.HerringUser,
    form=HerringUserForm,
    extra=1,
)


class SampleForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Sample
        fields = "__all__"
        widgets = {
            'sample_date': forms.DateInput(attrs={'type': 'date', "class": "tab", }),
            'sampler': forms.Select(attrs=chosen_js),
            'port': forms.Select(attrs=chosen_js),
            'fishing_area': forms.Select(attrs=chosen_js),
            'mesh_size': forms.Select(attrs=chosen_js),
            'gear': forms.Select(attrs=chosen_js),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        help_texts = {
            "gear": f"You can manage the list of gear types <a href='{reverse_lazy('herring:manage_gears')}'>here</a>",
            "mesh_size": f"You can manage the list of mesh sizes <a href='{reverse_lazy('herring:manage_mesh_sizes')}'>here</a>",
            "fishing_area": f"You can manage the list of fishing ares <a href='{reverse_lazy('herring:manage_fishing_areas')}'>here</a>",
            "sampler": f"You can manage the list of samplers <a href='{reverse_lazy('herring:manage_samplers')}'>here</a>",
        }

        for key in help_texts:
            self.fields[key].help_text = help_texts[key]


class SampleFishMeasuredForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_measured"]
        labels = {
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }


class SampleFishPreservedForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_preserved"]
        labels = {
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }


class LengthFrquencyWizardSetupForm(forms.Form):
    minimum_length = forms.FloatField(required=True, min_value=0, max_value=50,
                                      widget=forms.NumberInput(attrs={'placeholder': 'mulitple of 0.5 cm'}))
    maximum_length = forms.FloatField(required=True, min_value=0, max_value=50,
                                      widget=forms.NumberInput(attrs={'placeholder': 'mulitple of 0.5 cm'}))

    def clean_minimum_length(self):
        minimum_length = self.cleaned_data['minimum_length']
        if minimum_length % 0.5 > 0:  # if length is not divisible by 0.5
            raise forms.ValidationError("Number must be a multiple of 0.5!")
        return minimum_length

    def clean_maximum_length(self):
        maximum_length = self.cleaned_data['maximum_length']
        if maximum_length % 0.5 > 0:  # if length is not divisible by 0.5
            raise forms.ValidationError("Number must be a multiple of 0.5!")
        elif maximum_length < self.cleaned_data['minimum_length']:
            raise forms.ValidationError("Maxium length must be greater than or equal to minimum length!")
        return maximum_length


class LengthFrquencyWizardForm(forms.Form):
    count = forms.IntegerField(required=True, min_value=0, max_value=1000,
                               widget=forms.NumberInput(attrs={'placeholder': 'Number of fish observed'}))


class FishForm(forms.ModelForm):
    class Meta:
        model = models.FishDetail
        exclude = [
            "lab_processed_date", "otolith_processed_date", "creation_date", "last_modified_date",
            'test_204_accepted',
            'test_207_accepted',
            'test_209_accepted',
            'test_302_accepted',
            'test_305_accepted',
            'test_308_accepted',
            'test_311_accepted',
        ]

        widgets = {
            'sample': forms.Select(attrs=chosen_js),
            'remarks': forms.Textarea(attrs={'rows': '5'}),
            'created_by': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }


class LabSampleForm(forms.ModelForm):
    where_to = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.FishDetail
        # exclude = ["lab_processed_date", "otolith_processed_date"]
        fields = [
            "fish_length",
            "fish_weight",
            "sex",
            "maturity",
            "gonad_weight",
            "parasite",
            "remarks",
            "test_204_accepted",
            "test_207_accepted",
        ]

        attr_dict = {"class": "mandatory"}
        attr_dict_1 = {"class": "test_accept"}

        widgets = {
            "fish_length": forms.NumberInput(attrs=attr_dict),
            "fish_weight": forms.NumberInput(attrs=attr_dict),
            "sex": forms.Select(attrs=attr_dict),
            "maturity": forms.Select(attrs=attr_dict),
            "gonad_weight": forms.NumberInput(attrs=attr_dict),
            "parasite": forms.Select(attrs=attr_dict),
            "remarks": forms.Textarea(attrs={"rows": "3"}),

            "test_204_accepted": forms.TextInput(attrs=attr_dict_1),
            "test_207_accepted": forms.TextInput(attrs=attr_dict_1),
        }


class OtolithForm(forms.ModelForm):
    last_fish = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    where_to = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.FishDetail
        fields = [
            "annulus_count",
            "otolith_season",
            "fish_length",
            "remarks",
            "test_209_accepted",
        ]
        labels = {
            "otolith_image_remote_filepath": "Image filepath",
            "remarks": "Remarks (optional)",
        }

        attr_dict = {"class": "mandatory"}
        attr_dict_1 = {"class": "test_accept"}

        widgets = {
            "fish_length": forms.HiddenInput(),
            "remarks": forms.Textarea(attrs={"rows": 3}),
            "annulus_count": forms.TextInput(attrs=attr_dict),
            "otolith_season": forms.Select(attrs=attr_dict),

            "test_209_accepted": forms.TextInput(attrs=attr_dict_1),
            # "test_311_accepted":forms.TextInput(attrs=attr_dict_1),
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = [
        (1, "Progress Report"),
        (6, "Pretty sample export (csv)"),
        (2, "Pretty fish detail export (csv)"),
        (4, "Export hlog file (csv)"),
        (3, "Export hlen file (csv)"),
        (5, "Export hdet file (csv)"),
    ]
    REPORT_CHOICES.insert(0, (None, "------"))

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)

    field_order = ["report", "year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        year_choices = [(y["season"], y["season"]) for y in models.Sample.objects.order_by("-season").values('season').distinct()]

        self.fields['year'] = forms.ChoiceField(required=True, choices=year_choices)


class SamplerForm(forms.ModelForm):
    class Meta:
        model = models.Sampler
        fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
        }


SamplerFormset = modelformset_factory(
    model=models.Sampler,
    form=SamplerForm,
    extra=1,
)


class GearForm(forms.ModelForm):
    class Meta:
        model = models.Gear
        fields = "__all__"


GearFormset = modelformset_factory(
    model=models.Gear,
    form=GearForm,
    extra=1,
)


class FishingAreaForm(forms.ModelForm):
    class Meta:
        model = models.FishingArea
        fields = "__all__"


FishingAreaFormset = modelformset_factory(
    model=models.FishingArea,
    form=FishingAreaForm,
    extra=1,
)


class MeshSizeForm(forms.ModelForm):
    class Meta:
        model = models.MeshSize
        fields = "__all__"


MeshSizeFormset = modelformset_factory(
    model=models.MeshSize,
    form=MeshSizeForm,
    extra=1,
)


class PortForm(forms.ModelForm):
    class Meta:
        model = Port
        fields = "__all__"


PortFormset = modelformset_factory(
    model= Port,
    form=PortForm,
    extra=1,
)
