import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy, gettext as _

from scuba.mixins import LoginAccessRequiredMixin, ScubaAdminRequiredMixin, ScubaCRUDAccessRequiredMixin, SuperuserOrAdminRequiredMixin, ScubaBasicMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDeleteView, CommonDetailView, CommonFormView
from . import models, forms, filters, reports


class IndexTemplateView(ScubaBasicMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'scuba/index.html'


# REFERENCE TABLES #
####################


class ScubaUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'scuba/formset.html'
    h1 = "Manage Scuba Users"
    queryset = models.ScubaUser.objects.all()
    formset_class = forms.ScubaUserFormset
    success_url_name = "scuba:manage_scuba_users"
    home_url_name = "scuba:index"
    delete_url_name = "scuba:delete_scuba_user"
    container_class = "container bg-light curvy"


class ScubaUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.ScubaUser
    success_url = reverse_lazy("scuba:manage_scuba_users")


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


class SpeciesFormsetView(ScubaAdminRequiredMixin, CommonFormsetView):
    template_name = 'scuba/formset.html'
    h1 = "Manage Species"
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormset
    success_url_name = "scuba:manage_species"
    home_url_name = "scuba:index"
    delete_url_name = "scuba:delete_species"


class SpeciesHardDeleteView(ScubaAdminRequiredMixin, CommonHardDeleteView):
    model = models.Species
    success_url = reverse_lazy("scuba:manage_species")


# REGIONS #
###########

class RegionListView(ScubaAdminRequiredMixin, CommonFilterView):
    template_name = 'scuba/list.html'
    filterset_class = filters.RegionFilter
    home_url_name = "scuba:index"
    new_object_url = reverse_lazy("scuba:region_new")
    row_object_url_name = row_ = "scuba:region_detail"
    container_class = "container curvy"

    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'abbreviation', "class": "", "width": ""},
        {"name": 'tdescription|{}'.format("description"), "class": "", "width": ""},
        {"name": 'province', "class": "", "width": ""},
        {"name": 'transect_count|{}'.format(_("# transect")), "class": "", "width": ""},
        {"name": 'sample_count|{}'.format(_("# outings")), "class": "", "width": ""},
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
    container_class = "container curvy"


class RegionCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Region
    form_class = forms.RegionForm
    success_url = reverse_lazy('scuba:region_list')
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container curvy"


