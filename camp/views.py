import csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView,  UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView

from django_filters.views import FilterView
from . import models
from . import forms
from . import filters
from lib.functions.nz import nz




def not_in_camp_group(user):
    if user:
        return user.groups.filter(name='camp_access').count() != 0
#
@login_required(login_url = '/accounts/login_required/')
@user_passes_test(not_in_camp_group, login_url='/accounts/denied/')
def index(request):
    return render(request, 'camp/index.html')

class SearchFormView(LoginRequiredMixin, FormView):
    template_name = 'camp/sample_search.html'
    login_url = '/accounts/login_required/'
    form_class = forms.SearchForm

    # def get_initial(self):
    #     return {'year':timezone.now().year-1}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_list = []
        for obj in models.Station.objects.all():
            station_list.append({"site":obj.site_id,"val":obj.id,"text":obj.name})

        context["station_list"] = station_list
        return context

    def form_valid(self, form):
        year = form.cleaned_data["year"]
        month = form.cleaned_data["month"]
        site = nz(form.cleaned_data["site"],None)
        station = nz(form.cleaned_data["station"],None)
        species = nz(form.cleaned_data["species"],None)

        # check to see how many results will be returned
        qs = models.Sample.objects.all()
        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        if station:
            qs = qs.filter(station=station)
        if site and not station:
            qs = qs.filter(station__site=site)
        if species:
            qs = qs.filter(sample_spp__species=species)
        
        if qs.count() < 1000:
            return HttpResponseRedirect(reverse("camp:sample_list", kwargs={"year":year,"month":month,"site":site,"station":station,"species":species,}))
        else:
            messages.error(self.request,"The search requested has returned too many results. Please try again.")
            return HttpResponseRedirect(reverse("camp:search"))



# SAMPLE #
##########

# class CloserTemplateView(TemplateView):
#     template_name = 'grais/close_me.html'


class SampleListView(LoginRequiredMixin, ListView):
    template_name = "camp/sample_list.html"
    login_url = '/accounts/login_required/'

    def get_queryset(self):
        year = nz(self.kwargs["year"])
        month = nz(self.kwargs["month"])
        site = nz(self.kwargs["site"])
        station = nz(self.kwargs["station"])
        species = nz(self.kwargs["species"])

        qs = models.Sample.objects.all()
        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        if station:
            qs = qs.filter(station=station)
        if site and not station:
            qs = qs.filter(station__site=site)
        if species:
            qs = qs.filter(sample_spp__species=species)
        return qs


class SampleFilterView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SampleFilter
    template_name = "camp/sample_filter.html"
    login_url = '/accounts/login_required/'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"SeasonExact": timezone.now().year-1 }
        return kwargs

class SampleDetailView(LoginRequiredMixin, DetailView):
    model = models.Sample
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        context["field_list"] = [
            "station",
            "sample_start_date",
            "sample_end_date",
            "temperature_c",
            "salinity",
            "dissolved_o2",
            "per_sediment_water_cont",
            "per_sediment_organic_cont",
            "mean_sediment_grain_size",
            "silicate",
            "phosphate",
            "nitrates",
            "nitrite",
            "ammonia" ,
        ]

        return context

class SampleUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    login_url = '/accounts/login_required/'


class SampleCreateView(LoginRequiredMixin, CreateView):
    model = models.Sample
    form_class = forms.SampleForm
    login_url = '/accounts/login_required/'


class SampleDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Sample
    success_url = reverse_lazy('camp:sample_filter')
    success_message = 'The sample was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# SITE #
########

class SiteListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SiteFilter
    template_name = "camp/site_list.html"
    login_url = '/accounts/login_required/'

class SiteUpdateView(LoginRequiredMixin,  UpdateView):
    # permission_required = "__all__"
    raise_exception = True
    login_url = '/accounts/login_required/'
    model = models.Site
    form_class = forms.SiteForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SiteCreateView(LoginRequiredMixin, CreateView):
    model = models.Site
    login_url = '/accounts/login_required/'
    form_class = forms.SiteForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SiteDetailView(LoginRequiredMixin, DetailView):
    model = models.Site
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        field_list = [
            "site",
            "code",
            "province",
            "description",
        ]
        context['field_list'] = field_list

        station_list =  []
        for obj in self.object.stations.all():
            if obj.latitude_n and obj.longitude_w:
                station_list.append(
                    [obj.name, obj.latitude_n, obj.longitude_w]
                )
        context['station_list'] = station_list


        return context

class SiteDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Site
    success_url = reverse_lazy('camp:site_list')
    success_message = 'The site was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# STATION #
###########

