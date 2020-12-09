from . import models
# from shared_models import models as shared_models

from . import forms
from django.utils.translation import gettext_lazy as _


class AnidcMixin:
    key = "anidc"
    form_class = forms.AnidcForm
    model = models.AnimalDetCode
    title = "Animal Detail Code"


class AdscMixin:
    key = "adsc"
    form_class = forms.AdscForm
    model = models.AniDetSubjCode
    title = "Animal Detail Subject Code"


class CntMixin:
    key = "cnt"
    form_class = forms.CntForm
    model = models.Count
    title = "Count"


class CntcMixin:
    key = "cntc"
    form_class = forms.CntcForm
    model = models.CountCode
    title = "Count Code"


class CntdMixin:
    key = "cntd"
    form_class = forms.CntdForm
    model = models.CountDet
    title = "Count Detail"


class CollMixin:
    key = "coll"
    form_class = forms.CollForm
    model = models.Collection
    title = "Collection"


class ContdcMixin:
    key = "contdc"
    form_class = forms.ContdcForm
    model = models.ContainerDetCode
    title = "Container Detail Code"


class ContxMixin:
    key = "contx"
    form_class = forms.ContxForm
    model = models.ContainerXRef
    title = "Container Cross Reference"


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


class DrawMixin:
    key = "draw"
    form_class = forms.DrawForm
    model = models.Drawer
    title = "Drawer"


class EnvcMixin:
    key = "envc"
    form_class = forms.EnvcForm
    model = models.EnvCode
    title = "Environment Code"


class EnvMixin:
    key = "env"
    form_class = forms.EnvForm
    model = models.EnvCondition
    title = "Environment Condition"


class EnvscMixin:
    key = "envsc"
    form_class = forms.EnvscForm
    model = models.EnvSubjCode
    title = "Event Subject Code"


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


class FeedMixin:
    key = "feed"
    form_class = forms.FeedForm
    model = models.Feeding
    title = "Feeding"


class FeedcMixin:
    key = "feedc"
    form_class = forms.FeedcForm
    model = models.FeedCode
    title = "Feeding Code"


class FeedmMixin:
    key = "feedm"
    form_class = forms.FeedmForm
    model = models.FeedMethod
    title = "Feeding Method"


class GrpMixin:
    key = "grp"
    form_class = forms.GrpForm
    model = models.Group
    title = "Group"


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


class IndvMixin:
    key = "indv"
    form_class = forms.IndvForm
    model = models.Individual
    title = "Individual"


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


class LocMixin:
    key = 'loc'
    model = models.Location
    form_class = forms.LocForm
    title = _("Location")


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


class PrioMixin:
    key = 'prio'
    model = models.PriorityCode
    form_class = forms.PrioForm
    title = _("Priority Code")


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


class QualMixin:
    key = 'qual'
    model = models.QualCode
    form_class = forms.QualForm
    title = _("Quality Code")


class RelcMixin:
    key = 'relc'
    model = models.ReleaseSiteCode
    form_class = forms.RelcForm
    title = _("Release Site Code")


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


class SampMixin:
    key = 'samp'
    model = models.Sample
    form_class = forms.SampForm
    title = _("Sample ")


class SampcMixin:
    key = 'sampc'
    model = models.SampleCode
    form_class = forms.SampcForm
    title = _("Sample Code")


class SampdMixin:
    key = 'sampd'
    model = models.SampleDet
    form_class = forms.SampdForm
    title = _("Sample Detail")


class SpecMixin:
    key = 'spec'
    model = models.SpeciesCode
    form_class = forms.SpecForm
    title = _("Species Code")


class StokMixin:
    key = 'stok'
    model = models.StockCode
    form_class = forms.StokForm
    title = _("Stock Code")


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
