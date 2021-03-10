from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy

from lib.templatetags.custom_filters import nz
from shared_models.views import CommonTemplateView, CommonHardDeleteView, CommonFormsetView, CommonFormView
from . import models, forms
from .mixins import LoginAccessRequiredMixin, eDNAAdminRequiredMixin
from .utils import in_edna_admin_group


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'edna/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_edna_admin_group(self.request.user)
        return context


# REFERENCE TABLES #
####################

class ExperimentTypeFormsetView(eDNAAdminRequiredMixin, CommonFormsetView):
    template_name = 'edna/formset.html'
    h1 = "Manage Experiment Types"
    queryset = models.ExperimentType.objects.all()
    formset_class = forms.ExperimentTypeFormset
    success_url_name = "edna:manage_experiment_types"
    home_url_name = "edna:index"
    delete_url_name = "edna:delete_experiment_type"


class ExperimentTypeHardDeleteView(eDNAAdminRequiredMixin, CommonHardDeleteView):
    model = models.ExperimentType
    success_url = reverse_lazy("edna:manage_experiment_types")


class DNAExtractionProtocolFormsetView(eDNAAdminRequiredMixin, CommonFormsetView):
    template_name = 'edna/formset.html'
    h1 = "Manage DNA Extraction Protocols"
    queryset = models.DNAExtractionProtocol.objects.all()
    formset_class = forms.DNAExtractionProtocolFormset
    success_url_name = "edna:manage_dna_experiment_protocols"
    home_url_name = "edna:index"
    delete_url_name = "edna:delete_dna_experiment_protocol"


class DNAExtractionProtocolHardDeleteView(eDNAAdminRequiredMixin, CommonHardDeleteView):
    model = models.DNAExtractionProtocol
    success_url = reverse_lazy("edna:manage_dna_experiment_protocols")


