from . import models
# from shared_models import models as shared_models

from . import forms
from django.utils.translation import gettext_lazy as _


class ContdcMixin:
    key = "contdc"
    form_class = forms.ContdcForm
    model = models.ContainerDetCode
    title = "Container Detail Code"


class CdscMixin:
    key = "cdsc"
    form_class = forms.CdscForm
    model = models.ContDetSubjCode
    title = "Container Detail Subject Code"


class CupMixin:
    key = "cup"
    form_class = forms.CupForm
    model = models.Cup
    title = "Cup"


class CupdMixin:
    key = "cupd"
    form_class = forms.CupdForm
    model = models.CupDet
    title = "Cup Detail"


class EvntMixin:
    key = "evnt"
    form_class = forms.EvntForm
    model = models.Event
    title = "Event"


class EvntcMixin:
    key = "evntc"
    form_class = forms.EvntcForm
    model = models.EventCode
    title = "Event Code"


class FacicMixin:
    key = "facic"
    form_class = forms.FacicForm
    model = models.FacilityCode
    title = "Facility Code"


class HeatMixin:
    key = "heat"
    form_class = forms.HeatForm
    model = models.HeathUnit
    title = "Heath Unit"


class HeatdMixin:
    key = "heatd"
    form_class = forms.HeatdForm
    model = models.HeathUnitDet
    title = "Heath Unit Detail"


class InstMixin:
    key = "inst"
    form_class = forms.InstForm
    model = models.Instrument
    title = "Instrument"


class InstcMixin:
    key = "instc"
    form_class = forms.InstcForm
    model = models.InstrumentCode
    title = "Instrument Code"


class InstdMixin:
    key = "instd"
    form_class = forms.InstdForm
    model = models.InstrumentDet
    title = "Instrument Detail"


class InstdcMixin:
    key = 'instdc'
    model = models.InstDetCode
    form_class = forms.InstdcForm
    title = _("Instrument Detail Code")


class LoccMixin:
    key = 'locc'
    model = models.LocCode
    form_class = forms.LoccForm
    title = _("Location Code")


class OrgaMixin:
    key = 'orga'
    model = models.Organization
    form_class = forms.OrgaForm
    title = _("Organization")


class PercMixin:
    key = 'perc'
    model = models.PersonnelCode
    form_class = forms.PercForm
    title = _("Personnel Code")


class ProgMixin:
    key = 'prog'
    model = models.Program
    form_class = forms.ProgForm
    title = _("Program")


class ProgaMixin:
    key = 'proga'
    model = models.ProgAuthority
    form_class = forms.ProgaForm
    title = _("Program Authority")


class ProtMixin:
    key = 'prot'
    model = models.Protocol
    form_class = forms.ProtForm
    title = _("Protocol")


class ProtcMixin:
    key = 'protc'
    model = models.ProtoCode
    form_class = forms.ProtcForm
    title = _("Protocol Code")


class ProtfMixin:
    key = 'protf'
    model = models.Protofile
    form_class = forms.ProtfForm
    title = _("Protocol File")


class RiveMixin:
    key = 'rive'
    model = models.RiverCode
    form_class = forms.RiveForm
    title = _("River Code")


class RoleMixin:
    key = 'role'
    model = models.RoleCode
    form_class = forms.RoleForm
    title = _("Role Code")


class SubrMixin:
    key = 'subr'
    model = models.SubRiverCode
    form_class = forms.SubrForm
    title = _("Sub river Code")


class TankMixin:
    key = 'tank'
    model = models.Tank
    form_class = forms.TankForm
    title = _("Tank")


class TankdMixin:
    key = 'tankd'
    model = models.TankDet
    form_class = forms.TankdForm
    title = _("Tank Detail")


class TeamMixin:
    key = 'team'
    model = models.Team
    form_class = forms.TeamForm
    title = _("Team")


class TrayMixin:
    key = 'tray'
    model = models.Tray
    form_class = forms.TrayForm
    title = _("Tray")


class TraydMixin:
    key = 'trayd'
    model = models.TrayDet
    form_class = forms.TraydForm
    title = _("Tray Detail")


class TribMixin:
    key = 'trib'
    model = models.Tributary
    form_class = forms.TribForm
    title = _("Tributary")


class TrofMixin:
    key = 'trof'
    model = models.Trough
    form_class = forms.TrofForm
    title = _("Trough")


class TrofdMixin:
    key = 'trofd'
    model = models.TroughDet
    form_class = forms.TrofdForm
    title = _("Trough Detail")


class UnitMixin:
    key = 'unit'
    model = models.UnitCode
    form_class = forms.UnitForm
    title = _("Unit")
