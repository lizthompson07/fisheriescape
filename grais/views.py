import csv
from django.views.generic import ListView,  UpdateView, DeleteView, CreateView, DetailView, TemplateView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import GroupRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django_filters.views import FilterView
from django.utils import timezone
from . import models
from . import forms
from . import filters

class IndexView(GroupRequiredMixin,TemplateView):
    template_name = 'grais/index.html'
    group_required = [u"grais_access",]
    login_url = '/accounts/login_required/'


class DataFlowTemplateView(TemplateView):
    template_name = 'grais/dataflow.html'


# SAMPLE #
##########
class CloserTemplateView(TemplateView):
    template_name = 'grais/close_me.html'


class SampleListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SampleFilter
    template_name = "grais/sample_list.html"
    login_url = '/accounts/login_required/'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"SeasonSince": timezone.now().year-2 }
        return kwargs

class SampleDetailView(LoginRequiredMixin, DetailView):
    model = models.Sample
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context

class SampleUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sample
    form_class = forms.SampleForm
    login_url = '/accounts/login_required/'

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SampleCreateView(LoginRequiredMixin, CreateView):
    model = models.Sample
    form_class = forms.SampleForm
    login_url = '/accounts/login_required/'

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SampleDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Sample
    success_url = reverse_lazy('grais:sample_list')
    success_message = 'The sample was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# STATION #
###########

class StationListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.StationFilter
    template_name = "grais/station_list.html"
    login_url = '/accounts/login_required/'

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
        return {'last_modified_by': self.request.user}

class StationDetailView(LoginRequiredMixin, UpdateView):
    model = models.Station
    login_url = '/accounts/login_required/'
    fields =('__all__')
    template_name = 'grais/station_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context

class StationDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Station
    success_url = reverse_lazy('grais:station_list')
    success_message = 'The station was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PERSON #
##########

class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sampler
    login_url = '/accounts/login_required/'
    fields =('__all__')
    template_name = 'grais/person_form_popout.html'

class PersonCreateView(LoginRequiredMixin, CreateView):
    model = models.Sampler
    login_url = '/accounts/login_required/'
    fields =('__all__')
    template_name = 'grais/person_form_popout.html'

class PersonDetailView(LoginRequiredMixin, UpdateView):
    model = models.Sampler
    login_url = '/accounts/login_required/'
    template_name = 'grais/person_detail_popout.html'
    fields =('__all__')


# PROBE DATA #
##############

class ProbeMeasurementCreateView(LoginRequiredMixin, CreateView):
    model = models.ProbeMeasurement
    form_class = forms.ProbeMeasurementForm
    login_url = '/accounts/login_required/'
    template_name = 'grais/probe_measurement_form.html'

    def get_initial(self):
        sample = models.Sample.objects.get(pk=self.kwargs['sample'])
        return {
            'sample': sample,
            'last_modified_by': self.request.user,
            }


class ProbeMeasurementDetailView(LoginRequiredMixin, UpdateView):
    model = models.ProbeMeasurement
    form_class = forms.ProbeMeasurementForm
    login_url = '/accounts/login_required/'
    template_name = 'grais/probe_measurement_detail.html'

class ProbeMeasurementUpdateView(LoginRequiredMixin, UpdateView):
    model = models.ProbeMeasurement
    form_class = forms.ProbeMeasurementForm
    login_url = '/accounts/login_required/'
    template_name = 'grais/probe_measurement_form.html'

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProbeMeasurementDeleteView(LoginRequiredMixin, DeleteView):

    model = models.ProbeMeasurement
    template_name = "grais/probe_measurement_confirm_delete.html"
    success_message = 'The probe measurement was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('grais:sample_detail', kwargs={'pk':self.kwargs['sample']})


# LINES #
#########

