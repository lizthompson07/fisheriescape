import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.views.generic import FormView

from shared_models.views import CommonFormsetView, CommonHardDeleteView, CommonTemplateView, CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDetailView, CommonDeleteView, CommonPopoutUpdateView, CommonPopoutCreateView, CommonPopoutDeleteView
from grais import filters
from grais import forms
from grais import models
from grais import reports
from grais.mixins import GraisAccessRequiredMixin, GraisAdminRequiredMixin, GraisCRUDRequiredMixin
from grais.utils import is_grais_admin


# INCIDENTAL REPORT #
#####################

class ReportListView(GraisAccessRequiredMixin, CommonFilterView):
    filterset_class = filters.ReportFilter
    template_name = "grais/scratch/report_list.html"


class ReportUpdateView(GraisAccessRequiredMixin, CommonUpdateView):
    model = models.IncidentalReport
    form_class = forms.ReportForm
    template_name = "grais/scratch/report_form.html"

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ReportCreateView(GraisAccessRequiredMixin, CommonCreateView):
    model = models.IncidentalReport
    form_class = forms.ReportForm
    template_name = "grais/report_form.html"

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ReportDetailView(GraisAccessRequiredMixin, CommonDetailView):
    model = models.IncidentalReport

    template_name = "grais/report_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["field_list"] = [
            "report_date",
            "requestor_name",
            "report_source",
            "language_of_report",
            "call_answered_by",
            "call_returned_by",
            "location_description",
            "latitude_n",
            "longitude_w",
            "specimens_retained",
            "sighting_description",
            "identified_by",
            "date_of_occurrence",
            "observation_type",
            "phone1",
            "phone2",
            "email",
            "notes",
            # "date_last_modified",
            # "last_modified_by",
        ]

        # get a list of species
        species_list = []
        for obj in models.Species.objects.all():
            url = reverse("grais:report_species_add", kwargs={"report": self.object.id, "species": obj.id}),
            html_insert = '<a class="add-btn btn btn-outline-dark" href="#" target-url="{}"> <img src="{}" alt=""></a><span style="margin-left: 10px;">{} / <em>{}</em> / {}</span>'.format(
                url[0],
                static("admin/img/icon-addlink.svg"),
                obj.common_name,
                obj.scientific_name,
                obj.abbrev
            )
            species_list.append(html_insert)
        context['species_list'] = species_list
        return context


class ReportDeleteView(GraisAccessRequiredMixin, CommonDeleteView):
    model = models.IncidentalReport
    success_url = reverse_lazy('grais:report_list')
    success_message = 'The report was successfully deleted!'
    template_name = "grais/report_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


def report_species_observation_delete(request, report, species):
    report = models.IncidentalReport.objects.get(pk=report)
    species = models.Species.objects.get(pk=species)
    report.species.remove(species)
    messages.success(request, "The species has been successfully removed from this report.")
    return HttpResponseRedirect(reverse_lazy("grais:report_detail", kwargs={"pk": report.id}))


def report_species_observation_add(request, report, species):
    report = models.IncidentalReport.objects.get(pk=report)
    species = models.Species.objects.get(pk=species)
    report.species.add(species)
    return HttpResponseRedirect(reverse_lazy("grais:report_detail", kwargs={"pk": report.id}))


# FOLLOWUP #
############

class FollowUpUpdateView(GraisAccessRequiredMixin, CommonUpdateView):
    model = models.FollowUp
    form_class = forms.FollowUpForm
    template_name = 'grais/followup_form_popout.html'
    success_url = reverse_lazy("grais:close_me")


class FollowUpCreateView(GraisAccessRequiredMixin, CommonCreateView):
    model = models.FollowUp
    form_class = forms.FollowUpForm
    template_name = 'grais/followup_form_popout.html'
    success_url = reverse_lazy("grais:close_me")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = models.IncidentalReport.objects.get(pk=self.kwargs["report"])
        return context

    def get_initial(self):
        report = models.IncidentalReport.objects.get(pk=self.kwargs["report"])
        return {
            "incidental_report": report,
            "author": self.request.user
        }


@login_required(login_url='/accounts/login/')
@user_passes_test(is_grais_admin, login_url='/accounts/denied/')
def follow_up_delete(request, pk):
    followup = models.FollowUp.objects.get(pk=pk)
    followup.delete()
    messages.success(request, "The followup has been successfully deleted.")
    return HttpResponseRedirect(reverse_lazy("grais:report_detail", kwargs={"pk": followup.incidental_report_id}))
