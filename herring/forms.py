from django import forms
from django.core import validators
from django.utils import timezone

from . import models
from django.utils.safestring import mark_safe

chosen_js = {"class": "chosen-select-contains"}


class SamplerForm(forms.ModelForm):
    class Meta:
        model = models.Sampler
        fields = "__all__"
        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
        }


class SampleForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Sample
        fields = "__all__"
        exclude = ['old_id', 'season', "tests", "length_frequencies", 'lab_processing_complete', "otolith_processing_complete", 'district']
        labels = {
            # 'sampler':mark_safe("Sampler (<a href='#' id='add_sampler' >add</a>)"),
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            'vessel_cfvn': "Vessel CFVN",
            # 'survey_id': "Survey ID",
        }
        attr_dict = {"class": "tab", }

        widgets = {
            'remarks': forms.Textarea(attrs={'rows': '5', "class": "tab", }),
            'sample_date': forms.DateInput(attrs={'type': 'date', "class": "tab", }),
            'creation_date': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
            'last_modified_date': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            # 'sampling_protocol':forms.HiddenInput(),
            'latitude_n': forms.TextInput(attrs=attr_dict),
            'longitude_w': forms.TextInput(attrs=attr_dict),
            # 'vessel_cfvn':forms.TextInput(),
            'sampler_ref_number': forms.TextInput(attrs=attr_dict),
            'sampler': forms.Select(attrs=attr_dict),
            'port': forms.Select(attrs=attr_dict),
            'fishing_area': forms.Select(attrs=attr_dict),
            'gear': forms.Select(attrs=attr_dict),
            'experimental_net_used': forms.Select(attrs=attr_dict),
            'vessel_cfvn': forms.TextInput(attrs=attr_dict),
            'mesh_size': forms.Select(attrs=attr_dict),
            'catch_weight_lbs': forms.NumberInput(attrs=attr_dict),
            'sample_weight_lbs': forms.NumberInput(attrs=attr_dict),
            'total_fish_measured': forms.NumberInput(attrs=attr_dict),
            'total_fish_preserved': forms.NumberInput(attrs=attr_dict),
        }


class SampleFishMeasuredForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_measured", "last_modified_by"]
        labels = {
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class SampleFishPreservedForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_preserved", "last_modified_by"]
        labels = {
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'last_modified_by': forms.HiddenInput(),
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
            "lab_sampler",
            "last_modified_by",
            "test_204_accepted",
            "test_207_accepted",
            # "test_302_accepted",
            # "test_305_accepted",
            # "test_308_accepted",
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
            "lab_sampler": forms.HiddenInput(attrs=attr_dict),
            "last_modified_by": forms.HiddenInput(),

            "test_204_accepted": forms.TextInput(attrs=attr_dict_1),
            "test_207_accepted": forms.TextInput(attrs=attr_dict_1),
            # "test_302_accepted":forms.TextInput(attrs=attr_dict_1),
            # "test_305_accepted":forms.TextInput(attrs=attr_dict_1),
            # "test_308_accepted":forms.TextInput(attrs=attr_dict_1),
        }


class OtolithForm(forms.ModelForm):
    last_fish = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    where_to = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.FishDetail
        # exclude = ["lab_processed_date", "otolith_processed_date"]
        fields = [
            "otolith_sampler",
            "annulus_count",
            "otolith_season",
            "fish_length",
            # "otolith_image_remote_filepath",
            "remarks",
            "last_modified_by",
            "test_209_accepted",
            # "test_311_accepted",
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
            "otolith_sampler": forms.HiddenInput(attrs=attr_dict),
            "last_modified_by": forms.HiddenInput(),
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