class StationUpdateView(LoginRequiredMixin,  UpdateView):
    # permission_required = "__all__"
    raise_exception = True
    login_url = '/accounts/login_required/'
    model = models.Station
    form_class = forms.StationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class StationCreateView(LoginRequiredMixin, CreateView):
    model = models.Station
    login_url = '/accounts/login_required/'
    form_class = forms.StationForm

    def get_initial(self):
        return {'site': self.kwargs["site"]}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = models.Site.objects.get(pk=self.kwargs["site"])
        context['site'] = site
        return context


class StationDetailView(LoginRequiredMixin, DetailView):
    model = models.Station
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        field_list = [
            "name",
            "site",
            "station_number",
            "latitude_n",
            "longitude_w",
            "description",
        ]
        context['field_list'] = field_list

        return context

class StationDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Station
    success_message = 'The station was successfully deleted!'

    def get_success_url(self):
        return reverse_lazy("camp:site_detail", kwargs={"pk":self.object.site.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# SPECIES #
###########

class SpeciesListView(LoginRequiredMixin, FilterView):
    template_name = "camp/species_list.html"
    filterset_class = filters.SpeciesFilter
    login_url = '/accounts/login_required/'

class SpeciesDetailView(LoginRequiredMixin, DetailView):
    model = models.Species
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        context["field_list"] = [
            'common_name_eng',
            'common_name_fre',
            'scientific_name',
            'code',
            'tsn',
            'aphia_id',
            'notes',
        ]
        
        # get a list of x,y coords for the species
        locations = []

        # i want a queryset that has [species, station name, lat, lon, count of stn]

        qs = models.SpeciesObservations.objects.filter(species = self.object).values(
            'species_id',
            'sample__station__id',
            'sample__station__name',
            'sample__station__latitude_n',
            'sample__station__longitude_w'
        ).distinct().annotate(dcount=Count('sample__station__id'))

        for obj in qs:
            if obj["sample__station__latitude_n"] and obj["sample__station__longitude_w"]:
                year_last_seen = models.SpeciesObservations.objects.filter(species=self.object.id).filter(sample__station = obj["sample__station__id"]).order_by("-sample__sample_start_date").first().sample.sample_start_date.year
                locations.append(
                    [
                        obj["sample__station__name"],
                        obj["sample__station__latitude_n"],
                        obj["sample__station__longitude_w"],
                        obj["dcount"],
                        year_last_seen,
                    ]
                )

        context["locations"] = locations
        return context


class SpeciesUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Species
    login_url = '/accounts/login_required/'
    form_class = forms.SpeciesForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SpeciesCreateView(LoginRequiredMixin, CreateView):
    model = models.Species
    login_url = '/accounts/login_required/'
    form_class = forms.SpeciesForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SpeciesDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = models.Species
    permission_required = "__all__"
    success_url = reverse_lazy('camp:species_list')
    success_message = 'The species was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)




# # PERSON #
# ##########
#
# class PersonUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.Sampler
#     login_url = '/accounts/login_required/'
#     fields =('__all__')
#     template_name = 'grais/person_form_popout.html'
#
# class PersonCreateView(LoginRequiredMixin, CreateView):
#     model = models.Sampler
#     login_url = '/accounts/login_required/'
#     fields =('__all__')
#     template_name = 'grais/person_form_popout.html'
#
# class PersonDetailView(LoginRequiredMixin, UpdateView):
#     model = models.Sampler
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/person_detail_popout.html'
#     fields =('__all__')
#
#
# # PROBE DATA #
# ##############
#
# class ProbeMeasurementCreateView(LoginRequiredMixin, CreateView):
#     model = models.ProbeMeasurement
#     form_class = forms.ProbeMeasurementForm
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/probe_measurement_form.html'
#
#     def get_initial(self):
#         sample = models.Sample.objects.get(pk=self.kwargs['sample'])
#         return {
#             'sample': sample,
#             'last_modified_by': self.request.user,
#             }
#
#
# class ProbeMeasurementDetailView(LoginRequiredMixin, UpdateView):
#     model = models.ProbeMeasurement
#     form_class = forms.ProbeMeasurementForm
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/probe_measurement_detail.html'
#
# class ProbeMeasurementUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.ProbeMeasurement
#     form_class = forms.ProbeMeasurementForm
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/probe_measurement_form.html'
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class ProbeMeasurementDeleteView(LoginRequiredMixin, DeleteView):
#
#     model = models.ProbeMeasurement
#     template_name = "grais/probe_measurement_confirm_delete.html"
#     success_message = 'The probe measurement was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:sample_detail', kwargs={'pk':self.kwargs['sample']})
#
#
# # LINES #
# #########
#
# class LineCreateView(LoginRequiredMixin, CreateView):
#     model = models.Line
#     form_class = forms.LineCreateForm
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/line_form.html'
#
#     def get_initial(self):
#         sample = models.Sample.objects.get(pk=self.kwargs['sample'])
#         return {
#             'sample': sample,
#             'number_plates':2,
#             'number_petris':3,
#             'last_modified_by': self.request.user
#             }
#
#     def form_valid(self, form):
#         self.object = form.save()
#         petris = form.cleaned_data['number_petris']
#         plates = form.cleaned_data['number_plates']
#         if petris+plates > 0:
#             # create instances of surfaces on the collector lines
#             # create iterable
#             for i in range(petris):
#                 s = models.Surface.objects.create(line=self.object, surface_type = 'pe', label=i+1 )
#                 s.save()
#             for i in range(plates):
#                 s = models.Surface.objects.create(line=self.object, surface_type = 'pl', label=i+1 )
#                 s.save()
#         return HttpResponseRedirect(self.get_success_url())
#
# class LineDetailView(LoginRequiredMixin, DetailView):
#     model = models.Line
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/line_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['google_api_key'] = settings.GOOGLE_API_KEY
#         return context
#
# class LineUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.Line
#     form_class = forms.LineForm
#     login_url = '/accounts/login_required/'
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class LineDeleteView(LoginRequiredMixin, DeleteView):
#
#     model = models.Line
#     template_name = "grais/line_confirm_delete.html"
#     success_message = 'The line was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:sample_detail', kwargs={'pk':self.kwargs['sample']})
#
#
# # COLLECTORS #
# ##############
#
# class CollectorListView(LoginRequiredMixin, ListView):
#     model = models.Collector
#     login_url = '/accounts/login_required/'
#
# class CollectorDetailView(LoginRequiredMixin, UpdateView):
#     model = models.Collector
#     fields = "__all__"
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/collector_detail.html'
#
# class CollectorUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.Collector
#     fields = "__all__"
#     login_url = '/accounts/login_required/'
#     # template_name = 'grais/samplenote_form_popout.html'
#
# class CollectorCreateView(LoginRequiredMixin, CreateView):
#     model = models.Collector
#     fields = "__all__"
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/samplenote_form_popout.html'
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(reverse('grais:close_me'))
#
# class CollectorDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
#     model = models.Collector
#     permission_required = "__all__"
#     success_url = reverse_lazy('grais:collector_list')
#     success_message = 'The collector was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#
# # SURFACES #
# ############
#
# class SurfaceDetailView(LoginRequiredMixin, UpdateView):
#     model = models.Surface
#     form_class = forms.SurfaceImageForm
#     login_url = '/accounts/login_required/'
#     template_name = 'grais/surface_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         surface = self.kwargs['pk']
#         surface_spp = models.Surface.objects.get(id=surface).surface_spp.all()
#         total_coverage = 0
#         for sp in surface_spp:
#             total_coverage += sp.percent_coverage
#
#         context['total_coverage']= total_coverage
#         return context
#
# class SurfaceUpdateView(LoginRequiredMixin, UpdateView):
#     model = models.Surface
#     form_class = forms.SurfaceForm
#     login_url = '/accounts/login_required/'
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
# class SurfaceCreateView(LoginRequiredMixin, CreateView):
#     model = models.Surface
#     form_class = forms.SurfaceForm
#     login_url = '/accounts/login_required/'
#
#     def get_initial(self):
#         line = models.Line.objects.get(pk=self.kwargs['line'])
#         return {
#             'line': line,
#             'last_modified_by': self.request.user
#         }
#
# class SurfaceDeleteView(LoginRequiredMixin, DeleteView):
#
#     model = models.Surface
#     template_name = "grais/surface_confirm_delete.html"
#     success_message = 'The surface was successfully deleted!'
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse_lazy('grais:line_detail', kwargs={'sample':self.kwargs['sample'],'pk':self.kwargs['line']})
#
#
#
# # SURFACE SPECIES #
# class SurfaceSpeciesCreatePopoutView(LoginRequiredMixin,CreateView):
#     model = models.SurfaceSpecies
#     template_name ='grais/surface_species_form_popout.html'
#     login_url = '/accounts/login_required/'
#     form_class = forms.SurfaceSpeciesForm
#
#     def get_initial(self):
#         surface = models.Surface.objects.get(pk=self.kwargs['surface'])
#         species = models.Species.objects.get(pk=self.kwargs['species'])
#         return {
#             'surface': surface,
#             'species': species,
#             'last_modified_by': self.request.user,
#             }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         species = self.kwargs['species']
#         species = models.Species.objects.get(id=species)
#         context['species']= species
#         return context
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(reverse('grais:close_me'))
#
# class SurfaceSpeciesUpdatePopoutView(LoginRequiredMixin,UpdateView):
#     model = models.SurfaceSpecies
#     template_name ='grais/surface_species_form_popout.html'
#     form_class = forms.SurfaceSpeciesForm
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
#
# class SurfaceSpeciesDetailPopoutView(LoginRequiredMixin,UpdateView):
#     model = models.SurfaceSpecies
#     template_name ='grais/surface_species_detail_popout.html'
#     form_class = forms.SurfaceSpeciesForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         try:
#             extra_context = {'temp_msg':self.request.session['temp_msg']}
#             context.update(extra_context)
#             del self.request.session['temp_msg']
#         except Exception as e:
#             print("type error: " + str(e))
#             # pass
#
#         return context
#
# class SpeciesInsertListView(FilterView):
#     filterset_class = filters.SpeciesFilter
#     template_name = "grais/surface_species_insert.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         surface = self.kwargs['surface']
#         my_surface = models.Surface.objects.get(id=surface)
#         context['surface']= my_surface
#         surface_spp = models.Surface.objects.get(id=surface).surface_spp.all()
#         context['surface_spp']= surface_spp
#         total_coverage = 0
#         for sp in surface_spp:
#             total_coverage += sp.percent_coverage
#
#         context['total_coverage']= total_coverage
#
#         # confirmation message for when a new species is added to the list
#         try:
#             extra_context = {'temp_msg':self.request.session['temp_msg']}
#             context.update(extra_context)
#             del self.request.session['temp_msg']
#         except Exception as e:
#             print("type error: " + str(e))
#             # pass
#
#         return context
#
#
#     # def get_filterset_kwargs(self, filterset_class):
#     #     kwargs = super().get_filterset_kwargs(filterset_class)
#     #     if kwargs["data"] is None:
#     #         kwargs["data"] = {"biofouling": True }
#     #     return kwargs
#
# class SurfaceSpeciesDeletePopoutView(LoginRequiredMixin,DeleteView):
#     model = models.SurfaceSpecies
#     template_name ='grais/surface_species_confirm_delete.html'
#
#     def get_success_url(self):
#         return reverse_lazy('grais:close_me')
#
#
# # CSVs #
# ########
#
# def export_csv_1(request):
#     # Create the HttpResponse object with the appropriate CSV header.
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
#
#     writer = csv.writer(response)
#     writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
#     writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
#
#     return response
#
#
# # INCIDENTAL REPORT #
# #####################
#
# class ReportListView(LoginRequiredMixin, FilterView):
#     filterset_class = filters.ReportFilter
#     template_name = "grais/report_list.html"
#     login_url = '/accounts/login_required/'
#
#
# class ReportUpdateView(LoginRequiredMixin,  UpdateView):
#     login_url = '/accounts/login_required/'
#     model = models.IncidentalReport
#     form_class = forms.StationForm
#     template_name = "grais/report_form.html"
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class ReportCreateView(LoginRequiredMixin, CreateView):
#     model = models.IncidentalReport
#     login_url = '/accounts/login_required/'
#     form_class = forms.ReportForm
#     template_name = "grais/report_form.html"
#
#     def get_initial(self):
#         return {'last_modified_by': self.request.user}
#
#
# class ReportDetailView(LoginRequiredMixin, DetailView):
#     model = models.IncidentalReport
#     login_url = '/accounts/login_required/'
#     template_name = "grais/report_detail.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['google_api_key'] = settings.GOOGLE_API_KEY
#
#         field_list = [
#             "report_date",
#             "reporter_name",
#             "report_type",
#             "language_of_report",
#             "call_answered_by",
#             "call_returned_by",
#             "location_description",
#             "latitude_n",
#             "longitude_w",
#             "specimens_retained",
#             "sighting_description",
#             "identified_by",
#             "date_of_occurence",
#             "obvservation_type",
#             "phone",
#             "email",
#             "notes",
#             "date_last_modified",
#             "last_modified_by",
#         ]
#
#         context["field_list"] = field_list
#
#         return context
#
#
# class ReportDeleteView(LoginRequiredMixin, DeleteView):
#     model = models.IncidentalReport
#     success_url = reverse_lazy('grais:report_list')
#     success_message = 'The report was successfully deleted!'
#     template_name = "grais/report_confirm_delete.html"
#
#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_message)
#         return super().delete(request, *args, **kwargs)
#
