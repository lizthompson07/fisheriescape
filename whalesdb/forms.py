from django import forms
from whalesdb import models

import shared_models.models as shared_models


class CruForm(forms.ModelForm):
    class Meta:
        model = shared_models.Cruise
        fields = ["mission_number",
                  "description",
                  "chief_scientist",
                  "samplers",
                  "start_date",
                  "end_date",
                  "notes",
                  "season",
                  "vessel", ]


class DepForm(forms.ModelForm):
    min_height = 900
    min_width = 600

    class Meta:
        model = models.DepDeployment
        fields = ["stn", "dep_year", "dep_month", "dep_name", "prj", "mor"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['stn'].create_url = 'whalesdb:create_stn'
        self.fields['prj'].create_url = 'whalesdb:create_prj'
        self.fields['mor'].create_url = 'whalesdb:create_mor'


class EcaForm(forms.ModelForm):

    class Meta:
        model = models.EcaCalibrationEvent
        exclude = []
        widgets = {
            'eca_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class EccForm(forms.ModelForm):
    class Meta:
        model = models.EccCalibrationValue
        exclude = []
        widgets = {
        }


class EdaForm(forms.ModelForm):

    class Meta:
        model = models.EdaEquipmentAttachment
        exclude = []
        widgets = {
            'dep': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove equipment that is already attached to a given deployment
        remove = []
        if 'initial' in kwargs and 'dep' in kwargs['initial'] and \
                models.DepDeployment.objects.filter(pk=kwargs['initial']['dep']).count() > 0:
            remove = [eda.eqp.pk for eda in
                       models.DepDeployment.objects.get(pk=kwargs['initial']['dep']).attachments.all()]

        # exclude hydrophones from the equipment selection list
        self.fields['eqp'].queryset = self.fields['eqp'].queryset.exclude(emm__eqt=4).exclude(pk__in=remove)


class EmmForm(forms.ModelForm):
    min_height = 700
    min_width = 600

    class Meta:
        model = models.EmmMakeModel
        exclude = []
        widgets = {
        }


class EheForm(forms.ModelForm):
    class Meta:
        model = models.EheHydrophoneEvent
        exclude = []
        widgets = {
        }


class EqhForm(forms.ModelForm):
    class Meta:
        model = models.EqhHydrophoneProperty
        exclude = []
        widgets = {
            'emm': forms.HiddenInput()
        }


class EqoForm(forms.ModelForm):
    class Meta:
        model = models.EqoOwner
        exclude = []
        widgets = {
        }


class EqpForm(forms.ModelForm):
    min_height = 850
    min_width = 600

    class Meta:
        model = models.EqpEquipment
        exclude = []
        widgets = {
            'eqp_date_purchase': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['emm'].create_url = 'whalesdb:create_emm'
        self.fields['eqo_owned_by'].create_url = 'whalesdb:create_eqo'


class EqrForm(forms.ModelForm):
    class Meta:
        model = models.EqrRecorderProperties
        exclude = []
        widgets = {
            'emm': forms.HiddenInput()
        }


class EtrForm(forms.ModelForm):
    class Meta:
        model = models.EtrTechnicalRepairEvent
        exclude = []
        widgets = {
            'etr_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"}),
        }


class MorForm(forms.ModelForm):

    min_height = 935
    min_width = 600

    class Meta:
        model = models.MorMooringSetup
        exclude = []
        widgets = {
            'mor_additional_equipment': forms.Textarea(attrs={"rows": 2}),
            'mor_general_moor_description': forms.Textarea(attrs={"rows": 2}),
            'mor_notes': forms.Textarea(attrs={"rows": 2}),
        }


class PrjForm(forms.ModelForm):

    class Meta:
        model = models.PrjProject
        fields = ["name", "nom", "description_en", "description_fr", "prj_url"]
        widgets = {
            'description_en': forms.Textarea(attrs={"rows": 2}),
            'description_fr': forms.Textarea(attrs={"rows": 2}),
        }


class RciForm(forms.ModelForm):
    min_height = 1000
    min_width = 600

    class Meta:
        model = models.RciChannelInfo
        exclude = []
        widgets = {
            'rec_id': forms.HiddenInput(),
        }


class RecForm(forms.ModelForm):
    class Meta:
        model = models.RecDataset
        exclude = []
        widgets = {
            'rec_start_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"}),
            'rec_end_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class ReeForm(forms.ModelForm):
    min_height = 1000
    min_width = 600

    class Meta:
        model = models.ReeRecordingEvent
        exclude = []
        widgets = {
            'rec_id': forms.HiddenInput(),
            'ree_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class RetForm(forms.ModelForm):
    class Meta:
        model = models.RetRecordingEventType
        exclude = []


class RscForm(forms.ModelForm):
    class Meta:
        model = models.RscRecordingSchedule
        exclude = []
        widgets = {
        }


class RstForm(forms.ModelForm):
    class Meta:
        model = models.RstRecordingStage
        exclude = []
        widgets = {
            'rsc': forms.HiddenInput()
        }


class RttForm(forms.ModelForm):
    class Meta:
        model = models.RttTimezoneCode
        exclude = []


class StnForm(forms.ModelForm):
    min_height = 935
    min_width = 600

    class Meta:
        model = models.StnStation
        exclude = []
        widgets = {
            'stn_notes': forms.Textarea(attrs={"rows": 2}),
        }


class SteForm(forms.ModelForm):
    min_height = 935
    min_width = 600

    class Meta:
        model = models.SteStationEvent
        exclude = []
        widgets = {
            'ste_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"}),
            'dep': forms.HiddenInput(),
            'set_type': forms.HiddenInput(),
        }


class TeaForm(forms.ModelForm):
    class Meta:
        model = models.TeaTeamMember
        exclude = []
        widgets = {
        }
