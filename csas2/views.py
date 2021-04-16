from django.contrib import messages
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy

from lib.templatetags.custom_filters import nz
from shared_models.views import CommonTemplateView, CommonFormView, CommonDeleteView, CommonDetailView, \
    CommonCreateView, CommonUpdateView, CommonFilterView
from . import models, forms, filters
from .mixins import LoginAccessRequiredMixin, CsasAdminRequiredMixin, CanModifyRequestRequiredMixin
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
    paginate_by = 25
    home_url_name = "csas2:index"
    new_object_url = reverse_lazy("csas2:request_new")
    row_object_url_name = row_ = "csas2:request_detail"
    container_class = "container-fluid"

    field_list = [
        {"name": 'id|{}'.format("request id"), "class": "", "width": ""},
        {"name": 'tname|{}'.format("title"), "class": "", "width": ""},
        {"name": 'fiscal_year', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.CSASRequest.objects.annotate(
            search_term=Concat('name', Value(" "), 'nom', output_field=TextField()))


class CSASRequestDetailView(LoginAccessRequiredMixin, CommonDetailView):
    model = models.CSASRequest
    template_name = 'csas2/request_detail.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("csas2:request_list")}
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


class CSASRequestCreateView(LoginAccessRequiredMixin, CommonCreateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    success_url = reverse_lazy('csas2:request_list')
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    parent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("csas2:request_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class CSASRequestUpdateView(CanModifyRequestRequiredMixin, CommonUpdateView):
    model = models.CSASRequest
    form_class = forms.CSASRequestForm
    template_name = 'csas2/request_form.html'
    home_url_name = "csas2:index"
    grandparent_crumb = {"title": gettext_lazy("CSASRequest"), "url": reverse_lazy("csas2:request_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("csas2:request_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class CSASRequestDeleteView(CanModifyRequestRequiredMixin, CommonDeleteView):
    model = models.CSASRequest
    success_url = reverse_lazy('csas2:request_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'csas2/confirm_delete.html'


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