class RegionDetailView(ScubaAdminRequiredMixin, CommonDetailView):
    model = models.Region
    template_name = 'scuba/region_detail.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
    container_class = "container curvy"
    field_list = [
        'name',
        'abbreviation',
        'tdescription|{}'.format("description"),
        'province',
        'coordinates',
        'transect_count|{}'.format(_("# transects")),
        'sample_count|{}'.format(_("# outings")),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transect_field_list = [
            'name',
            'old_name',
            'starting_coordinates_ddmm|{}'.format(_("starting coordinates (0m)")),
            'ending_coordinates_ddmm|{}'.format(_("ending coordinates (100m)")),
            'distance|{}'.format(_("transect distance (m)")),

        ]
        context["transect_field_list"] = transect_field_list
        return context


class RegionDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Region
    success_url = reverse_lazy('scuba:region_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container curvy"


#
#
# # SITES #
# #########
#
#
# class SiteCreateView(ScubaAdminRequiredMixin, CommonCreateView):
#     model = models.Site
#     form_class = forms.SiteForm
#     template_name = 'scuba/form.html'
#     home_url_name = "scuba:index"
#     container_class = "container curvy"
#     grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
#
#     def get_region(self):
#         return get_object_or_404(models.Region, pk=self.kwargs.get("region"))
#
#     def get_parent_crumb(self):
#         return {"title": self.get_region(), "url": reverse("scuba:region_detail", args=[self.get_region().id])}
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
# class SiteDetailView(ScubaAdminRequiredMixin, CommonDetailView):
#     model = models.Site
#     template_name = 'scuba/site_detail.html'
#     home_url_name = "scuba:index"
#     grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
#     container_class = "container curvy"
#     field_list = [
#         'name',
#         'abbreviation',
#         'tdescription|{}'.format("description"),
#         'coordinates',
#     ]
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         return context
#
#
# class SiteUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
#     model = models.Site
#     form_class = forms.SiteForm
#     template_name = 'scuba/form.html'
#     home_url_name = "scuba:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
#     container_class = "container curvy"
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("scuba:site_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}
#
#
# class SiteDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
#     model = models.Site
#     success_message = 'The functional group was successfully deleted!'
#     template_name = 'scuba/confirm_delete.html'
#     container_class = "container curvy"
#     home_url_name = "scuba:index"
#     greatgrandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}
#
#     def get_parent_crumb(self):
#         return {"title": self.get_object(), "url": reverse_lazy("scuba:site_detail", args=[self.get_object().id])}
#
#     def get_grandparent_crumb(self):
#         return {"title": self.get_object().region, "url": reverse_lazy("scuba:region_detail", args=[self.get_object().region.id])}
#

# TRANSECTS #
#############


class TransectCreateView(ScubaAdminRequiredMixin, CommonCreateView):
    model = models.Transect
    form_class = forms.TransectForm
    template_name = 'scuba/coord_form.html'
    home_url_name = "scuba:index"
    container_class = "container curvy"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_region(self):
        region = get_object_or_404(models.Region, pk=self.kwargs["region"])
        return region

    def get_parent_crumb(self):
        return {"title": self.get_region(), "url": reverse("scuba:region_detail", args=[self.get_region().id])}

    def get_success_url(self):
        return self.get_parent_crumb()["url"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.region = self.get_region()
        return super().form_valid(form)


class TransectUpdateView(ScubaAdminRequiredMixin, CommonUpdateView):
    model = models.Transect
    form_class = forms.TransectForm
    template_name = 'scuba/coord_form.html'
    home_url_name = "scuba:index"
    container_class = "container curvy"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().region, "url": reverse("scuba:region_detail", args=[self.get_object().region.id])}


class TransectDeleteView(ScubaAdminRequiredMixin, CommonDeleteView):
    model = models.Transect
    success_url = reverse_lazy('scuba:region_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container curvy"
    grandparent_crumb = {"title": gettext_lazy("Regions"), "url": reverse_lazy("scuba:region_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object().region, "url": reverse("scuba:region_detail", args=[self.get_object().region.id])}


# SAMPLES #
###########

class SampleListView(ScubaBasicMixin, CommonFilterView):
    model = models.Sample
    template_name = 'scuba/list.html'
    filterset_class = filters.SampleFilter
    home_url_name = "scuba:index"
    row_object_url_name = "scuba:sample_detail"
    new_object_url = reverse_lazy("scuba:sample_new")
    new_btn_text = gettext_lazy("Add a New Sample")
    container_class = "container curvy"
    paginate_by = 25
    field_list = [
        {"name": 'id|{}'.format("sample Id"), "class": "", "width": ""},
        {"name": 'datetime|{}'.format("date"), "class": "", "width": ""},
        {"name": 'transect.region|region', "class": "", "width": ""},
        {"name": 'transect', "class": "", "width": ""},
        {"name": 'is_data_entry_complete|{}'.format("data entry complete?"), "class": "", "width": ""},
        {"name": 'dive_count|{}'.format(_("dive count")), "class": "", "width": ""},
    ]


class SampleUpdateView(ScubaCRUDAccessRequiredMixin, CommonUpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'scuba/coord_form.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("scuba:sample_detail", args=[self.get_object().id])}


class SampleCreateView(ScubaCRUDAccessRequiredMixin, CommonCreateView):
    model = models.Sample
    form_class = forms.SampleForm
    template_name = 'scuba/coord_form.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container curvy"


class SampleDetailView(ScubaBasicMixin, CommonDetailView):
    model = models.Sample
    template_name = 'scuba/sample_detail.html'
    home_url_name = "scuba:index"
    parent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container curvy"
    field_list = [
        'transect',
        'datetime',
        'starting_coordinates_ddmm|{}'.format(_("starting coordinates")),
        'ending_coordinates_ddmm|{}'.format(_("ending coordinates")),
        'distance|{}'.format(_("transect distance (m)")),
        'weather_notes',
        # 'is_upm',
        'comment',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dive_field_list = [
            'is_training|{}'.format(_("Training?")),
            # 'transect',
            'diver',
            'heading',
            'side',
            'width_m',
            'was_seeded',
            'comment',
            'observation_count|{}'.format(_("observation count")),
            "has_all_sections|{}".format(_("All sections present")),
        ]
        context["dive_field_list"] = dive_field_list
        return context


class SampleDeleteView(ScubaCRUDAccessRequiredMixin, CommonDeleteView):
    model = models.Sample
    success_url = reverse_lazy('scuba:sample_list')
    home_url_name = "scuba:index"
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container curvy"
    grandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("scuba:sample_detail", args=[self.get_object().id])}


# DIVES #
#########

class DiveCreateView(ScubaCRUDAccessRequiredMixin, CommonCreateView):
    model = models.Dive
    form_class = forms.DiveForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    container_class = "container curvy"
    grandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}

    def get_initial(self):
        sample = self.get_sample()
        return dict(
            sample=sample.id,
            start_descent=sample.datetime.strftime("%Y-%m-%dT") + "08:00",
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
        obj.created_by = self.request.user
        return super().form_valid(form)


class DiveUpdateView(ScubaCRUDAccessRequiredMixin, CommonUpdateView):
    model = models.Dive
    form_class = forms.DiveForm
    template_name = 'scuba/form.html'
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:dive_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("scuba:sample_detail", args=[self.get_object().sample.id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class DiveDeleteView(ScubaCRUDAccessRequiredMixin, CommonDeleteView):
    model = models.Dive
    success_message = 'The functional group was successfully deleted!'
    template_name = 'scuba/confirm_delete.html'
    container_class = "container curvy"
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("scuba:dive_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse_lazy("scuba:sample_detail", args=[self.get_object().sample.id])}


class DiveDetailView(ScubaBasicMixin, CommonDetailView):
    model = models.Dive
    template_name = 'scuba/dive_detail.html'
    home_url_name = "scuba:index"
    grandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}
    container_class = "container curvy"
    field_list = [
        'is_training',
        'diver',
        'dive_distance|{}'.format(_("dive distance (m)")),
        'start_descent',
        'bottom_time',
        'max_depth_ft',
        'psi_in',
        'psi_out',
        'heading',
        'side',
        'width_m',
        'comment',
        "has_all_sections|{}".format(_("All sections present")),
        'metadata',
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
            'id',
            'species',
            'sex_special_display|{}'.format("sex"),
            'egg_status_special_display|{}'.format("egg status"),
            'carapace_length_mm',
            'certainty_rating_special_display|{}'.format("length certainty"),
            'comment',
        ]
        context["observation_field_list"] = observation_field_list
        context["random_observation"] = models.Observation.objects.first()
        return context


class DiveDataEntryDetailView(ScubaCRUDAccessRequiredMixin, CommonDetailView):
    model = models.Dive
    template_name = 'scuba/dive_data_entry/main.html'
    container_class = "container-fluid"
    field_list = [
        'id|{}'.format(_("dive Id")),
        'transect',
        'diver',
        'heading',
        'side',
        'width_m',
        'comment',
    ]
    home_url_name = "scuba:index"
    greatgrandparent_crumb = {"title": gettext_lazy("Outings"), "url": reverse_lazy("scuba:sample_list")}

    def get_grandparent_crumb(self):
        return {"title": self.get_object().sample, "url": reverse("scuba:sample_detail", args=[self.get_object().sample.id])}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("scuba:dive_detail", args=[self.get_object().id])}

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
            'id',
            'sex',
            'egg_status',
            'carapace_length_mm',
            'species',
            'certainty_rating',
            'comment',
        ]
        context["observation_field_list"] = observation_field_list
        context["random_section"] = models.Section.objects.first()
        context["random_observation"] = models.Observation.objects.first()
        context["section_form"] = forms.SectionForm
        context["obs_form"] = forms.ObservationForm
        context["new_obs_form"] = forms.NewObservationForm
        qs = models.Species.objects.filter(is_default=True)
        if qs.exists():
            context["default_species_id"] = qs.first().id
        return context


# REPORTS #
###########

class ReportSearchFormView(ScubaBasicMixin, CommonFormView):
    template_name = 'scuba/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("Scuba Reports")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = form.cleaned_data["year"] if form.cleaned_data["year"] else ""
        if report == 1:
            return HttpResponseRedirect(reverse("scuba:dive_log_report") + f"?year={year}")
        elif report == 2:
            return HttpResponseRedirect(reverse("scuba:export_transect_data"))
        elif report == 3:
            return HttpResponseRedirect(reverse("scuba:export_section_data") + f"?year={year}")
        elif report == 4:
            return HttpResponseRedirect(reverse("scuba:export_obs_data") + f"?year={year}")
        elif report == 5:
            return HttpResponseRedirect(reverse("scuba:export_dive_data") + f"?year={year}")
        elif report == 6:
            return HttpResponseRedirect(reverse("scuba:export_outing_data") + f"?year={year}")
        elif report == 7:
            return HttpResponseRedirect(reverse("scuba:export_open_data") + "?dataset=true")
        elif report == 8:
            return HttpResponseRedirect(reverse("scuba:export_open_data") + "?dictionary=true")
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("scuba:reports"))


@login_required()
def dive_log_report(request):
    year = None if not request.GET.get("year") or request.GET.get("year") == "" else int(request.GET.get("year"))
    file_url = reports.generate_dive_log(year=year)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="dive log ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'

            return response
    raise Http404


def export_transect_data(request):
    year = request.GET.get("year")
    filename = "scuba transect export ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_transect_csv()),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_outing_data(request):
    year = request.GET.get("year")
    filename = "outing data export ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_outing_csv(year)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_section_data(request):
    year = request.GET.get("year")
    filename = "section data export ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_section_csv(year)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_dive_data(request):
    year = request.GET.get("year")
    filename = "dive data export ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_dive_csv(year)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_obs_data(request):
    year = request.GET.get("year")
    filename = "observation data export ({}).csv".format(now().strftime("%Y-%m-%d"))

    response = StreamingHttpResponse(
        streaming_content=(reports.generate_obs_csv(year)),
        content_type='text/csv',
    )
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


def export_open_data(request):
    if request.GET.get("dataset"):
        filename = "open_data_dataset_{}.csv".format(now().year)
        response = StreamingHttpResponse(
            streaming_content=(reports.generate_od_dataset()),
            content_type='text/csv',
        )
        response['Content-Disposition'] = f'attachment;filename={filename}'

    elif request.GET.get("dictionary"):
        response = reports.generate_od_dictionary()

    else:
        return Http404("bad parameter")

    return response
