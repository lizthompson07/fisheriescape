from . import models
from shared_models import models as shared_models

from . import forms
from django.utils.translation import gettext_lazy as _


class CruMixin:
    key = 'cru'
    model = shared_models.Cruise
    form_class = forms.CruForm
    title = _("Cruise")


class DepMixin:
    key = 'dep'
    model = models.DepDeployment
    form_class = forms.DepForm
    title = _("Deployment")


class EcaMixin(object):
    key = 'eca'
    model = models.EcaCalibrationEvent
    form_class = forms.EcaForm
    title = _("Calibration Event")


class EccMixin(object):
    key = 'ecc'
    model = models.EccCalibrationValue
    form_class = forms.EccForm
    title = _("Calibration Values")


class EdaMixin:
    key = 'eda'
    model = models.EdaEquipmentAttachment
    form_class = forms.EdaForm
    title = _("Equipment Attachment")


class EmmMixin:
    key = 'emm'
    model = models.EmmMakeModel
    form_class = forms.EmmForm
    title = _("Make/Model")


class EqhMixin:
    key = 'eqh'
    model = models.EqhHydrophoneProperty
    form_class = forms.EqhForm
    title = _("Hydrophone Properties")


class EqoMixin:
    key = 'eqo'
    model = models.EqoOwner
    form_class = forms.EqoForm
    title = _("Equipment Owner")


class EqpMixin:
    key = 'eqp'
    model = models.EqpEquipment
    form_class = forms.EqpForm
    title = _("Equipment")


class EqrMixin:
    key = 'eqr'
    model = models.EqrRecorderProperties
    form_class = forms.EqrForm
    title = _("Recorder Properties")


class EtrMixin:
    key = 'etr'
    model = models.EtrTechnicalRepairEvent
    form_class = forms.EtrForm
    title = _("Technical Repair Event")


class MorMixin:
    key = 'mor'
    model = models.MorMooringSetup
    form_class = forms.MorForm
    title = _("Mooring Setup")


class PrjMixin:
    key = 'prj'
    model = models.PrjProject
    form_class = forms.PrjForm
    title = _("Project")


class RciMixin(object):
    key = 'rci'
    model = models.RciChannelInfo
    form_class = forms.RciForm
    title = _("Channel Information")


class RecMixin(object):
    key = 'rec'
    model = models.RecDataset
    form_class = forms.RecForm
    title = _("Dataset")


class ReeMixin(object):
    key = 'ree'
    model = models.ReeRecordingEvent
    form_class = forms.ReeForm
    title = _("Recording Events")


class RetMixin(object):
    key = 'ret'
    model = models.RetRecordingEventType
    form_class = forms.RetForm
    title = _("Recording Event Type")


class RscMixin(object):
    key = 'rsc'
    model = models.RscRecordingSchedule
    form_class = forms.RscForm
    title = _("Recording Schedule")


class RstMixin(object):
    key = 'rst'
    model = models.RstRecordingStage
    form_class = forms.RstForm
    title = _("Recording Stage")


class RttMixin(object):
    key = 'rtt'
    model = models.RttTimezoneCode
    form_class = forms.RttForm
    title = _("Time Zone")


class SteMixin(object):
    key = 'ste'
    model = models.SteStationEvent
    form_class = forms.SteForm
    title = _("Station Event")


class StnMixin(object):
    key = 'stn'
    model = models.StnStation
    form_class = forms.StnForm
    title = _("Station")


class TeaMixin(object):
    key = 'tea'
    model = models.TeaTeamMember
    form_class = forms.TeaForm
    title = _("Team Member")
