import requests
import unicodecsv as csv
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count, TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from easy_pdf.views import PDFTemplateView
from django_filters.views import FilterView
from shapely.geometry import Polygon, box

from shared_models import models as shared_models
from . import models
from . import forms
from . import filters
from . import reports
from lib.functions.custom_functions import nz, listrify
from django.utils.encoding import smart_str


# open basic access up to anybody who is logged in
def in_sar_search_group(user):
    if user:
        return user.groups.filter(name='sar_search_access').count() != 0


class SARSearchAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_sar_search_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_sar_search_admin_group(user):
    if user:
        return user.groups.filter(name='sar_search_admin').count() != 0


class SARSearchAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_sar_search_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(SARSearchAccessRequiredMixin, TemplateView):
    template_name = 'sar_search/index.html'


class SARMapTemplateView(SARSearchAccessRequiredMixin, FormView):
    template_name = 'sar_search/sar_map.html'
    form_class = forms.MapForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['records'] = models.Record.objects.all()

        # if there are bounding coords, we look in the box
        if self.kwargs.get("n"):

            bbox = box(
                float(self.kwargs.get("n")),
                float(self.kwargs.get("s")),
                float(self.kwargs.get("e")),
                float(self.kwargs.get("w")),
            )

            species_list = list(set(
                [models.Species.objects.get(pk=obj.record.species.id) for obj in models.RecordPoints.objects.all() if
                 bbox.contains(obj.point)]
            ))
        else:
            species_list = [models.Species.objects.get(pk=obj["record__species"]) for obj in
                            models.RecordPoints.objects.values("record__species").order_by("record__species").distinct()]

        context['spatial_species_list'] = species_list


        # get a list of species without spatial representation
        species_list = []
        for obj in models.Species.objects.all():
            for record in obj.records.all():
                print(record)
                if not record.coords():
                    print(obj)
                    species_list.append(obj)
        context['non_spatial_species_list'] = list(set(species_list))

        return context

    def get_initial(self, *args, **kwargs):
        return {
            "north": self.kwargs.get("n"),
            "south": self.kwargs.get("s"),
            "east": self.kwargs.get("e"),
            "west": self.kwargs.get("w"),
        }

    def form_valid(self, form):
        print(form.cleaned_data)
        return HttpResponseRedirect(reverse("sar_search:map", kwargs={
            "n": form.cleaned_data.get("north"),
            "s": form.cleaned_data.get("south"),
            "e": form.cleaned_data.get("east"),
            "w": form.cleaned_data.get("west"),
        }))


# SPECIES #
###########

