from django.conf import settings
from django.contrib import messages
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy, gettext as _

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from shared_models.models import River
from shared_models.views import CommonFormsetView, CommonHardDeleteView, CommonTemplateView, CommonFormView, CommonUpdateView, CommonCreateView, \
    CommonDeleteView, CommonDetailView, CommonFilterView, CommonPopoutCreateView, CommonPopoutUpdateView
from . import filters
from . import forms
from . import models
from . import reports
from .mixins import TrapNetAccessRequiredMixin, TrapNetAdminRequiredMixin


class IndexTemplateView(TrapNetAccessRequiredMixin, CommonTemplateView):
    template_name = 'trapnet/index.html'
    h1 = gettext_lazy("Home")


# Settings

class SampleTypeFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Sample Types"
    queryset = models.SampleType.objects.all()
    formset_class = forms.SampleTypeFormset
    success_url_name = "trapnet:manage_sample_types"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_sample_type"


class SampleTypeHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.SampleType
    success_url = reverse_lazy("trapnet:manage_sample_types")


class StatusFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Statuses"
    queryset = models.Status.objects.all()
    formset_class = forms.StatusFormset
    success_url_name = "trapnet:manage_statuses"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_status"


class StatusHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Status
    success_url = reverse_lazy("trapnet:manage_statuses")


class SexFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Sexes"
    queryset = models.Sex.objects.all()
    formset_class = forms.SexFormset
    success_url_name = "trapnet:manage_sexes"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_sex"


class SexHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Sex
    success_url = reverse_lazy("trapnet:manage_sexes")


class LifeStageFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'trapnet/formset.html'
    h1 = "Manage Life Stages"
    queryset = models.LifeStage.objects.all()
    formset_class = forms.LifeStageFormset
    success_url_name = "trapnet:manage_life_stages"
    home_url_name = "trapnet:index"
    delete_url_name = "trapnet:delete_life_stage"


class LifeStageHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.LifeStage
    success_url = reverse_lazy("trapnet:manage_life_stages")


class OriginFormsetView(TrapNetAdminRequiredMixin, CommonFormsetView):
    template_name = 'shared_models/formset.html'
    h1 = "Manage Origins"
    queryset = models.Origin.objects.all()
    formset_class = forms.OriginFormset
    success_url_name = "shared_models:manage_origins"
    home_url_name = "shared_models:index"
    delete_url_name = "shared_models:delete_origin"


class OriginHardDeleteView(TrapNetAdminRequiredMixin, CommonHardDeleteView):
    model = models.Origin
    success_url = reverse_lazy("shared_models:manage_origins")


# SPECIES #
###########

class SpeciesListView(TrapNetAccessRequiredMixin, CommonFilterView):
    template_name = "trapnet/list.html"
    filterset_class = filters.SpeciesFilter
    queryset = models.Species.objects.annotate(
        search_term=Concat('common_name_eng', 'common_name_fre', 'scientific_name', 'code', 'abbrev', output_field=TextField()))
    new_object_url_name = "trapnet:species_new"
    row_object_url_name = "trapnet:species_detail"
    home_url_name = "trapnet:index"

    field_list = [
        {"name": 'code', "class": "", "width": ""},
        {"name": 'full_name|{}'.format(_("Species")), "class": "", "width": ""},
        {"name": 'scientific_name', "class": "", "width": ""},
        {"name": 'abbrev', "class": "", "width": ""},
        {"name": 'tsn', "class": "", "width": ""},
        {"name": 'aphia_id', "class": "", "width": ""},
    ]


class SpeciesCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = models.Species
    template_name = 'trapnet/form.html'
    form_class = forms.SpeciesForm
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class SpeciesDetailView(TrapNetAccessRequiredMixin, CommonDetailView):
    model = models.Species
    template_name = "trapnet/species_detail.html"
    field_list = [
        'code',
        'common_name_eng',
        'common_name_fre',
        'life_stage',
        'abbrev',
        'scientific_name',
        'tsn',
        'aphia_id',
        'notes',
    ]
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context


class SpeciesUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = models.Species
    template_name = 'trapnet/form.html'
    form_class = forms.SpeciesForm
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:species_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SpeciesDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.Species
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Species"), "url": reverse_lazy("trapnet:species_list")}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:species_detail", args=[self.get_object().id])}


# RIVER #
#########

class RiverListView(TrapNetAccessRequiredMixin, CommonFilterView):
    filterset_class = filters.RiverFilter
    template_name = 'trapnet/list.html'
    new_object_url_name = "trapnet:river_new"
    row_object_url_name = "trapnet:river_detail"
    home_url_name = "trapnet:index"
    queryset = River.objects.annotate(
        search_term=Concat('name', 'fishing_area_code', 'maritime_river_code', 'cgndb', output_field=TextField()))
    paginate_by = 25
    container_class = "container-fluid"
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'fishing_area_code', "class": "", "width": ""},
        {"name": 'maritime_river_code', "class": "", "width": ""},
        {"name": 'old_maritime_river_code', "class": "", "width": ""},
        {"name": 'cgndb', "class": "", "width": ""},
        {"name": 'parent_cgndb_id', "class": "", "width": ""},
        {"name": 'nbadw_water_body_id', "class": "", "width": ""},
        {"name": 'display_hierarchy|River hierarchy', "class": "", "width": ""},
    ]


class RiverCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = shared_models.River
    form_class = forms.RiverForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class RiverDetailView(TrapNetAccessRequiredMixin, CommonDetailView):
    model = shared_models.River
    template_name = 'trapnet/river_detail.html'
    field_list = [
        'name',
        'fishing_area_code',
        'maritime_river_code',
        'old_maritime_river_code',
        'cgndb',
        'parent_cgndb_id',
        'nbadw_water_body_id',
        'display_anchored_hierarchy|River hierarchy',
        'metadata',
    ]
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        context['site_field_list'] = [
            'name',
            'stream_order',
            'elevation_m',
            'province.abbrev_eng',
            'latitude_n',
            'longitude_w',
            'directions',
        ]
        context['my_site_object'] = models.RiverSite.objects.first()
        site_list = [[obj.name, obj.latitude_n, obj.longitude_w] for obj in self.object.river_sites.all() if
                     obj.latitude_n and obj.longitude_w]
        context['site_list'] = site_list
        return context


class RiverUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = shared_models.River
    form_class = forms.RiverForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:river_detail", args=[self.get_object().id])}


class RiverDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = shared_models.River
    success_url = reverse_lazy('trapnet:river_list')
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:river_detail", args=[self.get_object().id])}


# SITE #
########


class RiverSiteCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = models.RiverSite
    template_name = 'trapnet/form.html'
    form_class = forms.RiverSiteForm
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_parent_crumb(self):
        return {"title": self.get_river(), "url": reverse("trapnet:river_detail", args=[self.get_river().id])}

    def get_river(self):
        return get_object_or_404(River, pk=self.kwargs.get("river"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['river'] = self.get_river()
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.river = self.get_river()
        obj.created_by = self.request.user
        return super().form_valid(form)


class RiverSiteUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = models.RiverSite
    template_name = 'trapnet/form.html'
    form_class = forms.RiverSiteForm
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:site_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class RiverSiteDetailView(TrapNetAdminRequiredMixin, CommonDetailView):
    model = models.RiverSite
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}
    field_list = [
        'name',
        'river',
        'stream_order',
        'elevation_m',
        'province.abbrev_eng',
        'latitude_n',
        'longitude_w',
        'directions',
        'exclude_data_from_site',
        'metadata',
    ]

    def get_parent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context


class RiverSiteDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.RiverSite
    home_url_name = "trapnet:index"
    greatgrandparent_crumb = {"title": _("Rivers"), "url": reverse_lazy("trapnet:river_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().river, "url": reverse("trapnet:river_detail", args=[self.get_object().river.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:site_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# SAMPLE #
##########

class SampleListView(TrapNetAccessRequiredMixin, CommonFilterView):
    model = models.Sample
    filterset_class = filters.SampleFilter
    template_name = 'trapnet/list.html'
    queryset = models.Sample.objects.filter(site__exclude_data_from_site=False)
    new_object_url_name = "trapnet:sample_new"
    row_object_url_name = "trapnet:sample_detail"
    home_url_name = "trapnet:index"
    paginate_by = 25
    container_class = "container-fluid"
    field_list = [
        {"name": 'season', "class": "", "width": ""},
        {"name": 'sample_type', "class": "", "width": ""},
        {"name": 'site', "class": "", "width": ""},
        {"name": 'arrival_date', "class": "", "width": ""},
        {"name": 'departure_date', "class": "", "width": ""},
    ]


class SampleUpdateView(TrapNetAdminRequiredMixin, CommonUpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sample_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class SampleCreateView(TrapNetAdminRequiredMixin, CommonCreateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'trapnet/form.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super().form_valid(form)


class SampleDetailView(TrapNetAccessRequiredMixin, CommonDetailView):
    model = models.Sample
    template_name = 'trapnet/sample_detail.html'
    home_url_name = "trapnet:index"
    parent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        field_list = [
            'site',
            'sample_type',
            'arrival_date',
            'departure_date',
            'air_temp_arrival',
            'min_air_temp',
            'max_air_temp',
            'percent_cloud_cover',
            'precipitation_category',
            'precipitation_comment',
            'wind_speed',
            'wind_direction',
            'water_depth_m',
            'water_level_delta_m',
            'discharge_m3_sec',
            'water_temp_shore_c',
            'water_temp_trap_c',
            'rpm_arrival',
            'rpm_departure',
            'operating_condition',
            'operating_condition_comment',
            'notes',
            'season',
            'metadata',
        ]
        context['field_list'] = field_list

        context['obs_field_list'] = [
            'species',
            'status',
            'origin',
            'frequency',
            'fork_length',
            'total_length',
        ]
        context['my_obs_object'] = models.Entry.objects.first()

        return context


class SampleDeleteView(TrapNetAdminRequiredMixin, CommonDeleteView):
    model = models.Sample
    template_name = 'trapnet/confirm_delete.html'
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("trapnet:sample_detail", args=[self.get_object().id])}

    def get_success_url(self):
        return self.get_grandparent_crumb()["url"]


# OBSERVATIONS #
################

class EntryInsertView(TrapNetAccessRequiredMixin, CommonTemplateView):
    template_name = "trapnet/obs_insert.html"
    h1 = "Add / Modify Entries"
    home_url_name = "trapnet:index"
    grandparent_crumb = {"title": _("Samples"), "url": reverse_lazy("trapnet:sample_list")}

    def get_sample(self):
        return get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))

    def get_parent_crumb(self):
        return {"title": self.get_sample(), "url": reverse("trapnet:sample_detail", args=[self.get_sample().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = models.Sample.objects.get(pk=self.kwargs['sample'])
        context['sample'] = sample

        queryset = models.Species.objects.all()
        # get a list of species
        species_list = []
        for obj in queryset:
            html_insert = '<a class="add-btn btn btn-outline-dark" href="#" target-url="{}"> <img src="{}" alt=""></a><span style="margin-left: 10px;">{} - {} - <em>{}</em> </span>'.format(
                reverse("trapnet:obs_new", kwargs={"sample": sample.id, "species": obj.id}),
                static("admin/img/icon-addlink.svg"),
                obj.code,
                str(obj),
                obj.scientific_name,
            )
            species_list.append(html_insert)
        context['species_list'] = species_list
        context['obs_field_list'] = [
            'species',
            'first_tag',
            'last_tag',
            'status',
            'origin',
            'frequency',
            'fork_length',
            'total_length',
            'weight',
            'sex',
            'smolt_age',
            'location_tagged',
            'date_tagged',
            'scale_id_number',
            'tags_removed',
            'notes',
        ]
        context['my_obs_object'] = models.Entry.objects.first()
        return context


class EntryCreateView(TrapNetAccessRequiredMixin, CommonPopoutCreateView):
    model = models.Entry
    form_class = forms.EntryForm

    def get_sample(self):
        return get_object_or_404(models.Sample, pk=self.kwargs['sample'])

    def get_species(self):
        return get_object_or_404(models.Species, pk=self.kwargs['species'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species = models.Species.objects.get(id=self.kwargs['species'])
        sample = models.Sample.objects.get(id=self.kwargs['sample'])
        context['species'] = species
        context['sample'] = sample
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sample = self.get_sample()
        obj.species = self.get_species()
        obj.created_by = self.request.user
        return super().form_valid(form)


class EntryUpdateView(TrapNetAccessRequiredMixin, CommonPopoutUpdateView):
    model = models.Entry
    form_class = forms.EntryForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


def species_observation_delete(request, pk):
    object = models.Entry.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The species has been successfully deleted from {}.".format(object.sample))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# REPORTS #
###########

class ReportSearchFormView(TrapNetAccessRequiredMixin, CommonFormView):
    template_name = 'trapnet/report_search.html'
    form_class = forms.ReportSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        # ais_species_list = str(form.cleaned_data["ais_species"]).replace("[", "").replace("]", "").replace(" ", "").replace("'","").replace('"',"")

        report = int(form.cleaned_data["report"])
        my_year = form.cleaned_data["year"] if form.cleaned_data["year"] else "None"
        my_sites = listrify(form.cleaned_data["sites"]) if len(form.cleaned_data["sites"]) > 0 else "None"

        if report == 1:
            return HttpResponseRedirect(reverse("trapnet:sample_report", kwargs={"year": my_year, "sites": my_sites}))
        elif report == 2:
            return HttpResponseRedirect(reverse("trapnet:entry_report", kwargs={"year": my_year, "sites": my_sites}))
        elif report == 3:
            return HttpResponseRedirect(reverse("trapnet:od1_report", kwargs={"year": my_year, "sites": my_sites}))
        elif report == 4:
            return HttpResponseRedirect(reverse("trapnet:od1_dictionary"))
        elif report == 7:
            return HttpResponseRedirect(reverse("trapnet:od_spp_list"))
        elif report == 5:
            return HttpResponseRedirect(reverse("trapnet:od1_wms", kwargs={"lang": 1}))
        elif report == 6:
            return HttpResponseRedirect(reverse("trapnet:od1_wms", kwargs={"lang": 2}))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("trapnet:report_search"))


def export_sample_data(request, year, sites):
    response = reports.generate_sample_report(year, sites)
    return response


def export_entry_data(request, year, sites):
    response = reports.generate_entry_report(year, sites)
    return response


def export_open_data_ver1(request, year, sites):
    response = reports.generate_open_data_ver_1_report(year, sites)
    return response


def export_open_data_ver1_dictionary(request):
    response = reports.generate_open_data_ver_1_data_dictionary()
    return response


def export_spp_list(request):
    response = reports.generate_spp_list()
    return response


def export_open_data_ver1_wms(request, lang):
    response = reports.generate_open_data_ver_1_wms_report(lang)
    return response
