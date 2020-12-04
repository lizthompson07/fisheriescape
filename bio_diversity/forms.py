from django import forms
from bio_diversity import models


class CreatePrams:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields['created_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                    "class": "fp-date"})


class CreateTimePrams:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields['created_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                    "class": "fp-date"})
        self.fields['start_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                  "class": "fp-date"})
        self.fields['end_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                "class": "fp-date"})


class ContdcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ContainerDetCode
        exclude = []


class CdscForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ContDetSubjCode
        exclude = []


class CupForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Cup
        exclude = []


class CupdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.CupDet
        exclude = []


class HeatForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.HeathUnit
        exclude = []
        widgets = {
            'inservice_date' : forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class HeatdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.HeathUnitDet
        exclude = []


class InstForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Instrument
        exclude = []


class InstcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.InstrumentCode
        exclude = []


class InstdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.InstrumentDet
        exclude = []


class InstdcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.InstDetCode
        exclude = []


class OrgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Organization
        exclude = []


class ProgForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.Program
        exclude = []


class ProgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ProgAuthority
        exclude = []


class ProtForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.Protocol
        exclude = []


class ProtcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ProtoCode
        exclude = []


class ProtfForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Protofile
        exclude = []


class TankForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Tank
        exclude = []


class TankdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.TankDet
        exclude = []


class TrayForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Tray
        exclude = []


class TraydForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.TrayDet
        exclude = []


class TrofForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Trough
        exclude = []


class TrofdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.TroughDet
        exclude = []


class UnitForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.UnitCode
        exclude = []
