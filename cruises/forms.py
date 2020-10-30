from django import forms
from django.core import validators
from django.forms import modelformset_factory

from . import models
from django.utils.safestring import mark_safe
from shared_models import models as shared_models


class CruiseForm(forms.ModelForm):
    class Meta:
        model = shared_models.Cruise
        exclude = ["season", ]
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            'cruise': forms.HiddenInput(),
        }


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = models.Instrument
        fields = "__all__"
        widgets = {
            'cruise': forms.HiddenInput(),
        }


class VesselForm(forms.ModelForm):
    class Meta:
        model = shared_models.Vessel
        fields = "__all__"


VesselFormset = modelformset_factory(
    model=shared_models.Vessel,
    form=VesselForm,
    extra=1,
    widgets={
        "name": forms.Textarea(attrs=dict(rows=3)),
        "nom": forms.Textarea(attrs=dict(rows=3)),
        "address": forms.Textarea(attrs=dict(rows=3)),
    }
)


class InstituteForm(forms.ModelForm):
    class Meta:
        model = shared_models.Institute
        fields = "__all__"
        widgets = {
            "name": forms.Textarea(attrs=dict(rows=3)),
            "nom": forms.Textarea(attrs=dict(rows=3)),
            "address": forms.Textarea(attrs=dict(rows=3)),
        }


InstituteFormset = modelformset_factory(
    model=shared_models.Institute,
    form=InstituteForm,
    extra=1,
)


class InstrumentComponentForm(forms.ModelForm):
    class Meta:
        model = models.InstrumentComponent
        fields = "__all__"
        widgets = {
            "instrument": forms.HiddenInput(),
            "notes": forms.Textarea(attrs=dict(rows=3)),
        }


class ComponentTypeForm(forms.ModelForm):
    class Meta:
        model = models.ComponentType
        fields = "__all__"


ComponentTypeFormset = modelformset_factory(
    model=models.ComponentType,
    form=ComponentTypeForm,
    extra=1,
)

class HelpTextForm(forms.ModelForm):
    class Meta:
        model = models.HelpText
        fields = "__all__"
        widgets = {
            'eng_text': forms.Textarea(attrs={"rows": 2}),
            'fra_text': forms.Textarea(attrs={"rows": 2}),
        }

HelpTextFormset = modelformset_factory(
    model=models.HelpText,
    form=HelpTextForm,
    extra=1,
)