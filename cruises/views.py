import csv
from copy import deepcopy

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy

from shared_models import models as shared_models
from shared_models.views import CommonFilterView, CommonCreateView, CommonDetailView, CommonTemplateView, CommonUpdateView, \
    CommonPopoutCreateView, CommonPopoutUpdateView, CommonPopoutDeleteView, CommonHardDeleteView, CommonFormsetView, CommonDeleteView
from . import filters
from . import forms
from . import models


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


def can_modify(user, instance):
    if user:
        if in_cruises_admin_group(user):
            return True
        # are we dealing with a cruise:
        cruise = None
        if isinstance(instance, shared_models.Cruise):
            cruise = instance
        elif isinstance(instance, models.Instrument) or isinstance(instance, models.File):
            cruise = instance.cruise
        elif isinstance(instance, models.InstrumentComponent):
            cruise = instance.instrument.cruise

        if cruise:
            if user in cruise.editors.all():
                return True
            if cruise.created_by == user:
                return True
        return False


class OceanographyAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_cruises_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class CanModifyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        if self.kwargs.get("pk"):
            return can_modify(self.request.user, self.get_object())
        else:
            if self.kwargs.get("cruise"):
                cruise = get_object_or_404(shared_models.Cruise, pk = self.kwargs.get("cruise"))
                return can_modify(self.request.user, cruise)

            if self.kwargs.get("instrument"):
                instrument = get_object_or_404(models.Instrument, pk = self.kwargs.get("instrument"))
                return can_modify(self.request.user, instrument)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)
    return my_dict


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


class CruiseCreateView(OceanographyAccessRequiredMixin, CommonCreateView):
    template_name = 'cruises/form.html'
    model = shared_models.Cruise
    form_class = forms.CruiseForm
    parent_crumb = {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}
    home_url_name = "cruises:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context


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
        'metadata',
    ]
    parent_crumb = {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}
    home_url_name = "cruises:index"


class CruiseUpdateView(CanModifyRequiredMixin, CommonUpdateView):
    model = shared_models.Cruise
    form_class = forms.CruiseForm
    template_name = 'cruises/form.html'
    home_url_name = "cruises:index"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context


class CruiseCloneView(OceanographyAccessRequiredMixin, CruiseUpdateView):
    h1 = gettext_lazy("Clone")

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Cruise.objects.get(pk=new_obj.pk)

        new_obj.pk = None
        new_obj.created_by = self.request.user
        new_obj.modified_by = self.request.user
        new_obj.created_at = timezone.now()
        new_obj.save()

        # for each year of old project, clone into new project...
        for old_instrument in old_obj.instruments.all():
            new_instrument = deepcopy(old_instrument)
            new_instrument.cruise = new_obj
            new_instrument.pk = None
            new_instrument.save()

            for old_component in old_instrument.components.all():
                new_component = deepcopy(old_component)
                new_component.instrument = new_instrument
                new_component.pk = None
                new_component.save()

        return HttpResponseRedirect(reverse_lazy("cruises:cruise_detail", kwargs={"pk": new_obj.id}))

    def get_initial(self):
        obj = self.get_object()
        return dict(
            mission_number=obj.mission_number + " CLONED"
        )


class CruiseDeleteView(CanModifyRequiredMixin, CommonDeleteView):
    model = shared_models.Cruise
    template_name = 'cruises/confirm_delete.html'
    home_url_name = "cruises:index"
    success_url = reverse_lazy('cruises:cruise_list')

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

class FileCreateView(CanModifyRequiredMixin, CommonPopoutCreateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True

    def get_initial(self):
        cruise = shared_models.Cruise.objects.get(pk=self.kwargs['cruise'])
        return {'cruise': cruise}


class FileUpdateView(CanModifyRequiredMixin, CommonPopoutUpdateView):
    model = models.File
    form_class = forms.FileForm
    is_multipart_form_data = True


class FileDeleteView(CanModifyRequiredMixin, CommonPopoutDeleteView):
    model = models.File


# Instruments #
############

class InstrumentCreateView(CanModifyRequiredMixin, CommonCreateView):
    template_name = 'cruises/form.html'
    model = models.Instrument
    form_class = forms.InstrumentForm
    home_url_name = "cruises:index"

    def get_initial(self):
        cruise = shared_models.Cruise.objects.get(pk=self.kwargs['cruise'])
        return {'cruise': cruise}

    def get_cruise(self):
        return get_object_or_404(shared_models.Cruise, pk=self.kwargs.get("cruise"))

    def get_parent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_grandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}