class LineCreateView(LoginRequiredMixin, CreateView):
    model = models.Line
    form_class = forms.LineCreateForm
    login_url = '/accounts/login_required/'
    template_name = 'grais/line_form.html'

    def get_initial(self):
        sample = models.Sample.objects.get(pk=self.kwargs['sample'])
        return {
            'sample': sample,
            'number_plates':2,
            'number_petris':3,
            'last_modified_by': self.request.user
            }

    def form_valid(self, form):
        self.object = form.save()
        petris = form.cleaned_data['number_petris']
        plates = form.cleaned_data['number_plates']
        if petris+plates > 0:
            # create instances of surfaces on the collector lines
            # create iterable
            for i in range(petris):
                s = models.Surface.objects.create(line=self.object, surface_type = 'pe', label=i+1 )
                s.save()
            for i in range(plates):
                s = models.Surface.objects.create(line=self.object, surface_type = 'pl', label=i+1 )
                s.save()
        return HttpResponseRedirect(self.get_success_url())

class LineDetailView(LoginRequiredMixin, DetailView):
    model = models.Line
    login_url = '/accounts/login_required/'
    template_name = 'grais/line_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context

class LineUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Line
    form_class = forms.LineForm
    login_url = '/accounts/login_required/'

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class LineDeleteView(LoginRequiredMixin, DeleteView):

    model = models.Line
    template_name = "grais/line_confirm_delete.html"
    success_message = 'The line was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('grais:sample_detail', kwargs={'pk':self.kwargs['sample']})


# COLLECTORS #
##############

class CollectorListView(LoginRequiredMixin, ListView):
    model = models.Collector
    login_url = '/accounts/login_required/'

class CollectorDetailView(LoginRequiredMixin, UpdateView):
    model = models.Collector
    fields = "__all__"
    login_url = '/accounts/login_required/'
    template_name = 'grais/collector_detail.html'

class CollectorUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Collector
    fields = "__all__"
    login_url = '/accounts/login_required/'
    # template_name = 'grais/collector_form_popout.html'

class CollectorCreateView(LoginRequiredMixin, CreateView):
    model = models.Collector
    fields = "__all__"
    login_url = '/accounts/login_required/'
    template_name = 'grais/collector_form_popout.html'

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('grais:close_me'))

class CollectorDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = models.Collector
    permission_required = "__all__"
    success_url = reverse_lazy('grais:collector_list')
    success_message = 'The collector was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# SPECIES #
###########

class SpeciesListView(LoginRequiredMixin, FilterView):
    template_name = "grais/species_list.html"
    filterset_class = filters.SpeciesFilterFull
    login_url = '/accounts/login_required/'

class SpeciesDetailView(LoginRequiredMixin, DetailView):
    model = models.Species
    fields = "__all__"
    login_url = '/accounts/login_required/'

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

class SpeciesCreatePopoutView(LoginRequiredMixin, CreateView):
    model = models.Species
    login_url = '/accounts/login_required/'
    form_class = forms.SpeciesForm
    template_name = 'grais/species_form_popout.html'

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['temp_msg'] = "The new species has been added to the list."

        return HttpResponseRedirect(reverse('grais:close_me'))

class SpeciesDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = models.Species
    permission_required = "__all__"
    success_url = reverse_lazy('grais:species_list')
    success_message = 'The species was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# SURFACES #
############

class SurfaceDetailView(LoginRequiredMixin, UpdateView):
    model = models.Surface
    form_class = forms.SurfaceImageForm
    login_url = '/accounts/login_required/'
    template_name = 'grais/surface_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surface = self.kwargs['pk']
        surface_spp = models.Surface.objects.get(id=surface).surface_spp.all()
        total_coverage = 0
        for sp in surface_spp:
            total_coverage += sp.percent_coverage

        context['total_coverage']= total_coverage
        return context

class SurfaceUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Surface
    form_class = forms.SurfaceForm
    login_url = '/accounts/login_required/'

    def get_initial(self):
        return {'last_modified_by': self.request.user}

class SurfaceCreateView(LoginRequiredMixin, CreateView):
    model = models.Surface
    form_class = forms.SurfaceForm
    login_url = '/accounts/login_required/'

    def get_initial(self):
        line = models.Line.objects.get(pk=self.kwargs['line'])
        return {
            'line': line,
            'last_modified_by': self.request.user
        }

