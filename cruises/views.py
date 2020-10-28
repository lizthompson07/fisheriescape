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

from shared_models.views import CommonFilterView, CommonCreateView, CommonDetailView, CommonTemplateView, CommonUpdateView, \
    CommonPopoutCreateView, CommonPopoutUpdateView, CommonPopoutDeleteView, CommonHardDeleteView, CommonFormsetView, CommonDeleteView
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
        {"name": 'time_period|time_period', "class": "", "width": ""},
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
        'mission_number',
        'mission_name',
        'description',
        'purpose',
        'chief_scientist',
        'samplers',
        'time_period|{}'.format(gettext_lazy("time period")),
        'end_date',
        'probe',
        'area_of_operation',
        'number_of_profiles',
        'meds_id',
        'notes',
        'season',
        'vessel',
        'funding_agency_name',
        'funding_project_title',
        'funding_project_id',
        'research_projects_programs',
        'references',
    ]
    parent_crumb = {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}
    home_url_name = "cruises:index"


class CruiseUpdateView(OceanographyAdminRequiredMixin, CommonUpdateView):
    model = shared_models.Cruise
    form_class = forms.CruiseForm
    template_name = 'cruises/form.html'
    home_url_name = "cruises:index"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}


class CruiseDeleteView(OceanographyAdminRequiredMixin, CommonDeleteView):
    model = shared_models.Cruise
    template_name = 'cruises/confirm_delete.html'
    home_url_name = "cruises:index"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}


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

class FileCreateView(OceanographyAccessRequiredMixin, CommonPopoutCreateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True

    def get_initial(self):
        cruise = shared_models.Cruise.objects.get(pk=self.kwargs['cruise'])
        return {'cruise': cruise}


class FileUpdateView(OceanographyAdminRequiredMixin, CommonPopoutUpdateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True


class FileDeleteView(OceanographyAdminRequiredMixin, CommonPopoutDeleteView):
    model = models.File


# INSTRUMENT #
##############

class InstrumentCreateView(OceanographyAccessRequiredMixin, CommonPopoutCreateView):
    model = models.Instrument
    form_class = forms.InstrumentForm

    def get_initial(self):
        cruise = shared_models.Cruise.objects.get(pk=self.kwargs['cruise'])
        return {'cruise': cruise}


class InstrumentUpdateView(OceanographyAdminRequiredMixin, CommonPopoutUpdateView):
    model = models.Instrument
    form_class = forms.InstrumentForm


class InstrumentDeleteView(OceanographyAdminRequiredMixin, CommonPopoutDeleteView):
    model = models.Instrument


# SETTINGS #
############

class VesselFormsetView(OceanographyAdminRequiredMixin, CommonFormsetView):
    template_name = 'cruises/formset.html'
    h1 = "Manage Vessels"
    queryset = shared_models.Vessel.objects.all()
    formset_class = forms.VesselFormset
    success_url_name = "cruises:manage_vessels"
    home_url_name = "cruises:index"
    delete_url_name = "cruises:delete_vessel"
    container_class = "container-fluid"


class VesselHardDeleteView(OceanographyAdminRequiredMixin, CommonHardDeleteView):
    model = shared_models.Vessel
    success_url = reverse_lazy("cruises:manage_vessels")


class InstituteFormsetView(OceanographyAdminRequiredMixin, CommonFormsetView):
    template_name = 'cruises/formset.html'
    h1 = "Manage Institutes"
    queryset = shared_models.Institute.objects.all()
    formset_class = forms.InstituteFormset
    success_url_name = "cruises:manage_institutes"
    home_url_name = "cruises:index"
    delete_url_name = "cruises:delete_institute"
    container_class = "container-fluid"


class InstituteHardDeleteView(OceanographyAdminRequiredMixin, CommonHardDeleteView):
    model = shared_models.Institute
    success_url = reverse_lazy("cruises:manage_institutes")