class InstrumentDetailView(CanModifyRequiredMixin, CommonDetailView):
    template_name = "cruises/instrument_detail.html"
    model = models.Instrument
    field_list = [
        'name',
        'notes',
    ]
    home_url_name = "cruises:index"

    def get_cruise(self):
        return self.get_object().cruise

    def get_parent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_grandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component_object"] = models.InstrumentComponent.objects.first()
        context["component_field_list"] = [
            "component_type",
            "model_number",
            "serial_number",
            "notes",
        ]

        return context


class InstrumentUpdateView(CanModifyRequiredMixin, CommonUpdateView):
    model = models.Instrument
    form_class = forms.InstrumentForm
    template_name = 'cruises/form.html'
    home_url_name = "cruises:index"

    def get_cruise(self):
        return self.get_object().cruise

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cruises:instrument_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_greatgrandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}


class InstrumentDeleteView(CanModifyRequiredMixin, CommonDeleteView):
    model = models.Instrument
    template_name = 'cruises/confirm_delete.html'
    home_url_name = "cruises:index"
    delete_protection = False

    def get_success_url(self):
        return self.get_grandparent_crumb().get("url")

    def get_cruise(self):
        return self.get_object().cruise

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cruises:instrument_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_greatgrandparent_crumb(self):
        return {"title": gettext_lazy("Cruises"), "url": reverse_lazy("cruises:cruise_list")}


# Instrument component #
########################

class InstrumentComponentCreateView(CanModifyRequiredMixin, CommonCreateView):
    model = models.InstrumentComponent
    template_name = 'cruises/form.html'
    form_class = forms.InstrumentComponentForm
    home_url_name = "index"

    def get_cruise(self):
        return models.Instrument.objects.get(pk=self.kwargs["instrument"]).cruise

    def get_instrument(self):
        return models.Instrument.objects.get(pk=self.kwargs["instrument"])

    def get_parent_crumb(self):
        return {"title": self.get_instrument(),
                "url": reverse_lazy("cruises:instrument_detail", args=[self.get_instrument().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_initial(self):
        return {"instrument": self.get_instrument(), }


class InstrumentComponentUpdateView(CanModifyRequiredMixin, CommonUpdateView):
    model = models.InstrumentComponent
    template_name = 'cruises/form.html'
    form_class = forms.InstrumentComponentForm
    home_url_name = "index"
    grandparent_crumb = {"title": gettext_lazy("Instruments"), "url": reverse_lazy("ocean:instrument_list")}

    def get_cruise(self):
        return self.get_object().instrument.cruise

    def get_instrument(self):
        return self.get_object().instrument

    def get_parent_crumb(self):
        return {"title": self.get_instrument(),
                "url": reverse_lazy("cruises:instrument_detail", args=[self.get_instrument().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}

    def get_delete_url(self):
        return reverse("cruises:component_delete", args=[self.get_object().id])


class InstrumentComponentDeleteView(CanModifyRequiredMixin, CommonDeleteView):
    model = models.InstrumentComponent
    template_name = 'cruises/confirm_delete.html'
    home_url_name = "index"

    def get_cruise(self):
        return self.get_object().instrument.cruise

    def get_instrument(self):
        return self.get_object().instrument

    def get_parent_crumb(self):
        return {"title": self.get_instrument(),
                "url": reverse_lazy("cruises:instrument_detail", args=[self.get_instrument().id])}

    def get_grandparent_crumb(self):
        return {"title": self.get_cruise(), "url": reverse_lazy("cruises:cruise_detail", args=[self.get_cruise().id])}


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


class ComponentTypeFormsetView(OceanographyAdminRequiredMixin, CommonFormsetView):
    template_name = 'cruises/formset.html'
    h1 = "Manage Component Types"
    queryset = models.ComponentType.objects.all()
    formset_class = forms.ComponentTypeFormset
    success_url_name = "cruises:manage_component_types"
    home_url_name = "cruises:index"
    delete_url_name = "cruises:delete_component_type"


class ComponentTypeHardDeleteView(OceanographyAdminRequiredMixin, CommonHardDeleteView):
    model = models.ComponentType
    success_url = reverse_lazy("cruises:manage_component_types")


class HelpTextFormsetView(OceanographyAdminRequiredMixin, CommonFormsetView):
    template_name = 'cruises/formset.html'
    h1 = "Manage Help Texts"
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url_name = "cruises:manage_help_texts"
    home_url_name = "cruises:index"
    delete_url_name = "cruises:delete_help_text"


class HelpTextHardDeleteView(OceanographyAdminRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("cruises:manage_help_texts")
