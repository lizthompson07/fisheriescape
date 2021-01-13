from datetime import date

from django import forms
from django.db import IntegrityError
from django.utils.translation import gettext

from bio_diversity import models


class CreatePrams:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        # forms.DateInput(attrs={"placeholder": "Click to select a date..",
        #                       "class": "fp-date"})


class CreateTimePrams:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        # forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        self.fields['start_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                  "class": "fp-date"})
        self.fields['end_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                "class": "fp-date"})

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        # 2) valid is false if today is after end_date
        end_date = cleaned_data.get("end_date")
        valid = cleaned_data.get("det_valid")
        if end_date:
            start_date = cleaned_data.get("start_date")
            today = date.today()
            if end_date and start_date and end_date < start_date:
                self.add_error('end_date', gettext(
                    "The end date must be after the start date!"
                ))
            elif end_date and valid and end_date < today:
                self.add_error('det_valid', gettext("Cannot be valid after end date"))


class AnidcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.AnimalDetCode
        exclude = []


class AnixForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.AniDetailXref
        exclude = []


class AdscForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.AniDetSubjCode
        exclude = []


class CntForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Count
        exclude = []


class CntcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.CountCode
        exclude = []


class CntdForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.CountDet
        exclude = []


class CollForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Collection
        exclude = []


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


class EnvForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvCondition
        exclude = []
        widgets = {
            'env_start': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                    "class": "fp-date-time"}),
            'env_end': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date-time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        end_date = cleaned_data.get("env_end")
        if end_date:
            start_date = cleaned_data.get("env_start")
            if end_date and start_date and end_date < start_date:
                self.add_error('env_end', gettext(
                    "The end date must be after the start date!"
                ))


class EnvcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvCode
        exclude = []


class EnvcfForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvCondFile
        exclude = []


class EnvscForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvSubjCode
        exclude = []


class EnvtForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvTreatment
        exclude = []


class EnvtcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EnvTreatCode
        exclude = []


class EvntForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = []
        widgets = {
            'evnt_start': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                     "class": "fp-date-time"}),
            'evnt_end': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                   "class": "fp-date-time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team_id'].create_url = 'bio_diversity:create_team'

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date
        end_date = cleaned_data.get("evnt_end")
        if end_date:
            start_date = cleaned_data.get("evnt_start")
            if end_date and start_date and end_date < start_date:
                self.add_error('evnt_end', gettext(
                    "The end date must be after the start date!"
                ))


class EvntcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.EventCode
        exclude = []


class FacicForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.FacilityCode
        exclude = []


class FecuForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.Fecundity
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


class GrpForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = []


class GrpdForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.GroupDet
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


class ImgForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Image
        exclude = []


class ImgcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.ImageCode
        exclude = []


class IndvForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Individual
        exclude = []

    field_order = [
        'ufid',
        'pit_tag',
        'indv_valid',
        'grp_id',
        'spec_id',
        'stok_id',
        'coll_id',
        'comments',
    ]


class IndvdForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.IndividualDet
        exclude = []


class IndvtForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.IndTreatment
        exclude = []
        widgets = {
            'start_datetime': forms.DateInput(attrs={"placeholder": "Click to select a date...",
                                                     "class": "fp-date-time"}),
            'end_datetime': forms.DateInput(attrs={"placeholder": "Click to select a date...",
                                                   "class": "fp-date-time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        end_date = cleaned_data.get("end_datetime")
        if end_date:
            start_date = cleaned_data.get("start_datetime")
            if end_date and start_date and end_date < start_date:
                self.add_error('end_datetime', gettext(
                    "The end date must be after the start date!"
                ))


class IndvtcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.IndTreatCode
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
        }


class LoccForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.LocCode
        exclude = []


class OrgaForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Organization
        exclude = []


class PairForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.Pairing
        exclude = []
        widgets = {
            "indv_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class PercForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.PersonnelCode
        exclude = []


class PrioForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.PriorityCode
        exclude = []


class ProgForm(CreateTimePrams, forms.ModelForm):
    class Meta:
        model = models.Program
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['proga_id'].create_url = 'bio_diversity:create_proga'
        self.fields['orga_id'].create_url = 'bio_diversity:create_orga'


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


class QualForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.QualCode
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


class SampForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = []


class SampcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SampleCode
        exclude = []


class SampdForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SampleDet
        exclude = []


class SireForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Sire
        exclude = []
        widgets = {
            "indv_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class SpwnForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.Spawning
        exclude = []
        widgets = {
            'spwn_date': forms.DateInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pair_id'].create_url = 'bio_diversity:create_pair'


class SpwndForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SpawnDet
        exclude = []


class SpwndcForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SpawnDetCode
        exclude = []


class SpwnscForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SpawnDetSubjCode
        exclude = []


class SpecForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.SpeciesCode
        exclude = []


class StokForm(CreatePrams, forms.ModelForm):
    class Meta:
        model = models.StockCode
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
