import csv
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from easy_pdf.views import PDFTemplateView
from django_filters.views import FilterView

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters


class CloserTemplateView(TemplateView):
    template_name = 'diets/close_me.html'


def in_diets_group(user):
    if user:
        return user.groups.filter(name='diets_access').count() != 0


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_diets_group, login_url='/accounts/denied/')
def index(request):
    return render(request, 'diets/index.html')


# SPECIES #
###########

class SpeciesListView(LoginRequiredMixin, FilterView):
    template_name = "diets/species_list.html"
    filterset_class = filters.SpeciesFilter
    login_url = '/accounts/login_required/'
    queryset = models.Species.objects.annotate(
        search_term=Concat('common_name_eng', 'common_name_fre', 'scientific_name', 'id', output_field=TextField()))


class SpeciesDetailView(LoginRequiredMixin, DetailView):
    model = models.Species
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'common_name_eng',
            'common_name_fre',
            'scientific_name',
            'tsn',
            'aphia_id',
        ]
        return context


class SpeciesUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Species
    login_url = '/accounts/login_required/'
    form_class = forms.SpeciesForm


class SpeciesCreateView(LoginRequiredMixin, CreateView):
    model = models.Species
    login_url = '/accounts/login_required/'
    form_class = forms.SpeciesForm


class SpeciesDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Species
    permission_required = "__all__"
    success_url = reverse_lazy('diets:species_list')
    success_message = 'The species was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PREDATOR #
############

class PredatorSearchFormView(LoginRequiredMixin, FormView):
    template_name = 'diets/predator_search.html'
    login_url = '/accounts/login_required/'
    form_class = forms.SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cruise_list = [{"val": obj.id, "text": obj} for obj in models.Cruise.objects.all()]
        species_list = [{"val": obj.id, "text": obj} for obj in models.Species.objects.all()]

        context["species_list"] = species_list
        context["cruise_list"] = cruise_list
        return context

    def form_valid(self, form):
        cruise = nz(form.cleaned_data["cruise"], None)
        species = nz(form.cleaned_data["species"], None)

        # check to see how many results will be returned
        qs = models.Predator.objects.all()
        if cruise:
            qs = qs.filter(cruise_id=cruise)
        if species:
            qs = qs.filter(species_id=species)

        if qs.count() > 1500:
            messages.error(self.request, "The search requested has returned too many results. Please try again.")
            return HttpResponseRedirect(reverse("diets:predator_search"))
        elif qs.count() is 0:
            messages.error(self.request, "The search requested has returned no results. Please try again.")
            return HttpResponseRedirect(reverse("diets:predator_search"))
        else:
            return HttpResponseRedirect(reverse("diets:predator_list",
                                                kwargs={"cruise": cruise, "species": species, }))


# class PredatorListView(LoginRequiredMixin, FilterView):
#     template_name = "diets/predator_list.html"
#     filterset_class = filters.PredatorFilter
#     login_url = '/accounts/login_required/'
#     queryset = models.Predator.objects.annotate(
#         search_term=Concat('species__common_name_eng', 'species__common_name_fre', 'species__scientific_name',
#                            'species__id', output_field=TextField()))

class PredatorListView(LoginRequiredMixin, ListView):
    template_name = "diets/predator_list.html"
    login_url = '/accounts/login_required/'

    def get_queryset(self):
        cruise = nz(self.kwargs["cruise"])
        species = nz(self.kwargs["species"])

        qs = models.Predator.objects.all()
        if cruise:
            qs = qs.filter(cruise_id=cruise)
        if species:
            qs = qs.filter(species_id=species)
        return qs


class PredatorDetailView(LoginRequiredMixin, DetailView):
    model = models.Predator
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'set',
            'stratum',
            'fish_number',
            'processing_date',
            'sampler',
            'somatic_length_mm',
            'somatic_wt_g',
            'stomach_wt_g',
            'comments',
        ]
        return context


class PredatorUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Predator
    login_url = '/accounts/login_required/'
    form_class = forms.PredatorForm


class PredatorCreateView(LoginRequiredMixin, CreateView):
    model = models.Predator
    login_url = '/accounts/login_required/'
    form_class = forms.PredatorForm


class PredatorDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Predator
    permission_required = "__all__"
    success_url = reverse_lazy('diets:predator_search')
    success_message = 'The predator was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PREY #
########

class PreyInsertView(TemplateView):
    template_name = "diets/prey_insert.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        predator = models.Predator.objects.get(pk=self.kwargs['predator'])
        context['predator'] = predator
        prey_items = models.Predator.objects.get(pk=predator.id).prey_items.all()
        context['prey_items'] = prey_items

        queryset = models.Species.objects.annotate(
            search_term=Concat('common_name_eng', 'common_name_fre', 'scientific_name', 'id',
                               output_field=TextField()))

        # get a list of species
        species_list = []
        for obj in queryset:
            # html_insert = '<a href="#" class="district_insert" code={p}{d}>{p}{d}</a> - {l}, {prov}'.format(
            #         p=d.province_id, d=d.district_id, l=l.replace("'", ""), prov=d.get_province_id_display().upper())
            html_insert = '<a class="add-btn btn btn-outline-dark" href="#" target-url="{}"> <img src="{}" alt=""></a><span style="margin-left: 10px;">{} / {} / <em>{}</em> / {}</span>'.format(
                reverse("diets:prey_new", kwargs={"predator": predator.id, "species": obj.id}),
                static("admin/img/icon-addlink.svg"),
                obj.common_name_eng,
                obj.common_name_fre,
                obj.scientific_name,
                obj.id
            )
            species_list.append(html_insert)
        context['species_list'] = species_list
        context["species_count"] = models.Prey.objects.filter(predator=predator).count

        return context


class PreyCreateView(LoginRequiredMixin, CreateView):
    model = models.Prey
    template_name = 'diets/prey_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.PreyForm

    def get_initial(self):
        predator = models.Predator.objects.get(pk=self.kwargs['predator'])
        species = models.Species.objects.get(pk=self.kwargs['species'])
        return {
            'predator': predator,
            'species': species,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species = models.Species.objects.get(id=self.kwargs['species'])
        predator = models.Predator.objects.get(id=self.kwargs['predator'])
        context['species'] = species
        context['predator'] = predator
        return context

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('diets:close_me'))


class PreyUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Prey
    template_name = 'diets/prey_form_popout.html'
    form_class = forms.PreyForm

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('diets:close_me'))


def prey_delete(request, pk, backto):
    object = models.Prey.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The prey has been successfully deleted from {}.".format(object.predator))

    if backto == "detail":
        return HttpResponseRedirect(reverse_lazy("diets:predator_detail", kwargs={"pk": object.predator.id}))
    else:
        return HttpResponseRedirect(reverse_lazy("diets:prey_search", kwargs={"predator": object.predator.id}))



# CRUISE #
##########

class CruiseListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.Cruise

class CruiseDetailView(LoginRequiredMixin, DetailView):
    model = models.Cruise
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'cruise_number',
            'description',
            'chief_scientist',
            'samplers',
            'start_date',
            'end_date',
            'notes',
            'season',
            'vessel',
        ]
        return context


class CruiseUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Cruise
    login_url = '/accounts/login_required/'
    form_class = forms.CruiseForm


class CruiseCreateView(LoginRequiredMixin, CreateView):
    model = models.Cruise
    login_url = '/accounts/login_required/'
    form_class = forms.CruiseForm
    success_url = reverse_lazy('diets:cruise_list')


class CruiseDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Cruise
    success_url = reverse_lazy('diets:cruise_list')
    success_message = 'The cruise was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)



# DIGESTION #
#############

class DigestionListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.DigestionLevel


class DigestionUpdateView(LoginRequiredMixin, UpdateView):
    model = models.DigestionLevel
    login_url = '/accounts/login_required/'
    form_class = forms.DigestionForm
    success_url = reverse_lazy('diets:digestion_list')


class DigestionCreateView(LoginRequiredMixin, CreateView):
    model = models.DigestionLevel
    login_url = '/accounts/login_required/'
    form_class = forms.DigestionForm
    success_url = reverse_lazy('diets:digestion_list')


class DigestionDeleteView(LoginRequiredMixin, DeleteView):
    model = models.DigestionLevel
    success_url = reverse_lazy('diets:digestion_list')
    success_message = 'The digestion level was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
