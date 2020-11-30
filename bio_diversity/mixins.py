from . import models
from shared_models import models as shared_models

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


