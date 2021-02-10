from . import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class AptMixin:
    key = 'apt'
    model = models.AptAdvisoryProcessType
    title = _("Advisory Process Type")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_apt")


class CohMixin:
    key = 'coh'
    model = models.CohHonorific
    title = _("Honorific")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_coh")


class LocMixin:
    key = 'loc'
    model = models.LocLocationProv
    title = _("Meeting Location Province")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_loc")


class MeqMixin:
    key = 'meq'
    model = models.MeqQuarter
    title = _("Meeting Quarter")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_meq")


class ScpMixin:
    key = 'scp'
    model = models.ScpScope
    title = _("Scope")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_scp")


class SttMixin:
    key = 'stt'
    model = models.SttStatus
    title = _("Meeting Status")
    fields = ['name', 'nom', 'description_en', 'description_fr']
    success_url = reverse_lazy("csas:list_stt")