#
#
# # ESTUARY #
# ###########
#
# class EstuaryListView(GraisAccessRequiredMixin, FilterView):
#     filterset_class = filters.EstuaryFilter
#     template_name = "grais/estuary_list.html"
#
#
# class EstuaryUpdateView(GraisAdminRequiredMixin, UpdateView):
#     # permission_required = "__all__"
#     raise_exception = True
#
#     model = models.Estuary
#     form_class = forms.EstuaryForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class EstuaryCreateView(GraisAdminRequiredMixin, CreateView):
#     model = models.Estuary
#
#     form_class = forms.EstuaryForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class EstuaryDetailView(GraisAccessRequiredMixin, DetailView):
#     model = models.Estuary
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['google_api_key'] = settings.GOOGLE_API_KEY
#
#         field_list = [
#             "id",
#             "name",
#             "province",
#             "description",
#         ]
#         context['field_list'] = field_list
#
#         site_list = [[site.code, site.latitude_n, site.longitude_w] for site in self.object.sites.all() if
#                      site.latitude_n and site.longitude_w]
#         context['site_list'] = site_list
#
#         return context
#
#
# class EstuaryDeleteView(GraisAdminRequiredMixin, DeleteView):
#     model = models.Estuary
#     success_url = reverse_lazy('grais:estuary_list')
#     success_message = 'The sstuary was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#
# # SITE #
# ########
#
# class SiteUpdateView(GraisAdminRequiredMixin, UpdateView):
#     # permission_required = "__all__"
#     raise_exception = True
#
#     model = models.Site
#     form_class = forms.SiteForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#     def get_success_url(self):
#         return reverse_lazy('grais:estuary_detail', kwargs={'pk': self.object.estuary.id})
#
#
# class SiteCreateView(GraisAdminRequiredMixin, CreateView):
#     model = models.Site
#
#     form_class = forms.SiteForm
#
#     def get_initial(self):
#         return {
#             'estuary': self.kwargs['estuary'],
#             'last_modified_by': self.request.user,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['estuary'] = models.Estuary.objects.get(pk=self.kwargs['estuary'])
#         except KeyError:
#             pass
#         return context
#
#     def get_success_url(self):
#         return reverse_lazy('grais:estuary_detail', kwargs={'pk': self.object.estuary.id})
#
#
# class SiteDetailView(GraisAccessRequiredMixin, DetailView):
#     model = models.Site
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         field_list = [
#             'estuary',
#             'code',
#             'name',
#             'latitude_n',
#             'longitude_w',
#             'description',
#         ]
#         context['field_list'] = field_list
#         return context
#
#
# class SiteDeleteView(GraisAdminRequiredMixin, DeleteView):
#     model = models.Site
#     success_url = reverse_lazy('grais:site_list')
#     success_message = 'The site was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:estuary_detail', kwargs={'pk': self.object.estuary.id})
#
#
# # SAMPLE #
# ##########
# class GCSampleListView(GraisAccessRequiredMixin, FilterView):
#     filterset_class = filters.GCSampleFilter
#     template_name = "grais/gcsample_list.html"
#     model = models.GCSample
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["my_object"] = models.GCSample.objects.first()
#         context["field_list"] = [
#             'season',
#             'site',
#             'traps_set|Traps set',
#             'traps_fished|Traps fished',
#         ]
#         return context
#
#
# class GCSampleDetailView(GraisAccessRequiredMixin, DetailView):
#     model = models.GCSample
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['google_api_key'] = settings.GOOGLE_API_KEY
#         context["field_list"] = [
#             'site',
#             'traps_set',
#             'traps_fished',
#             'samplers',
#             'eelgrass_assessed',
#             'eelgrass_percent_coverage',
#             'vegetation_species',
#             'sediment',
#             'season',
#             'last_modified',
#             'last_modified_by',
#             'notes',
#         ]
#         return context
#
#
# class GCSampleUpdateView(GraisAdminRequiredMixin, UpdateView):
#     model = models.GCSample
#     form_class = forms.GCSampleForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:gcsample_detail", kwargs={"pk": object.id}))
#
#
# class GCSampleCreateView(GraisAdminRequiredMixin, CreateView):
#     model = models.GCSample
#     form_class = forms.GCSampleForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:gcsample_detail", kwargs={"pk": object.id}))
#
#
# class GCSampleDeleteView(GraisAdminRequiredMixin, DeleteView):
#     model = models.GCSample
#     success_url = reverse_lazy('grais:gcsample_list')
#     success_message = 'The sample was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#
# # GC PROBE DATA #
# ##############
#
# class GCProbeMeasurementCreateView(GraisAdminRequiredMixin, CreateView):
#     model = models.GCProbeMeasurement
#     form_class = forms.GCProbeMeasurementForm
#     template_name = 'grais/gcprobe_measurement_form.html'
#
#     def get_initial(self):
#         gcsample = models.GCSample.objects.get(pk=self.kwargs['gcsample'])
#         return {
#             'sample': gcsample,
#             'last_modified_by': self.request.user,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['gcsample'] = models.GCSample.objects.get(pk=self.kwargs["gcsample"])
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:gcprobe_measurement_detail", kwargs={"pk": object.id}))
#
#
# class GCProbeMeasurementDetailView(GraisAdminRequiredMixin, UpdateView):
#     model = models.GCProbeMeasurement
#     form_class = forms.GCProbeMeasurementForm
#     template_name = 'grais/gcprobe_measurement_detail.html'
#
#
# class GCProbeMeasurementUpdateView(GraisAdminRequiredMixin, UpdateView):
#     model = models.GCProbeMeasurement
#     form_class = forms.GCProbeMeasurementForm
#     template_name = 'grais/gcprobe_measurement_form.html'
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:gcprobe_measurement_detail", kwargs={"pk": object.id}))
#
#
# class GCProbeMeasurementDeleteView(GraisAdminRequiredMixin, DeleteView):
#     model = models.GCProbeMeasurement
#     template_name = "grais/gcprobe_measurement_confirm_delete.html"
#     success_message = 'The probe measurement was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:gcsample_detail', kwargs={'pk': self.object.sample.id})
#
#
# # TRAP #
# #########
#
# class TrapCreateView(GraisAdminRequiredMixin, CreateView):
#     model = models.Trap
#     form_class = forms.TrapForm
#
#     def get_initial(self):
#         sample = models.GCSample.objects.get(pk=self.kwargs['gcsample'])
#         return {
#             'sample': sample,
#             'last_modified_by': self.request.user
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['gcsample'] = models.GCSample.objects.get(pk=self.kwargs["gcsample"])
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:trap_detail", kwargs={"pk": object.id}))
#
#
# class TrapDetailView(GraisAccessRequiredMixin, DetailView, FormView):
#     model = models.Trap
#     form_class = forms.TrapSpeciesForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['google_api_key'] = settings.GOOGLE_API_KEY
#         context["field_list"] = [
#             # 'sample',
#             'trap_number',
#             'trap_type',
#             'bait_type',
#             'depth_at_set_m',
#             'latitude_n',
#             'longitude_w',
#             'gps_waypoint',
#             'notes',
#             'total_green_crab_wt_kg',
#         ]
#
#         context["crab_field_list"] = [
#             'species',
#             'width',
#             'sex',
#             'carapace_color',
#             'abdomen_color',
#             'egg_color',
#             'notes',
#         ]
#         context["bycatch_field_list"] = [
#             'species',
#             'count',
#             'notes',
#         ]
#         context["random_catch_object"] = models.Catch.objects.first
#         # get a list of species
#
#         return context
#
#
# class TrapUpdateView(GraisAdminRequiredMixin, UpdateView):
#     model = models.Trap
#     form_class = forms.TrapForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("grais:trap_detail", kwargs={"pk": object.id}))
#
#
# class TrapDeleteView(GraisAdminRequiredMixin, DeleteView):
#     model = models.Trap
#     success_message = 'The trap was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:gcsample_detail', kwargs={'pk': self.object.sample.id})
#
#
# # CATCH #
# #########
#
# class CatchCreateViewPopout(GraisAdminRequiredMixin, FormView):
#     template_name = 'grais/catch_form_popout.html'
#     form_class = forms.NewCatchForm
#     model = models.Catch
#
#     def get_initial(self):
#         my_dict = {}
#         my_trap = models.Trap.objects.get(pk=self.kwargs['trap'])
#         my_species = models.Species.objects.get(pk=self.kwargs['species'])
#         my_dict["species"] = my_species
#         my_dict["trap"] = my_trap
#         # my_dict["last_modified_by"] = self.request.user.id
#
#         # if this is a bycatch sp, let's look up the previous entry
#         if not my_species.green_crab_monitoring:
#             try:
#                 my_catch = models.Catch.objects.get(
#                     species=my_species,
#                     trap=my_trap,
#                 )
#             except models.Catch.DoesNotExist:
#                 pass
#             else:
#                 my_dict["notes"] = my_catch.notes
#                 my_dict["count"] = my_catch.count
#
#         return my_dict
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         my_species = models.Species.objects.get(id=self.kwargs['species'])
#         my_trap = models.Trap.objects.get(id=self.kwargs['trap'])
#         context['species'] = my_species
#         context['trap'] = my_trap
#         return context
#
#     def form_valid(self, form):
#         my_species = models.Species.objects.get(id=self.kwargs['species'])
#         my_trap = models.Trap.objects.get(id=self.kwargs['trap'])
#
#         # if the species is a bycatch species, save all the data as a catch instance
#         if not my_species.green_crab_monitoring:
#             if form.cleaned_data.get("count"):
#                 my_catch, created = models.Catch.objects.get_or_create(
#                     species=my_species,
#                     trap=my_trap,
#                 )
#                 my_catch.count = form.cleaned_data.get("count")
#                 my_catch.notes = form.cleaned_data.get("notes")
#                 my_catch.last_modified_by = self.request.user
#                 my_catch.save()
#
#         # if targeted species, lets create x number of blank entries
#         else:
#             for i in range(0, form.cleaned_data.get("count")):
#                 print("creating catch")
#                 models.Catch.objects.create(
#                     species=my_species,
#                     trap=my_trap,
#                     last_modified_by=self.request.user,
#                 )
#
#         return HttpResponseRedirect(reverse('grais:close_me'))
#
#
# class CatchUpdateViewPopout(GraisAdminRequiredMixin, UpdateView):
#     template_name = 'grais/catch_form_popout.html'
#     form_class = forms.CatchForm
#     model = models.Catch
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user.id}
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(reverse('grais:close_me'))
#
#
# @login_required(login_url='/accounts/login/')
# @user_passes_test(is_grais_admin, login_url='/accounts/denied/')
# def catch_delete(request, pk):
#     my_catch = models.Catch.objects.get(pk=pk)
#     my_catch.delete()
#     messages.success(request, "The catch item has been successfully removed from this trap.")
#     return HttpResponseRedirect(reverse_lazy("grais:trap_detail", kwargs={"pk": my_catch.trap.id}))
#
#
# @login_required(login_url='/accounts/login/')
# @user_passes_test(is_grais_admin, login_url='/accounts/denied/')
# def manage_catch(request, trap, type):
#     qs = models.Catch.objects.filter(trap_id=trap)
#     context = dict()
#     context["my_object"] = qs.first()
#     context["trap"] = qs.first().trap
#
#     if type == "invasive":
#         qs = qs.filter(species__invasive=True, species__green_crab_monitoring=True)
#         crab = True
#     elif type == "noninvasive":
#         qs = qs.filter(species__invasive=False, species__green_crab_monitoring=True)
#         crab = True
#     elif type == "bycatch":
#         qs = qs.filter(species__green_crab_monitoring=False)
#         crab = False
#
#     if crab:
#         context["field_list"] = [
#             'width',
#             'sex',
#             'carapace_color',
#             'abdomen_color',
#             'egg_color',
#             'notes',
#         ]
#     else:
#         context["field_list"] = [
#             'count',
#             'notes',
#         ]
#
#     if request.method == 'POST':
#         formset = forms.CatchFormSet(request.POST, )
#         if formset.is_valid():
#             formset.save()
#             # do something with the formset.cleaned_data
#             messages.success(request, "Items have been successfully updated")
#             return HttpResponseRedirect(reverse("grais:manage_catch", kwargs={"trap": trap, "type": type}))
#     else:
#         formset = forms.CatchFormSet(queryset=qs)
#
#     context['title'] = "Manage Catch"
#     context['formset'] = formset
#     return render(request, 'grais/manage_catch.html', context)
#
#
# #
# # # Bycatch #
# # #########
# #
# # class BycatchCreateViewPopout(GraisAdminRequiredMixin, CreateView):
# #     template_name = 'grais/crab_form_popout.html'
# #     form_class = forms.BycatchForm
# #     model = models.Catch
# #
# #     def get_initial(self):
# #         my_dict = {}
# #         my_dict["trap"] = models.Trap.objects.get(pk=self.kwargs['trap'])
# #         my_dict["species"] = models.Species.objects.get(pk=self.kwargs['species'])
# #         my_dict["last_modified_by"] = self.request.user.id
# #         return my_dict
# #
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         trap = models.Trap.objects.get(id=self.kwargs['trap'])
# #         species = models.Species.objects.get(id=self.kwargs['species'])
# #         context['species'] = species
# #         context['trap'] = trap
# #         return context
# #
# #     def form_valid(self, form):
# #         self.object = form.save()
# #         return HttpResponseRedirect(reverse('grais:close_me'))
# #
# #
# # class BycatchUpdateViewPopout(GraisAdminRequiredMixin, CreateView):
# #     template_name = 'grais/crab_form_popout.html'
# #     form_class = forms.BycatchForm
# #     model = models.Catch
# #
# #     def get_initial(self):
# #         return {'last_modified_by': self.request.user.id}
# #
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         return context
# #
# #     def form_valid(self, form):
# #         self.object = form.save()
# #         return HttpResponseRedirect(reverse('grais:close_me'))
# #
# #
# # @login_required(login_url='/accounts/login/')
# # @user_passes_test(is_grais_admin, login_url='/accounts/denied/')
# # def bycatch_delete(request, pk):
# #     bycatch = models.Catch.objects.get(pk=pk)
# #     bycatch.delete()
# #     messages.success(request, "The bycatch has been successfully removed from this trap.")
# #     return HttpResponseRedirect(reverse_lazy("grais:trap_detail", kwargs={"pk": bycatch.trap.id}))
#
#

