from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy, gettext as _

from scuba.mixins import LoginAccessRequiredMixin, ScubaAdminRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDeleteView, CommonDetailView
from . import models, forms, filters


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'scuba/index.html'


# REFERENCE TABLES #
####################

class DiverFormsetView(ScubaAdminRequiredMixin, CommonFormsetView):
    template_name = 'scuba/formset.html'
    h1 = "Manage Divers"
    queryset = models.Diver.objects.all()
    formset_class = forms.DiverFormset
    success_url_name = "scuba:manage_divers"
    home_url_name = "scuba:index"
    delete_url_name = "scuba:delete_diver"


class DiverHardDeleteView(ScubaAdminRequiredMixin, CommonHardDeleteView):
    model = models.Diver
    success_url = reverse_lazy("scuba:manage_divers")


# REGIONS #
###########

class RegionListView(ScubaAdminRequiredMixin, CommonFilterView):
    template_name = 'scuba/list.html'
    filterset_class = filters.RegionFilter
    home_url_name = "scuba:index"
    new_object_url = reverse_lazy("scuba:region_new")
    row_object_url_name = row_ = "scuba:region_detail"
    container_class = "container-fluid bg-light curvy"

    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'tdescription|{}'.format("description"), "class": "", "width": ""},
        {"name": 'province', "class": "", "width": ""},
    ]

    def get_queryset(self):
        return models.Region.objects.annotate(
            search_term=Concat('name', Value(" "), 'abbreviation', output_field=TextField()))


class RegionUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Region
    form_class = forms.RegionForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"


class RegionCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Region
    form_class = forms.RegionForm
    success_url = reverse_lazy('scuba:region_list')
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"


class RegionDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Region
    template_name = 'scuba/region_detail.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"
    field_list = [
        'name',
        'tdescription|{}'.format("description"),
        'province',
        'samples|{}'.format(_("sample count")),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_field_list = [
            'name',
            'abbreviation',
            'tdescription|{}'.format("description"),
            'latitude',
            'longitude',
        ]
        context["site_field_list"] = site_field_list
        return context


class RegionDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Region
    success_url = reverse_lazy('scuba:region_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"


# SITES #
#########


class SiteCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Site
    form_class = forms.SiteForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    container_class = "container bg-light curvy"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_region(self):
        return get_object_or_404(models.Region, pk=self.kwargs.get("region"))

    def get_parent_crumb(self):
        return {"title": self.get_region(), "url": reverse("scuba:region_detail", args=[self.get_region().id])}

    def get_success_url(self):
        return self.get_parent_crumb()["url"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.region = self.get_region()
        return super().form_valid(form)


class SiteUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Site
    form_class = forms.SiteForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"


class SiteDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Site
    success_url = reverse_lazy('scuba:region_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"