class SpeciesListView(SARSearchAccessRequiredMixin, FilterView):
    template_name = "sar_search/species_list.html"
    filterset_class = filters.SpeciesFilter
    queryset = models.Species.objects.annotate(
        search_term=Concat('common_name_eng', 'common_name_fre', 'scientific_name', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_object'] = models.Species.objects.first()
        context["field_list"] = [
            'full_name|Species',
            'scientific_name',
            'taxon',
            'sara_status',
            'cosewic_status',
            'sara_schedule',
            # 'province_range',
            # 'tsn',
        ]
        return context


class SpeciesDetailView(SARSearchAccessRequiredMixin, DetailView):
    model = models.Species

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        context["field_list"] = [
            'common_name_eng',
            'common_name_fre',
            'scientific_name',
            'population_eng',
            'population_fre',
            'tsn',
            'taxon',
            'sara_status',
            'cosewic_status',
            'sara_schedule',
            'province_range',
            'notes',
        ]

        context["record_field_list"] = [
            'name',
            'counties',
            'record_type',
            # 'source',
            'date_last_modified',
        ]

        return context


class SpeciesUpdateView(SARSearchAdminRequiredMixin, UpdateView):
    model = models.Species

    form_class = forms.SpeciesForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class SpeciesCreateView(SARSearchAdminRequiredMixin, CreateView):
    model = models.Species

    form_class = forms.SpeciesForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class SpeciesDeleteView(SARSearchAdminRequiredMixin, DeleteView):
    model = models.Species
    permission_required = "__all__"
    success_url = reverse_lazy('sar_search:species_list')
    success_message = 'The species was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# RANGE #
#########

class RecordUpdateView(SARSearchAdminRequiredMixin, UpdateView):
    model = models.Record
    form_class = forms.RecordForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("sar_search:record_detail", kwargs={"pk": my_object.id}))


class RecordCreateView(SARSearchAdminRequiredMixin, CreateView):
    model = models.Record

    form_class = forms.RecordForm

    def get_initial(self):
        return {'species': self.kwargs.get("species")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get("species"):
            species = models.Species.objects.get(pk=self.kwargs["species"])
            context['species'] = species
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("sar_search:record_detail", kwargs={"pk": my_object.id}))


class RecordDetailView(SARSearchAdminRequiredMixin, DetailView):
    model = models.Record

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        field_list = [
            'name',
            'counties',
            'record_type',
            'source',
            'date_last_modified',
        ]
        context['field_list'] = field_list

        return context


class RecordDeleteView(SARSearchAdminRequiredMixin, DeleteView):
    model = models.Record
    success_message = 'The record was successfully deleted!'

    def get_success_url(self):
        return reverse_lazy("sar_search:species_detail", kwargs={"pk": self.object.species.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def manage_coords(request, record):
    qs = models.RecordPoints.objects.filter(record=record)
    my_record = models.Record.objects.get(pk=record)
    if request.method == 'POST':
        formset = forms.CoordFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "coords have been successfully updated")
            return HttpResponseRedirect(reverse("sar_search:manage_coords", kwargs={"record": record}))
    else:
        print(my_record.record_type)
        if my_record.record_type == 1 and my_record.points.count() >= 1:
            formset = forms.CoordFormSetNoExtra(
                queryset=qs,
                initial=[{"record": record}],
            )
        else:
            formset = forms.CoordFormSet(
                queryset=qs,
                initial=[{"record": record}],
            )
    context = {}
    context['title'] = "Manage Record Coordinates"
    context['formset'] = formset
    context["record"] = my_record
    context["my_object"] = models.RecordPoints.objects.first()
    context["field_list"] = [
        'name',
        'latitude_n',
        'longitude_w',
    ]
    return render(request, 'sar_search/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def delete_coord(request, pk):
    my_obj = models.RecordPoints.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("sar_search:manage_coords", kwargs={"record": my_obj.record.id}))


class RecordImportFileView(SARSearchAdminRequiredMixin, UpdateView):
    model = models.Species
    fields = ["temp_file", ]
    template_name = 'sar_search/points_file_import_form.html'

    def form_valid(self, form):
        my_object = form.save()
        # now we need to do some magic with the file...

        # load the file
        url = self.request.META.get("HTTP_ORIGIN") + my_object.temp_file.url
        r = requests.get(url)
        # print(r.text.splitlines())
        csv_reader = csv.DictReader(r.iter_lines())

        for row in csv_reader:
            # OrderedDict([('record_name', 'St. John River'), ('site_name', '1'), ('site_lat', '46.302'), ('site_long', '-67.5327'), ('source', 'Environment Canada. 2013. Recovery Strategy for the Cobblestone Tiger Beetle (Cicindela marginipennis) in Canada. Species at Risk Act Recovery Strategy Series. Environment Canada, Ottawa. v + 18 pp.')])
            if row["type"] == "polygon":
                my_type = 3
            elif row["type"] == "line" or row["type"] == "polyline":
                my_type = 2
            else:
                my_type = 1

            my_record, created = models.Record.objects.get_or_create(
                species=my_object,
                name=row["record_name"],
                record_type=my_type,
                source=row["record_source"],
            )

            if row["site_lat"] and row["site_long"]:
                my_new_point = models.RecordPoints.objects.create(
                    record=my_record,
                    name=row["site_name"],
                    latitude_n=float(row["site_lat"]),
                    longitude_w=float(row["site_long"]),
                )

        # clear the file in my object
        my_object.temp_file = None
        my_object.save()
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))


# SETTINGS #
############
@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def manage_taxa(request):
    qs = models.Taxon.objects.all()
    if request.method == 'POST':
        formset = forms.TaxonFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Taxa have been successfully updated")
            return HttpResponseRedirect(reverse("sar_search:manage_taxa"))
    else:
        formset = forms.TaxonFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Taxa"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'code',
        'name',
        'nom',
    ]
    return render(request, 'sar_search/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def delete_taxon(request, pk):
    my_obj = models.Taxon.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("sar_search:manage_taxa"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def manage_statuses(request):
    qs = models.SpeciesStatus.objects.all()
    if request.method == 'POST':
        formset = forms.SpeciesStatusFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Species status has been successfully updated")
            return HttpResponseRedirect(reverse("sar_search:manage_statuses"))
    else:
        formset = forms.SpeciesStatusFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Species Statuses"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'code',
        'name',
        'nom',
        'description_eng',
        'description_fre',
    ]
    return render(request, 'sar_search/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def delete_status(request, pk):
    my_obj = models.SpeciesStatus.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("sar_search:manage_statuses"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def manage_schedules(request):
    qs = models.SARASchedule.objects.all()
    if request.method == 'POST':
        formset = forms.SARAScheduleFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "schedules have been successfully updated")
            return HttpResponseRedirect(reverse("sar_search:manage_schedules"))
    else:
        formset = forms.SARAScheduleFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage SARA Schedules"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'description_eng',
        'description_fre',
    ]
    return render(request, 'sar_search/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def delete_schedule(request, pk):
    my_obj = models.SARASchedule.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("sar_search:manage_schedules"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def manage_counties(request):
    qs = models.County.objects.all()
    if request.method == 'POST':
        formset = forms.CountyFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "counties have been successfully updated")
            return HttpResponseRedirect(reverse("sar_search:manage_counties"))
    else:
        formset = forms.CountyFormSet(
            queryset=qs)
    context = {}
    context['title'] = "Manage Counties"
    context['formset'] = formset
    context["my_object"] = qs.first()
    context["field_list"] = [
        'code',
        'name',
        'nom',
        'province',
    ]
    return render(request, 'sar_search/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_sar_search_admin_group, login_url='/accounts/denied/')
def delete_county(request, pk):
    my_obj = models.SARASchedule.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("sar_search:manage_counties"))