# REPORTS #
###########

class ReportSearchFormView(GraisAccessRequiredMixin, FormView):
    template_name = 'grais/report_search.html'
    form_class = forms.ReportSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        species_list = str(form.cleaned_data["species"]).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
        report = int(form.cleaned_data["report"])
        year = form.cleaned_data["year"] if form.cleaned_data["year"] else "None"

        if report == 1:
            return HttpResponseRedirect(reverse("grais:spp_sample_xlsx", kwargs={"species_list": species_list}))
        elif report == 2:
            return HttpResponseRedirect(reverse("grais:od1_report", kwargs={"year": year})) if form.cleaned_data[
                "year"] else HttpResponseRedirect(reverse("grais:od1_report"))
        elif report == 3:
            return HttpResponseRedirect(reverse("grais:od1_dictionary"))
        elif report == 4:
            return HttpResponseRedirect(reverse("grais:od1_wms", kwargs={"year": year, "lang": 1}))
        elif report == 5:
            return HttpResponseRedirect(reverse("grais:od1_wms", kwargs={"year": year, "lang": 2}))
        elif report == 6:
            return HttpResponseRedirect(reverse("grais:gc_cpue_report", kwargs={"year": year}))
        elif report == 7:
            return HttpResponseRedirect(reverse("grais:gc_envr_report", kwargs={"year": year}))
        elif report == 8:
            return HttpResponseRedirect(reverse("grais:gc_site_report"))
        elif report == 9:
            return HttpResponseRedirect(reverse("grais:biofouling_pa_xlsx") + f"?year={year}")
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("grais:report_search"))


def species_sample_spreadsheet_export(request, species_list):
    file_url = reports.generate_species_sample_spreadsheet(species_list)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="grais export {}.xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def biofouling_presence_absence_spreadsheet_export(request):
    year = request.GET["year"] if request.GET["year"] != "None" else None

    file_url = reports.generate_biofouling_pa_spreadsheet(year)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="biofouling presence absence {}.xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def export_open_data_ver1(request, year=None):
    response = reports.generate_open_data_ver_1_report(year)
    return response


def export_open_data_ver1_dictionary(request):
    response = reports.generate_open_data_ver_1_data_dictionary()
    return response


def export_open_data_ver1_wms(request, year, lang):
    response = reports.generate_open_data_ver_1_wms_report(year, lang)
    return response


def export_gc_cpue(request, year):
    file_url = reports.generate_gc_cpue_report(year)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="{} green crab CPUE data.xlsx"'.format(year)
            return response
    raise Http404


def export_gc_envr(request, year):
    file_url = reports.generate_gc_envr_report(year)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="{} green crab environmental data.xlsx"'.format(year)
            return response
    raise Http404


def export_gc_sites(request):
    file_url = reports.generate_gc_sites_report()

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="green crab site descriptions.xlsx"'
            return response
    raise Http404
#
