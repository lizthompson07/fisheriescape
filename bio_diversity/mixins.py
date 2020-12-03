from . import models
#from shared_models import models as shared_models

from . import forms
from django.utils.translation import gettext_lazy as _


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


class OrgaMixin:
    key = 'orga'
    model = models.Organization
    form_class = forms.OrgaForm
    title = _("Organization")


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


class UnitMixin:
    key = 'unit'
    model = models.UnitCode
    form_class = forms.UnitForm
    title = _("Unit")
