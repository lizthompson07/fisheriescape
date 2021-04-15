import csv
from io import StringIO
import datetime as dt
import requests
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.templatetags.custom_filters import nz
from shared_models.views import CommonTemplateView, CommonHardDeleteView, CommonFormsetView, CommonFormView, CommonDeleteView, CommonDetailView, \
    CommonCreateView, CommonUpdateView, CommonFilterView, CommonPopoutCreateView, CommonPopoutUpdateView, CommonPopoutDeleteView
from . import models, forms, filters, utils
from .mixins import LoginAccessRequiredMixin, CsasAdminRequiredMixin
from .utils import in_csas_admin_group


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'csas2/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_csas_admin_group(self.request.user)
        return context



# csas requests # 
#################

class CSASRequestListView(LoginAccessRequiredMixin, CommonFilterView):
    template_name = 'csas2/list.html'
    filterset_class = filters.CSASRequestFilter
    home_url_name = "grais:index"
    new_object_url = reverse_lazy("grais:species_new")
    row_object_url_name = row_ = "grais:species_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'tname|{}'.format("common name"), "class": "", "width": ""},
        {"name": 'formatted_scientific|{}'.format("scientific name"), "class": "", "width": ""},
        {"name": 'abbrev', "class": "", "width": ""},
        {"name": 'tsn|ITIS TSN', "class": "", "width": ""},
        {"name": 'aphia_id|WoRMS Aphia ID', "class": "", "width": ""},
        {"name": 'color_morph', "class": "", "width": ""},
        {"name": 'invasive', "class": "", "width": ""},
        {"name": 'green_crab_monitoring|green crab monitoring?', "class": "", "width": ""},
        {"name": 'Has occurred in db?', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.CSASRequest.objects.annotate(
            search_term=Concat('common_name', Value(" "), 'common_name_fra', Value(" "), 'scientific_name', output_field=TextField()))


class CSASRequestUpdateView(GraisAdminRequiredMixin, CommonUpdateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("grais:species_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:species_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class CSASRequestCreateView(GraisCRUDRequiredMixin, CommonCreateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    success_url = reverse_lazy('grais:species_list')
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("grais:species_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class CSASRequestDetailView(GraisAccessRequiredMixin, CommonDetailView):
    model = models.CSASRequest
    template_name = 'grais/biofouling/species_detail.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("grais:species_list")}
    field_list = [
        'id',
        'common_name',
        'common_name_fra',
        'scientific_name',
        'abbrev',
        'tsn',
        'aphia',
        'epibiont_type',
        'color_morph',
        'invasive',
        'green_crab_monitoring',
        'database occurrences',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CSASRequestDeleteView(GraisAdminRequiredMixin, CommonDeleteView):
    model = models.CSASRequest
    success_url = reverse_lazy('grais:species_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'grais/confirm_delete.html'






# REPORTS #
###########

class ReportSearchFormView(CsasAdminRequiredMixin, CommonFormView):
    template_name = 'csas2/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("eDNA Reports")

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = nz(form.cleaned_data["year"], "None")
        messages.error(self.request, "Report is not available. Please select another report.")
        return HttpResponseRedirect(reverse("csas2:reports"))

