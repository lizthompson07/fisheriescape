from django import forms
from bio_diversity import models


class CreatePrams:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields['created_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                    "class": "fp-date"})


class InstForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Instrument
        exclude = []


class InstcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.InstrumentCode
        exclude = []


class InstdForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.InstrumentDet
        exclude = []
        widgets = {
            'start_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"}),
            'end_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"}),
        }


class InstdcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.InstDetCode
        exclude = []


class OrgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Organization
        exclude = []


class ProgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ProgAuthority
        exclude = []


class ProtcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ProtoCode
        exclude = []


class ProtfForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Protofile
        exclude = []
        # widgets = {
        #     'prot_file': forms.FilePathField(path='.'),
        # }
