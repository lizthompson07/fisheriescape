from django import forms
from django.core import validators
from . import models
from django.utils.safestring import mark_safe

class SamplerForm(forms.ModelForm):
    class Meta:
        model = models.Sampler
        fields = "__all__"
        widgets = {
            'notes':forms.Textarea(attrs={'rows': '3'}),
        }

class PortSampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = "__all__"
        exclude = ['old_id', 'season', "tests", "length_frequencies", 'lab_processing_complete', "otolith_processing_complete", "vessel"]
        labels={
            'sampler':mark_safe("Sampler (<a href='#' id='add_sampler' >add</a>)"),
            'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'remarks':forms.Textarea(attrs={'rows': '5'}),
            'sample_date':forms.DateInput(attrs={'type': 'date'}),
            'creation_date':forms.HiddenInput(),
            'created_by':forms.HiddenInput(),
            'last_modified_date':forms.HiddenInput(),
            'last_modified_by':forms.HiddenInput(),
            'sampling_protocol':forms.HiddenInput(),
            'latitude_n':forms.NumberInput(),
            'longitude_w':forms.NumberInput(),
            'vessel_cfvn':forms.TextInput(),
        }

class PortSampleFishMeasuredForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_measured", "last_modified_by"]
        labels={
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'last_modified_by':forms.HiddenInput(),
        }

class PortSampleFishPreservedForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = ["total_fish_preserved", "last_modified_by"]
        labels={
            # 'district':mark_safe("District (<a href='#' >search</a>)"),
            # 'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'last_modified_by':forms.HiddenInput(),
        }


class LengthFrquencyWizardSetupForm(forms.Form):
    minimum_length = forms.FloatField(required=True,min_value=0, max_value=50, widget=forms.NumberInput(attrs={'placeholder': 'mulitple of 0.5 cm'}))
    maximum_length = forms.FloatField(required=True,min_value=0, max_value=50, widget=forms.NumberInput(attrs={'placeholder': 'mulitple of 0.5 cm'}))

    def clean_minimum_length(self):
        minimum_length = self.cleaned_data['minimum_length']
        if minimum_length % 0.5 > 0: #if length is not divisible by 0.5
            raise forms.ValidationError("Number must be a multiple of 0.5!")
        return minimum_length

    def clean_maximum_length(self):
        maximum_length = self.cleaned_data['maximum_length']
        if maximum_length % 0.5 > 0: #if length is not divisible by 0.5
            raise forms.ValidationError("Number must be a multiple of 0.5!")
        elif maximum_length < self.cleaned_data['minimum_length']:
            raise forms.ValidationError("Maxium length must be greater than or equal to minimum length!")
        return maximum_length

class LengthFrquencyWizardForm(forms.Form):
    count = forms.IntegerField(required=True, min_value=0, max_value=1000, widget=forms.NumberInput(attrs={'placeholder': 'Number of fish observed'}))

class FishForm(forms.ModelForm):
    class Meta:
        model = models.FishDetail
        exclude = ["lab_processed_date", "otolith_processed_date", "creation_date", "last_modified_date"]

        widgets = {
            'sample':forms.HiddenInput(),
            'remarks':forms.Textarea(attrs={'rows': '5'}),
            'created_by':forms.HiddenInput(),
            'last_modified_by':forms.HiddenInput(),
        }

class LabSampleForm(forms.ModelForm):
    improbable_field = forms.CharField(widget=forms.HiddenInput(), required = False)
    improbable_test = forms.CharField(widget=forms.HiddenInput(), required = False)
    improbable_accepted = forms.CharField(widget=forms.HiddenInput(), required = False)

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
        ]

        widgets = {
            "fish_length":forms.HiddenInput(),
            "fish_weight":forms.HiddenInput(),
            "sex":forms.HiddenInput(),
            "maturity":forms.HiddenInput(),
            "gonad_weight":forms.HiddenInput(),
            "parasite":forms.HiddenInput(),
            "remarks":forms.HiddenInput(),
            "lab_sampler":forms.HiddenInput(),
            "last_modified_by":forms.HiddenInput(),

        }
    # def clean_fish_length(self):
    #     value = self.cleaned_data['fish_length']
    #     print(str(value) + " is the value")
    #     if value == 1:
    #         print("hera!")
    #         raise forms.ValidationError("bullshit!!")
    #     return value



class OtolithForm(forms.ModelForm):
    improbable_field = forms.CharField(widget=forms.HiddenInput(), required = False)
    improbable_test = forms.CharField(widget=forms.HiddenInput(), required = False)
    improbable_accepted = forms.CharField(widget=forms.HiddenInput(), required = False)

    class Meta:
        model = models.FishDetail
        # exclude = ["lab_processed_date", "otolith_processed_date"]
        fields = [
          "otolith_sampler",
          "annulus_count",
          "otolith_season",
          "otolith_image_remote_filepath",
          "remarks",
          "last_modified_by",
        ]
        labels = {
            "otolith_image_remote_filepath":"Filepath to image"
        }
        widgets = {
            "fish_length":forms.HiddenInput(),
            "fish_weight":forms.HiddenInput(),
            "sex":forms.HiddenInput(),
            "maturity":forms.HiddenInput(),
            "gonad_weight":forms.HiddenInput(),
            "parasite":forms.HiddenInput(),
            "remarks":forms.Textarea(attrs={"rows":5}),
            "otolith_sampler":forms.HiddenInput(),
            "last_modified_by":forms.HiddenInput(),

        }