class SurfaceDeleteView(LoginRequiredMixin, DeleteView):

    model = models.Surface
    template_name = "grais/surface_confirm_delete.html"
    success_message = 'The surface was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('grais:line_detail', kwargs={'sample':self.kwargs['sample'],'pk':self.kwargs['line']})



# SURFACE SPECIES #
class SurfaceSpeciesCreatePopoutView(LoginRequiredMixin,CreateView):
    model = models.SurfaceSpecies
    template_name ='grais/surface_species_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.SurfaceSpeciesForm

    def get_initial(self):
        surface = models.Surface.objects.get(pk=self.kwargs['surface'])
        species = models.Species.objects.get(pk=self.kwargs['species'])
        return {
            'surface': surface,
            'species': species,
            'last_modified_by': self.request.user,
            }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species = self.kwargs['species']
        species = models.Species.objects.get(id=species)
        context['species']= species
        return context

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('grais:close_me'))

class SurfaceSpeciesUpdatePopoutView(LoginRequiredMixin,UpdateView):
    model = models.SurfaceSpecies
    template_name ='grais/surface_species_form_popout.html'
    form_class = forms.SurfaceSpeciesForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}



class SurfaceSpeciesDetailPopoutView(LoginRequiredMixin,UpdateView):
    model = models.SurfaceSpecies
    template_name ='grais/surface_species_detail_popout.html'
    form_class = forms.SurfaceSpeciesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            extra_context = {'temp_msg':self.request.session['temp_msg']}
            context.update(extra_context)
            del self.request.session['temp_msg']
        except Exception as e:
            print("type error: " + str(e))
            # pass

        return context

class SpeciesInsertListView(FilterView):
    filterset_class = filters.SpeciesFilter
    template_name = "grais/surface_species_insert.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surface = self.kwargs['surface']
        my_surface = models.Surface.objects.get(id=surface)
        context['surface']= my_surface
        surface_spp = models.Surface.objects.get(id=surface).surface_spp.all()
        context['surface_spp']= surface_spp
        total_coverage = 0
        for sp in surface_spp:
            total_coverage += sp.percent_coverage

        context['total_coverage']= total_coverage

        # confirmation message for when a new species is added to the list
        try:
            extra_context = {'temp_msg':self.request.session['temp_msg']}
            context.update(extra_context)
            del self.request.session['temp_msg']
        except Exception as e:
            print("type error: " + str(e))
            # pass

        return context


    # def get_filterset_kwargs(self, filterset_class):
    #     kwargs = super().get_filterset_kwargs(filterset_class)
    #     if kwargs["data"] is None:
    #         kwargs["data"] = {"biofouling": True }
    #     return kwargs

class SurfaceSpeciesDeletePopoutView(LoginRequiredMixin,DeleteView):
    model = models.SurfaceSpecies
    template_name ='grais/surface_species_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('grais:close_me')


# CSVs #
########

def export_csv_1(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response


# INCIDENTAL REPORT #
#####################

class ReportListView(LoginRequiredMixin, FilterView):
    filterset_class = filters.ReportFilter
    template_name = "grais/report_list.html"
    login_url = '/accounts/login_required/'


class ReportUpdateView(LoginRequiredMixin,  UpdateView):
    login_url = '/accounts/login_required/'
    model = models.IncidentalReport
    form_class = forms.StationForm
    template_name = "grais/report_form.html"

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = models.IncidentalReport
    login_url = '/accounts/login_required/'
    form_class = forms.ReportForm
    template_name = "grais/report_form.html"

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = models.IncidentalReport
    login_url = '/accounts/login_required/'
    template_name = "grais/report_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        field_list = [
            "report_date",
            "reporter_name",
            "report_type",
            "language_of_report",
            "call_answered_by",
            "call_returned_by",
            "location_description",
            "latitude_n",
            "longitude_w",
            "specimens_retained",
            "sighting_description",
            "identified_by",
            "date_of_occurence",
            "obvservation_type",
            "phone",
            "email",
            "notes",
            "date_last_modified",
            "last_modified_by",
        ]

        context["field_list"] = field_list

        return context


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = models.IncidentalReport
    success_url = reverse_lazy('grais:report_list')
    success_message = 'The report was successfully deleted!'
    template_name = "grais/report_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

