import csv
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, DeleteView
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse_lazy
from . import models
from . import forms


class IndexTemplateView(TemplateView):
    template_name = "snowcrab/index.html"


# CRUISE #
##########

class CruiseListView(LoginRequiredMixin, ListView):
    template_name = "snowcrab/cruise_list.html"
    model = models.Cruise


class CruiseDetailView(LoginRequiredMixin, DetailView):
    template_name = "snowcrab/cruise_detail.html"
    model = models.Cruise

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)

        context["editable"] = False

        context['google_api_key'] = settings.GOOGLE_API_KEY

        context['field_list'] = [
            "cruise_number",
            "mission_number",
            "vessel",
            "start_date",
            "end_date",
            "chief_scientist",
            "remarks",
            "season",
        ]

        return context


class CruiseUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "snowcrab/cruise_form.html"
    model = models.Cruise
    form_class = forms.CruiseForm
    login_url = '/accounts/login_required/'

    def get_success_url(self, **kwargs):
        return reverse_lazy("crab:cruise_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)

        context["editable"] = True
        return context


# SETS #
########

class SetDetailView(LoginRequiredMixin, DetailView):
    template_name = "snowcrab/set_detail.html"
    model = models.Set

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)

        context['field_list_1'] = [
            'set_name',
            'set_number',
            'year',
            'month',
            'day',
            'zone',
            'valid',
        ]
        context['field_list_2'] = [
            'latitude_start_logbook',
            'latitude_end_logbook',
            'longitude_start_logbook',
            'longitude_end_logbook',
            'latitude_start',
            'latitude_end',
            'longitude_start',
            'longitude_end',
        ]
        context['field_list_3'] = [
            'start_time_logbook',
            'end_time_logbook',
            'start_time',
            'end_time',
        ]
        context['field_list_4'] = [
            'depth_logbook',
            'bottom_temperature_logbook',
            'warp_logbook',
            'swept_area',
            'swept_area_method',
            'comment',
        ]

        return context

#
# # BOTTLES #
# ###########
#
# class BottleListView(ListView):
#     template_name = "oceanography/_set_list.html"
#
#     def get_queryset(self):
#         return models.Bottle.objects.filter(mission = self.kwargs["mission"])
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#
#         context["mission"] = models.Mission.objects.get(id = self.kwargs["mission"])
#         context["bottle"] = models.Bottle.objects.first()
#         return context
#
# class BottleDetailView(UpdateView):
#     template_name = "oceanography/bottle_form.html"
#     model = models.Bottle
#     form_class = forms.BottleForm
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = False
#         return context
#
#
# class BottleUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = "oceanography/bottle_form.html"
#     model = models.Bottle
#     form_class = forms.BottleForm
#     login_url = '/accounts/login_required/'
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("oceanography:bottle_detail", kwargs={"pk":self.object.id})
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = True
#         return context
#
#
# # CSVs #
# ########
# def export_mission_csv(request, pk):
#     # create instance of mission:
#     m = models.Mission.objects.get(pk=pk)
#
#     # Create the HttpResponse object with the appropriate CSV header.
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(slugify(m.mission_number))
#
#     writer = csv.writer(response)
#
#
#     # write the header information
#     writer.writerow(['mission_name', m.mission_name])
#     writer.writerow(['mission_number', m.mission_number])
#     writer.writerow(['vessel_name', m.vessel_name])
#     writer.writerow(['chief_scientist', m.chief_scientist])
#     writer.writerow(['samplers', m.samplers])
#     writer.writerow(['start_date (yyyy-mm-dd)', m.start_date.strftime('%Y-%m-%d')])
#     writer.writerow(['end_date (yyyy-mm-dd)', m.end_date.strftime('%Y-%m-%d')])
#     writer.writerow(['probe', m.probe])
#     writer.writerow(['area_of_operation', m.area_of_operation])
#     writer.writerow(['notes', m.notes])
#     writer.writerow(['timezone', "UTC"])
#
#     # write the header for the bottle table
#     writer.writerow(["",])
#     writer.writerow([
#     "bottle_uid",
#     "station",
#     "set",
#     "event",
#     "date_yyyy_mm_dd",
#     "time_hh_mm",
#     "sounding_m",
#     "bottle_depth_m",
#     "temp_c",
#     "sal_ppt",
#     "ph",
#     "lat_DDdd",
#     "long_DDdd",
#     "ctd_filename",
#     "samples_collected",
#     "remarks",])
#
#     my_date = ""
#     my_time = ""
#     for b in m.bottles.all():
#         try:
#             my_date = b.date_time_UTC.strftime('%Y-%m-%d')
#             my_time = b.date_time_UTC.strftime('%H:%M')
#         except Exception as e:
#             print(e)
#             my_date = None
#             my_time = None
#
#         writer.writerow(
#         [
#         b.bottle_uid,
#         b.station,
#         b.set,
#         b.event,
#         my_date,
#         my_time,
#         b.sounding_m,
#         b.bottle_depth_m,
#         b.temp_c,
#         b.sal_ppt,
#         b.ph,
#         b.lat_DDdd,
#         b.long_DDdd,
#         b.ctd_filename,
#         b.samples_collected,
#         b.remarks,])
#
#     return response
#
#
# # FILES #
# #########
#
# class FileCreateView(CreateView):
#     template_name = "oceanography/file_form.html"
#     model = models.File
#     form_class = forms.FileForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse_lazy("oceanography:mission_detail", kwargs={"pk":object.mission.id}))
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = True
#         return context
#
#     def get_initial(self):
#         mission = models.Mission.objects.get(pk=self.kwargs['mission'])
#         return {'mission': mission}
#
#
# class FileDetailView(UpdateView):
#     template_name = "oceanography/file_form.html"
#     model = models.File
#     form_class = forms.FileForm
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = False
#         return context
#
#
# class FileUpdateView(UpdateView):
#     template_name = "oceanography/file_form.html"
#     model = models.File
#     form_class = forms.FileForm
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("oceanography:mission_detail", kwargs={"pk":self.object.mission.id})
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = True
#         return context
#
# class FileDeleteView(DeleteView):
#     template_name = "oceanography/file_confirm_delete.html"
#     model = models.File
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("oceanography:mission_detail", kwargs={"pk":self.object.mission.id})
