from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy

from grais import filters
from grais import forms
from grais import models
from grais.mixins import GraisAccessRequiredMixin, GraisAdminRequiredMixin, GraisCRUDRequiredMixin
from shared_models.views import CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDetailView, CommonDeleteView, CommonPopoutUpdateView, CommonPopoutCreateView, CommonPopoutDeleteView, CommonFormsetView, CommonHardDeleteView


# Estuary #
###########

class EstuaryListView(GraisAccessRequiredMixin, CommonFilterView):
    model = models.Estuary
    template_name = 'grais/list.html'
    filterset_class = filters.EstuaryFilter
    home_url_name = "grais:index"
    new_object_url = reverse_lazy("grais:estuary_new")
    row_object_url_name = row_ = "grais:estuary_detail"
    h1 = "Estuaries"

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'name|{}'.format("common name"), "class": "", "width": ""},
        {"name": 'province.abbrev_eng|{}'.format("province"), "class": "", "width": ""},
        {"name": 'site_count|sample count', "class": "", "width": ""},
    ]


class EstuaryUpdateView(GraisCRUDRequiredMixin, CommonUpdateView):
    model = models.Estuary
    form_class = forms.EstuaryForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:estuary_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class EstuaryCreateView(GraisCRUDRequiredMixin, CommonCreateView):
    model = models.Estuary
    form_class = forms.EstuaryForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class EstuaryDetailView(GraisAccessRequiredMixin, CommonDetailView):
    model = models.Estuary
    template_name = 'grais/green_crab/estuary_detail.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}
    field_list = [
        'id',
        'name',
        'latitude',
        'longitude',
        'description',
        'metadata',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_field_list"] = [
            'code',
            'name',
            'description',
        ]
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class EstuaryDeleteView(GraisCRUDRequiredMixin, CommonDeleteView):
    model = models.Estuary
    success_url = reverse_lazy('grais:estuary_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'grais/confirm_delete.html'


# SITE #
########

class SiteUpdateView(GraisCRUDRequiredMixin, CommonUpdateView):
    model = models.Site
    form_class = forms.SiteForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:site_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class SiteCreateView(GraisCRUDRequiredMixin, CommonCreateView):
    model = models.Site
    form_class = forms.SiteForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}

    def get_parent_crumb(self):
        return {"title": self.get_estuary(), "url": reverse_lazy("grais:estuary_detail", args=[self.get_estuary().id])}

    def get_estuary(self):
        return get_object_or_404(models.Estuary, pk=self.kwargs.get("estuary"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.estuary = self.get_estuary()
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class SiteDetailView(GraisCRUDRequiredMixin, CommonDetailView):
    model = models.Site
    template_name = 'grais/green_crab/site_detail.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}
    field_list = [
        'id',
        'code',
        'name',
        'description',
        'metadata',
    ]
    container_class = "container-fluid"

    def get_parent_crumb(self):
        return {"title": self.get_object().estuary, "url": reverse_lazy("grais:estuary_detail", args=[self.get_object().estuary.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sample_field_list"] = [
            "id",
            "season",
        ]
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class SiteDeleteView(GraisCRUDRequiredMixin, CommonDeleteView):
    model = models.Site
    success_message = 'The functional group was successfully deleted!'
    template_name = 'grais/confirm_delete.html'
    greatgrandparent_crumb = {"title": gettext_lazy("Estuaries"), "url": reverse_lazy("grais:estuary_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:site_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().estuary, "url": reverse_lazy("grais:estuary_detail", args=[self.get_object().estuary.id])}

    def get_success_url(self):
        return self.get_grandparent_crumb().get("url")


# GCSAMPLE #
###########

class GCSampleListView(GraisAccessRequiredMixin, CommonFilterView):
    model = models.GCSample
    template_name = 'grais/list.html'
    filterset_class = filters.GCSampleFilter
    paginate_by = 100
    home_url_name = "grais:index"
    new_object_url = reverse_lazy("grais:gcsample_new")
    row_object_url_name = row_ = "grais:gcsample_detail"
    h1 = "Green Crab Samples"

    field_list = [
        {"name": 'season', "class": "", "width": ""},
        {"name": 'site', "class": "", "width": ""},
        {"name": 'traps_set', "class": "", "width": ""},
        {"name": 'traps_fished', "class": "", "width": ""},
        {"name": 'trap_count|{}'.format("trap count"), "class": "", "width": ""},
        {"name": 'bycatch_count|{}'.format("bycatch count"), "class": "", "width": ""},
        {"name": 'invasive_crabs_count|{}'.format("invasive crab count"), "class": "", "width": ""},
        {"name": 'noninvasive_crabs_count|{}'.format("non-invasive crab count"), "class": "", "width": ""},
    ]


class GCSampleUpdateView(GraisCRUDRequiredMixin, CommonUpdateView):
    model = models.GCSample
    form_class = forms.GCSampleForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:gcsample_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class GCSampleCreateView(GraisCRUDRequiredMixin, CommonCreateView):
    model = models.GCSample
    form_class = forms.GCSampleForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class GCSampleDetailView(GraisCRUDRequiredMixin, CommonDetailView):
    model = models.GCSample
    template_name = 'grais/green_crab/sample_detail/main.html'
    home_url_name = "grais:index"
    parent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}
    field_list = [
        'id',
        'site',
        'season',
        'traps_set',
        'traps_fished',
        'samplers',
        'eelgrass_assessed',
        'eelgrass_percent_coverage',
        'vegetation_species',
        'sediment',
        'notes',
        'metadata',

    ]
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["probe_field_list"] = [
            'dt|Date/time',
            'probe',
            'cloud_cover',
            'temp_c',
            'sal',
            'o2_percent',
            'o2_mgl',
            'sp_cond_ms',
            'cond_ms',
            'cloud_cover',
            'tide_description',
            'weather_conditions',
        ]
        context["trap_field_list"] = [
            'trap_number',
            'trap_type',
            'coordinates',
            'total_green_crab_wt_kg',
            'bycatch_count|{}'.format("bycatch count"),
            'invasive_crabs_count|{}'.format("invasive crab count"),
            'noninvasive_crabs_count|{}'.format("non-invasive crab count"),
        ]
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class GCSampleDeleteView(GraisCRUDRequiredMixin, CommonDeleteView):
    model = models.GCSample
    success_url = reverse_lazy('grais:gcsample_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'grais/confirm_delete.html'


# PROBE MEASUREMENT #
#####################

class GCProbeMeasurementUpdateView(GraisAccessRequiredMixin, CommonPopoutUpdateView):
    model = models.GCProbeMeasurement
    form_class = forms.GCProbeMeasurementForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return super().form_valid(form)


class GCProbeMeasurementCreateView(GraisAccessRequiredMixin, CommonPopoutCreateView):
    model = models.GCProbeMeasurement
    form_class = forms.GCProbeMeasurementForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sample = get_object_or_404(models.GCSample, pk=self.kwargs.get("sample"))
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)


class GCProbeMeasurementDeleteView(GraisAccessRequiredMixin, CommonPopoutDeleteView):
    model = models.GCProbeMeasurement


# TRAPS #
###########

class TrapUpdateView(GraisCRUDRequiredMixin, CommonUpdateView):
    model = models.Trap
    form_class = forms.TrapForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:trap_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class TrapCreateView(GraisCRUDRequiredMixin, CommonCreateView):
    model = models.Trap
    form_class = forms.TrapForm
    template_name = 'grais/form.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_sample(), "url": reverse_lazy("grais:gcsample_detail", args=[self.get_sample().id])}

    def get_sample(self):
        return get_object_or_404(models.GCSample, pk=self.kwargs.get("sample"))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sample = self.get_sample()
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class TrapDetailView(GraisCRUDRequiredMixin, CommonDetailView):
    model = models.Trap
    template_name = 'grais/green_crab/trap_detail/main.html'
    home_url_name = "grais:index"
    grandparent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}
    field_list = [
        'id',
        'trap_number',
        'trap_type',
        'bait_type',
        'depth_at_set_m',
        'coordinates',
        'gps_waypoint',
        'notes',
        'total_green_crab_wt_kg',
        'bycatch_count|{}'.format("bycatch count"),
        'invasive_crabs_count|{}'.format("invasive crab count"),
        'noninvasive_crabs_count|{}'.format("non-invasive crab count"),
    ]
    container_class = "container-fluid"

    def get_parent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("grais:gcsample_detail", args=[self.get_object().sample.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crab_field_list"] = [
            'species',
            'width',
            'sex',
            'carapace_color',
            'abdomen_color',
            'egg_color',
            'notes',
        ]
        context["bycatch_field_list"] = [
            'species',
            'count',
            'notes',
        ]

        context["mapbox_api_key"] = settings.MAPBOX_API_KEY
        return context


class TrapDeleteView(GraisCRUDRequiredMixin, CommonDeleteView):
    model = models.Trap
    success_message = 'The functional group was successfully deleted!'
    template_name = 'grais/confirm_delete.html'
    greatgrandparent_crumb = {"title": gettext_lazy("Green Crab Samples"), "url": reverse_lazy("grais:gcsample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("grais:trap_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("grais:gcsample_detail", args=[self.get_object().sample.id])}

    def get_success_url(self):
        return self.get_grandparent_crumb().get("url")


# SPECIES OBSERVATIONS - VUE JS #
##################################

class CatchObservationTemplateView(GraisAccessRequiredMixin, CommonDetailView):
    template_name = 'grais/green_crab/species_observations.html'
    home_url_name = 'grais:index'
    greatgrandparent_crumb = {"title": gettext_lazy("GCSamples"), "url": reverse_lazy("grais:gcsample_list")}

    def get_object(self):
        return get_object_or_404(models.Trap, pk=self.kwargs.get("pk"))

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy(f"grais:trap_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy(f"grais:gcsample_detail", args=[self.get_object().sample.id])}

    def get_greatgrandparent_crumb(self):
        return {"title": "Green Crab Samples", "url": reverse_lazy(f"grais:gcsample_list")}

    def get_h1(self):
        return f"{self.kwargs.get('type').title()} Observations"


class BaitFormsetView(GraisAdminRequiredMixin, CommonFormsetView):
    template_name = 'grais/formset.html'
    h1 = "Manage Bait Types"
    queryset = models.Bait.objects.all()
    formset_class = forms.BaitFormset
    success_url_name = "grais:manage_baits"
    home_url_name = "grais:index"
    delete_url_name = "grais:delete_bait"


class BaitHardDeleteView(GraisAdminRequiredMixin, CommonHardDeleteView):
    model = models.Bait
    success_url = reverse_lazy("grais:manage_baits")
