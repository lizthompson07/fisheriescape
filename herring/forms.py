from django import forms
from django.core import validators
from . import models
from django.utils.safestring import mark_safe


class PortSampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = "__all__"
        exclude = ['old_id', 'season']
        labels={
            'district':mark_safe("District (<a href='#' >search</a>)"),
            'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        }
        widgets = {
            'remarks':forms.Textarea(attrs={'rows': '5'}),
            'sample_date':forms.DateInput(attrs={'type': 'date'}),
            'creation_date':forms.HiddenInput(),
            'created_by':forms.HiddenInput(),
            'last_modified_date':forms.HiddenInput(),
            'last_modified_by':forms.HiddenInput(),
            'sampling_protocol':forms.HiddenInput(),
            'latitude_n':forms.NumberInput(attrs={'placeholder':"dd.ddddd"}),
            'longitude_w':forms.NumberInput(attrs={'placeholder':"dd.ddddd"}),

        }
