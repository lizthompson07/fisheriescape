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
    post_display_fields = ["dive_count"]


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


class SiteDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Site
    template_name = 'scuba/site_detail.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"
    field_list = [
        'name',
        'abbreviation',
        'tdescription|{}'.format("description"),
        'latitude',
        'longitude',
    ]

    def get_parent_crumb(self):
        return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transect_field_list = [
            'name',
        ]
        context["transect_field_list"] = transect_field_list
        return context


class SiteUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Site
    form_class = forms.SiteForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:site_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}


class SiteDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Site
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:site_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}


# TRANSECTS #
#############


class TransectCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Transect
    form_class = forms.TransectForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    container_class = "container bg-light curvy"
    greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_site(self):
        site = get_object_or_404(models.Site, pk=self.kwargs["site"])
        return site

    def get_parent_crumb(self):
        return {"title": self.get_site(), "url": reverse("scuba:site_detail", args=[self.get_site().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_site().region, "url": reverse("scuba:region_detail", args=[self.get_site().region.id])}

    def get_success_url(self):
        return self.get_parent_crumb()["url"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.site = self.get_site()
        return super().form_valid(form)


class TransectDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Transect
    template_name = 'scuba/site_detail.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container bg-light curvy"

    def get_site(self):
        site = get_object_or_404(models.Site, pk=self.kwargs["site"])
        return site

    def get_parent_crumb(self):
        return {"title": self.get_site(), "url": reverse_lazy("scuba:site_detail", args=[self.get_site().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_field_list = [
            'name',
        ]
        context["site_field_list"] = site_field_list
        return context


class TransectUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Transect
    form_class = forms.TransectForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    container_class = "container bg-light curvy"
    greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().site, "url": reverse("scuba:site_detail", args=[self.get_object().site.id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().site.region, "url": reverse("scuba:region_detail", args=[self.get_object().site.region.id])}


class TransectDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Transect
    success_url = reverse_lazy('scuba:region_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"
    greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().site, "url": reverse("scuba:site_detail", args=[self.get_object().site.id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().site.region, "url": reverse("scuba:region_detail", args=[self.get_object().site.region.id])}


# SAMPLES #
###########

class SampleListView(ScubaAdminRequiredMixin, CommonFilterView):
    model = models.Sample
    template_name = 'scuba/list.html'
    filterset_class = filters.SampleFilter
    home_url_name = "scuba:index"
    row_object_url_name = "scuba:sample_detail"
    new_object_url = reverse_lazy("scuba:sample_new")
    new_btn_text = gettext_lazy("Add a New Sample")
    container_class = "container-fluid bg-light curvy"
    field_list = [
        {"name": 'datetime|{}'.format("date"), "class": "", "width": ""},
        {"name": 'site.region|{}'.format("region"), "class": "", "width": ""},
        {"name": 'site', "class": "", "width": ""},
        {"name": 'dive_count|{}'.format(_("dive count")), "class": "", "width": ""},
    ]


class SampleUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container bg-light curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("scuba:sample_detail", args=[self.get_object().id])}


class SampleCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Sample
    form_class = forms.SampleForm
    success_url = reverse_lazy('scuba:sample_list')
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container bg-light curvy"


class SampleDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Sample
    template_name = 'scuba/sample_detail.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container bg-light curvy"
    field_list = [
        'site_region|{}'.format(gettext_lazy("site")),
        'datetime',
        'weather_notes',
        'comment',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dive_field_list = [
            'transect',
            'diver',
            'heading',
            'side',
            'width_m',
            'comment',
            'observation_count|{}'.format(_("lobster count")),
        ]
        context["dive_field_list"] = dive_field_list
        return context


class SampleDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Sample
    success_url = reverse_lazy('scuba:sample_list')
    home_url_name = "scuba:index"
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"
    grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("scuba:sample_detail", args=[self.get_object().id])}


# DIVES #
#########

class DiveCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Dive
    form_class = forms.DiveForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    container_class = "container bg-light curvy"
    grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}

    def get_initial(self):
        sample = self.get_sample()
        return dict(
            sample=sample.id,
            start_descent=sample.datetime,
            start_final_ascent=sample.datetime,
            reach_surface=sample.datetime,
        )

    def get_sample(self):
        return get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))

    def get_parent_crumb(self):
        return {"title": self.get_sample(), "url": reverse("scuba:sample_detail", args=[self.get_sample().id])}

    def get_success_url(self):
        return self.get_parent_crumb()["url"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        sample = self.get_sample()
        obj.sample = sample
        return super().form_valid(form)


class DiveUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Dive
    form_class = forms.DiveForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container bg-light curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:dive_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("scuba:sample_detail", args=[self.get_object().sample.id])}


class DiveDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Dive
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container bg-light curvy"
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:dive_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("scuba:sample_detail", args=[self.get_object().sample.id])}


class DiveDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Dive
    template_name = 'scuba/dive_detail.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container bg-light curvy"
    field_list = [
        'transect',
        'diver',
        'start_descent',
        'bottom_time',
        'max_depth_ft',
        'psi_in',
        'psi_out',
        'heading',
        'side',
        'width_m',
        'comment',
    ]

    def get_parent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse("scuba:sample_detail", args=[self.get_object().sample.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_field_list = [
            'interval',
            'depth_ft',
            'substrate_profile|{}'.format(_("substrate profile")),
            'comment',
        ]
        context["section_field_list"] = section_field_list
        observation_field_list = [
            'id|{}'.format(_("lobster id")),
            'sex',
            'egg_status',
            'carapace_length_mm',
            'certainty_rating',
            'comment',
        ]
        context["observation_field_list"] = observation_field_list
        context["random_observation"] = models.Observation.objects.first()
        return context


class DiveDataEntryTemplateView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Dive
    template_name = 'scuba/dive_data_entry/main.html'
    container_class = "container bg-light-green curvy"
    field_list = [
        'id|{}'.format(_("dive Id")),
        'transect',
        'diver',
        'heading',
        'side',
        'width_m',
        'comment',
    ]

    def get_h1(self):
        return _("Data Entry Mode")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_field_list = [
            'interval',
            'depth_ft',
            'substrate_profile|{}'.format(_("substrate profile")),
            'observation_count|{}'.format(_("observation count")),
            'comment',
        ]
        context["section_field_list"] = section_field_list
        observation_field_list = [
            'sex',
            'egg_status',
            'carapace_length_mm',
            'certainty_rating',
            'comment',
            # 'id|{}'.format(_("observation ID")),
        ]
        context["observation_field_list"] = observation_field_list
        context["random_observation"] = models.Observation.objects.first()
        context["section_form"] = forms.SectionForm
        return context