#
# # REGIONS #
# ###########
#
# class RegionListView(eDNAAdminRequiredMixin, CommonFilterView):
#     template_name = 'edna/list.html'
#     filterset_class = filters.RegionFilter
#     home_url_name = "edna:index"
#     new_object_url = reverse_lazy("edna:region_new")
#     row_object_url_name = row_ = "edna:region_detail"
#     container_class = "container-fluid bg-light curvy"
#
#     field_list = [
#         {"name": 'name', "class": "", "width": ""},
#         {"name": 'tdescription|{}'.format("description"), "class": "", "width": ""},
#         {"name": 'province', "class": "", "width": ""},
#     ]
#
#     def get_queryset(self):
#         return models.Region.objects.annotate(
#             search_term=Concat('name', Value(" "), 'abbreviation', output_field=TextField()))
#
#
# class RegionUpdateView(eDNAAdminRequiredMixin, CommonUpdateView):
#     model = models.Region
#     form_class = forms.RegionForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#     container_class = "container bg-light curvy"
#
#
# class RegionCreateView(eDNAAdminRequiredMixin, CommonCreateView):
#     model = models.Region
#     form_class = forms.RegionForm
#     success_url = reverse_lazy('edna:region_list')
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#     container_class = "container bg-light curvy"
#
#
# class RegionDetailView(eDNAAdminRequiredMixin, CommonDetailView):
#     model = models.Region
#     template_name = 'edna/region_detail.html'
#     home_url_name = "edna:index"
#     parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#     container_class = "container bg-light curvy"
#     field_list = [
#         'name',
#         'tdescription|{}'.format("description"),
#         'province',
#         'samples|{}'.format(_("sample count")),
#     ]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         site_field_list = [
#             'name',
#             'abbreviation',
#             'tdescription|{}'.format("description"),
#             'coordinates',
#         ]
#         context["site_field_list"] = site_field_list
#         return context
#
#
# class RegionDeleteView(eDNAAdminRequiredMixin, CommonDeleteView):
#     model = models.Region
#     success_url = reverse_lazy('edna:region_list')
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'edna/confirm_delete.html'
#     container_class = "container bg-light curvy"
#
#
# # SITES #
# #########
#
#
# class SiteCreateView(eDNAAdminRequiredMixin, CommonCreateView):
#     model = models.Site
#     form_class = forms.SiteForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     container_class = "container bg-light curvy"
#     grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#
#     def get_region(self):
#         return get_object_or_404(models.Region, pk=self.kwargs.get("region"))
#
#     def get_parent_crumb(self):
#         return {"title": self.get_region(), "url": reverse("edna:region_detail", args=[self.get_region().id])}
#
#     def get_success_url(self):
#         return self.get_parent_crumb()["url"]
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.region = self.get_region()
#         return super().form_valid(form)
#
#
# class SiteDetailView(eDNAAdminRequiredMixin, CommonDetailView):
#     model = models.Site
#     template_name = 'edna/site_detail.html'
#     home_url_name = "edna:index"
#     grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#     container_class = "container bg-light curvy"
#     field_list = [
#         'name',
#         'abbreviation',
#         'tdescription|{}'.format("description"),
#         'coordinates',
#     ]
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("edna:region_detail", args=[self.get_object().region.id])}
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         transect_field_list = [
#             'name',
#             'starting_coordinates_ddmm|{}'.format(_("starting coordinates")),
#             'ending_coordinates_ddmm|{}'.format(_("ending coordinates")),
#             'transect_distance|{}'.format(_("transect distance (m)")),
#
#         ]
#         context["transect_field_list"] = transect_field_list
#         return context
#
#
# class SiteUpdateView(eDNAAdminRequiredMixin, CommonUpdateView):
#     model = models.Site
#     form_class = forms.SiteForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#     container_class = "container bg-light curvy"
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("edna:site_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("edna:region_detail", args=[self.get_object().region.id])}
#
#
# class SiteDeleteView(eDNAAdminRequiredMixin, CommonDeleteView):
#     model = models.Site
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'edna/confirm_delete.html'
#     container_class = "container bg-light curvy"
#     home_url_name = "edna:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("edna:site_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("edna:region_detail", args=[self.get_object().region.id])}
#
#
# # TRANSECTS #
# #############
#
#
# class TransectCreateView(eDNAAdminRequiredMixin, CommonCreateView):
#     model = models.Transect
#     form_class = forms.TransectForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     container_class = "container bg-light curvy"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#
#     def get_site(self):
#         site = get_object_or_404(models.Site, pk=self.kwargs["site"])
#         return site
#
#     def get_parent_crumb(self):
#         return {"title": self.get_site(), "url": reverse("edna:site_detail", args=[self.get_site().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_site().region, "url": reverse("edna:region_detail", args=[self.get_site().region.id])}
#
#     def get_success_url(self):
#         return self.get_parent_crumb()["url"]
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         obj.site = self.get_site()
#         return super().form_valid(form)
#
#
# class TransectUpdateView(eDNAAdminRequiredMixin, CommonUpdateView):
#     model = models.Transect
#     form_class = forms.TransectForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     container_class = "container bg-light curvy"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object().site, "url": reverse("edna:site_detail", args=[self.get_object().site.id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().site.region, "url": reverse("edna:region_detail", args=[self.get_object().site.region.id])}
#
#
# class TransectDeleteView(eDNAAdminRequiredMixin, CommonDeleteView):
#     model = models.Transect
#     success_url = reverse_lazy('edna:region_list')
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'edna/confirm_delete.html'
#     container_class = "container bg-light curvy"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("edna:region_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object().site, "url": reverse("edna:site_detail", args=[self.get_object().site.id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().site.region, "url": reverse("edna:region_detail", args=[self.get_object().site.region.id])}
#
#
# # SAMPLES #
# ###########
#
# class SampleListView(eDNAAdminRequiredMixin, CommonFilterView):
#     model = models.Sample
#     template_name = 'edna/list.html'
#     filterset_class = filters.SampleFilter
#     home_url_name = "edna:index"
#     row_object_url_name = "edna:sample_detail"
#     new_object_url = reverse_lazy("edna:sample_new")
#     new_btn_text = gettext_lazy("Add a New Sample")
#     container_class = "container-fluid bg-light curvy"
#     field_list = [
#         {"name": 'id|{}'.format("sample Id"), "class": "", "width": ""},
#         {"name": 'datetime|{}'.format("date"), "class": "", "width": ""},
#         {"name": 'site.region|{}'.format("region"), "class": "", "width": ""},
#         {"name": 'site', "class": "", "width": ""},
#         {"name": 'dive_count|{}'.format(_("dive count")), "class": "", "width": ""},
#     ]
#
#
# class SampleUpdateView(eDNAAdminRequiredMixin, CommonUpdateView):
#     model = models.Sample
#     form_class = forms.SampleForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#     container_class = "container bg-light curvy"
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse("edna:sample_detail", args=[self.get_object().id])}
#
#
# class SampleCreateView(eDNAAdminRequiredMixin, CommonCreateView):
#     model = models.Sample
#     form_class = forms.SampleForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     parent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#     container_class = "container bg-light curvy"
#
#
# class SampleDetailView(eDNAAdminRequiredMixin, CommonDetailView):
#     model = models.Sample
#     template_name = 'edna/sample_detail.html'
#     home_url_name = "edna:index"
#     parent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#     container_class = "container bg-light curvy"
#     field_list = [
#         'site_region|{}'.format(gettext_lazy("site")),
#         'datetime',
#         'weather_notes',
#         'comment',
#     ]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         dive_field_list = [
#             'transect',
#             'diver',
#             'heading',
#             'side',
#             'width_m',
#             'comment',
#             'observation_count|{}'.format(_("lobster count")),
#         ]
#         context["dive_field_list"] = dive_field_list
#         return context
#
#
# class SampleDeleteView(eDNAAdminRequiredMixin, CommonDeleteView):
#     model = models.Sample
#     success_url = reverse_lazy('edna:sample_list')
#     home_url_name = "edna:index"
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'edna/confirm_delete.html'
#     container_class = "container bg-light curvy"
#     grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse("edna:sample_detail", args=[self.get_object().id])}
#
#
# # DIVES #
# #########
#
# class DiveCreateView(eDNAAdminRequiredMixin, CommonCreateView):
#     model = models.Dive
#     form_class = forms.DiveForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     container_class = "container bg-light curvy"
#     grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#
#     def get_initial(self):
#         sample = self.get_sample()
#         return dict(
#             sample=sample.id,
#             start_descent=sample.datetime,
#             start_final_ascent=sample.datetime,
#             reach_surface=sample.datetime,
#         )
#
#     def get_sample(self):
#         return get_object_or_404(models.Sample, pk=self.kwargs.get("sample"))
#
#     def get_parent_crumb(self):
#         return {"title": self.get_sample(), "url": reverse("edna:sample_detail", args=[self.get_sample().id])}
#
#     def get_success_url(self):
#         return self.get_parent_crumb()["url"]
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         sample = self.get_sample()
#         obj.sample = sample
#         return super().form_valid(form)
#
#
# class DiveUpdateView(eDNAAdminRequiredMixin, CommonUpdateView):
#     model = models.Dive
#     form_class = forms.DiveForm
#     template_name = 'edna/form.html'
#     home_url_name = "edna:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#     container_class = "container bg-light curvy"
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("edna:dive_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().sample, "url": reverse_lazy("edna:sample_detail", args=[self.get_object().sample.id])}
#
#
# class DiveDeleteView(eDNAAdminRequiredMixin, CommonDeleteView):
#     model = models.Dive
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'edna/confirm_delete.html'
#     container_class = "container bg-light curvy"
#     home_url_name = "edna:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("edna:dive_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().sample, "url": reverse_lazy("edna:sample_detail", args=[self.get_object().sample.id])}
#
#
# class DiveDetailView(eDNAAdminRequiredMixin, CommonDetailView):
#     model = models.Dive
#     template_name = 'edna/dive_detail.html'
#     home_url_name = "edna:index"
#     grandparent_crumb = {"title": gettext_lazy("Samples"), "url": reverse_lazy("edna:sample_list")}
#     container_class = "container bg-light curvy"
#     field_list = [
#         'transect',
#         'diver',
#         'starting_coordinates_ddmm|{}'.format(_("starting coordinates")),
#         'ending_coordinates_ddmm|{}'.format(_("ending coordinates")),
#         'dive_distance|{}'.format(_("dive distance (m)")),
#         'start_descent',
#         'bottom_time',
#         'max_depth_ft',
#         'psi_in',
#         'psi_out',
#         'heading',
#         'side',
#         'width_m',
#         'comment',
#     ]
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object().sample, "url": reverse("edna:sample_detail", args=[self.get_object().sample.id])}
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         section_field_list = [
#             'interval',
#             'depth_ft',
#             'substrate_profile|{}'.format(_("substrate profile")),
#             'comment',
#         ]
#         context["section_field_list"] = section_field_list
#         observation_field_list = [
#             'id',
#             'sex_special_display|{}'.format("sex"),
#             'egg_status_special_display|{}'.format("egg status"),
#             'carapace_length_mm',
#             'certainty_rating_special_display|{}'.format("length certainty"),
#             'comment',
#         ]
#         context["observation_field_list"] = observation_field_list
#         context["random_observation"] = models.Observation.objects.first()
#         return context
#
#
# class DiveDataEntryDetailView(eDNAAdminRequiredMixin, CommonDetailView):
#     model = models.Dive
#     template_name = 'edna/dive_data_entry/main.html'
#     container_class = "container bg-light-green curvy"
#     field_list = [
#         'id|{}'.format(_("dive Id")),
#         'transect',
#         'diver',
#         'heading',
#         'side',
#         'width_m',
#         'comment',
#     ]
#
#     def get_h1(self):
#         return _("Data Entry Mode")
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         section_field_list = [
#             'interval',
#             'depth_ft',
#             'substrate_profile|{}'.format(_("substrate profile")),
#             'observation_count|{}'.format(_("observation count")),
#             'comment',
#         ]
#         context["section_field_list"] = section_field_list
#         observation_field_list = [
#             'id',
#             'sex',
#             'egg_status',
#             'carapace_length_mm',
#             'certainty_rating',
#             'comment',
#         ]
#         context["observation_field_list"] = observation_field_list
#         context["random_section"] = models.Section.objects.first()
#         context["random_observation"] = models.Observation.objects.first()
#         context["section_form"] = forms.SectionForm
#         context["obs_form"] = forms.ObservationForm
#         context["new_obs_form"] = forms.NewObservationForm
#         return context
#
#
# REPORTS #
###########

class ReportSearchFormView(eDNAAdminRequiredMixin, CommonFormView):
    template_name = 'edna/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("eDNA Reports")

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = nz(form.cleaned_data["year"], "None")
        if report == 1:
            return HttpResponseRedirect(reverse("edna:dive_log_report") + f"?year={year}")
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("edna:reports"))

#
# @login_required()
# def dive_log_report(request):
#     year = None if not request.GET.get("year") or request.GET.get("year") == "None" else int(request.GET.get("year"))
#     file_url = reports.generate_dive_log(year=year)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = f'inline; filename="dive log ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'
#
#             return response
#     raise Http404
