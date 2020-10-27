from django.utils.translation import gettext_lazy, gettext
import csv
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, DeleteView
from django.utils.text import slugify
from django.urls import reverse_lazy

from shared_models.views import CommonFilterView, CommonCreateView, CommonDetailView, CommonTemplateView
from . import models
from . import filters
from . import forms
from shared_models import models as shared_models


# open basic access up to anybody who is logged in
def in_cruises_group(user):
    if user.id:
        # return user.groups.filter(name='sar_search_access').count() != 0
        return True


class OceanographyAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return in_cruises_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_cruises_admin_group(user):
    if user:
        return user.groups.filter(name='oceanography_admin').count() != 0


class OceanographyAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_cruises_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(OceanographyAccessRequiredMixin, CommonTemplateView):
    template_name = "cruises/index.html"
    h1 = "Home"

# Cruises #
############

class CruiseListView(OceanographyAccessRequiredMixin, CommonFilterView):
    template_name = "cruises/list.html"
    paginate_by = 50
    filterset_class = filters.CruiseFilter
    queryset = shared_models.Cruise.objects.annotate(
        search_term=Concat('mission_name', 'mission_number', output_field=TextField())).order_by("-start_date", "mission_number")
    field_list = [
        {"name": 'institute', "class": "", "width": ""},
        {"name": 'mission_number', "class": "", "width": ""},
        {"name": 'mission_name', "class": "", "width": ""},
        {"name": 'vessel', "class": "", "width": ""},
        {"name": 'chief_scientist', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
        {"name": 'meds_id', "class": "", "width": ""},
        {"name": 'season', "class": "", "width": ""},
    ]
    new_object_url = reverse_lazy("cruises:cruise_new")
    row_object_url_name = "cruises:cruise_detail"
    home_url_name = "cruises:index"


class CruiseCreateView(OceanographyAdminRequiredMixin, CommonCreateView):
    template_name = 'cruises/form.html'
    model = shared_models.Cruise
    form_class = forms.CruiseForm
    parent_crumb = {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}
    home_url_name = "cruises:index"


class CruiseDetailView(OceanographyAccessRequiredMixin, CommonDetailView):
    template_name = "cruises/cruise_detail.html"
    model = shared_models.Cruise
    field_list = [
        'institute',
        'season',
        'vessel',
        'mission_number',
        'mission_name',
        'description',
        'chief_scientist',
        'samplers',
        'time_period|time period',
        'end_date',
        'probe',
        'area_of_operation',
        'number_of_profiles',
        'meds_id',
        'notes',
    ]
    parent_crumb = {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}
    home_url_name = "cruises:index"


class CruiseUpdateView(OceanographyAdminRequiredMixin, UpdateView):
    model = shared_models.Cruise
    form_class = forms.CruiseForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("cruises:mission_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)

        context["editable"] = True
        return context


# CSVs #
########
def export_mission_csv(request, pk):
    # create instance of mission:
    m = shared_models.Cruise.objects.get(pk=pk)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(slugify(m.mission_number))

    writer = csv.writer(response)

    # write the header information
    writer.writerow(['institute', m.institute])
    writer.writerow(['mission_name', m.mission_name])
    writer.writerow(['mission_number', m.mission_number])
    writer.writerow(['vessel', m.vessel])
    writer.writerow(['chief_scientist', m.chief_scientist])
    writer.writerow(['samplers', m.samplers])
    writer.writerow(['start_date (yyyy-mm-dd)', m.start_date.strftime('%Y-%m-%d')])
    writer.writerow(['end_date (yyyy-mm-dd)', m.end_date.strftime('%Y-%m-%d')])
    writer.writerow(['probe', m.probe])
    writer.writerow(['area_of_operation', m.area_of_operation])
    writer.writerow(['notes', m.notes])
    writer.writerow(['timezone', "UTC"])

    # write the header for the bottle table
    writer.writerow(["", ])
    writer.writerow([
        "bottle_uid",
        "station",
        "set",
        "event",
        "date_yyyy_mm_dd",
        "time_hh_mm",
        "sounding_m",
        "bottle_depth_m",
        "temp_c",
        "salinity",
        "salinity_units",
        "ph",
        "lat_DDdd",
        "long_DDdd",
        "ctd_filename",
        "samples_collected",
        "remarks", ])

    my_date = ""
    my_time = ""
    for b in m.bottles.all():
        try:
            my_date = b.date_time_UTC.strftime('%Y-%m-%d')
            my_time = b.date_time_UTC.strftime('%H:%M')
        except Exception as e:
            print(e)
            my_date = None
            my_time = None

        writer.writerow(
            [
                b.bottle_uid,
                b.station,
                b.set,
                b.event,
                my_date,
                my_time,
                b.sounding_m,
                b.bottle_depth_m,
                b.temp_c,
                b.salinity,
                b.get_sal_units_display(),
                b.ph,
                b.lat_DDdd,
                b.long_DDdd,
                b.ctd_filename,
                b.samples_collected,
                b.remarks, ])

    return response


# FILES #
#########

class FileCreateView(OceanographyAccessRequiredMixin, CreateView):
    template_name = "cruises/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy("cruises:mission_detail", kwargs={"pk": object.mission.id}))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        context["mission"] = shared_models.Cruise.objects.get(pk=self.kwargs.get("mission"))
        return context

    def get_initial(self):
        mission = shared_models.Cruise.objects.get(pk=self.kwargs['mission'])
        return {'mission': mission}


class FileDetailView(OceanographyAccessRequiredMixin, UpdateView):
    template_name = "cruises/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context


class FileUpdateView(OceanographyAdminRequiredMixin, UpdateView):
    template_name = "cruises/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("cruises:mission_detail", kwargs={"pk": self.object.mission.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context


class FileDeleteView(OceanographyAdminRequiredMixin, DeleteView):
    template_name = "cruises/file_confirm_delete.html"
    model = models.File

    def get_success_url(self, **kwargs):
        return reverse_lazy("cruises:mission_detail", kwargs={"pk": self.object.mission.id})
