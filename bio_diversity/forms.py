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


class ContxForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ContainerXRef
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


class DrawForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Drawer
        exclude = []


class EvntForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = []
        widgets = {
            'evnt_start': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date-time"}),
            'evnt_starttime': forms.TimeInput(attrs={"class": "fp-date-time"}),
            'evnt_end': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date-time"}),
            'evnt_endtime': forms.TimeInput(attrs={"class": "fp-time"}),
        }


class EvntcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EventCode
        exclude = []


class FacicForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.FacilityCode
        exclude = []


class FeedForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Feeding
        exclude = []


class FeedcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.FeedCode
        exclude = []


class FeedmForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.FeedMethod
        exclude = []


class HeatForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.HeathUnit
        exclude = []
        widgets = {
            'inservice_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
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


class LocForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Location
        exclude = []
        widgets = {
            'loc_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date-time"}),
            'loc_time': forms.TimeInput(attrs={"class": "fp-time"}),
        }


class LoccForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.LocCode
        exclude = []


class OrgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Organization
        exclude = []


class PercForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.PersonnelCode
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


class RelcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ReleaseSiteCode
        exclude = []


class RiveForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.RiverCode
        exclude = []


class RoleForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.RoleCode
        exclude = []


class SubrForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SubRiverCode
        exclude = []


class TankForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Tank
        exclude = []


class TankdForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.TankDet
        exclude = []


class TeamForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Team
        exclude = []


class TrayForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Tray
        exclude = []


class TraydForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.TrayDet
        exclude = []


class TribForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Tributary
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
