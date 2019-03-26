from shared_models import models as shared_models
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django_filters.views import FilterView
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


class PredatorFilterView(LoginRequiredMixin, FilterView):
    template_name = "diets/predator_filter.html"
    filterset_class = filters.PredatorFilter
    login_url = '/accounts/login_required/'
    queryset = models.Predator.objects.annotate(
        search_term=Concat('species__common_name_eng', 'species__common_name_fre', 'species__scientific_name',
                           'species__id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Predator.objects.first()
        context["field_list"] = [
            'id',
            'stomach_id',
            'species.common_name_eng',
            'cruise',
            'processing_date',
        ]
        return context


class PredatorDetailView(LoginRequiredMixin, DetailView):
    model = models.Predator
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'cruise',
            'processing_date',
            'samplers',
            'set',
            'fish_number',
            'stomach_id',
            'somatic_length_cm',
            'stomach_wt_g',
            'content_wt_g',
            'comments',
            'last_modified_by',
            'date_last_modified',
            # 'somatic_wt_g',
            # 'stratum',
        ]

        species_list = []
        for obj in models.Species.objects.all():
            url = reverse("diets:prey_new", kwargs={"predator": self.object.id, "species": obj.id}),
            html_insert = '<a class="add-btn btn btn-outline-dark" href="#" target-url="{}"> <img src="{}" alt=""></a><span style="margin-left: 10px;">{} / {} / <em>{}</em> / {}</span>'.format(
                url[0],
                static("admin/img/icon-addlink.svg"),
                obj.id,
                obj.common_name_eng,
                obj.scientific_name,
                obj.abbrev,
            )
            species_list.append(html_insert)
        context['species_list'] = species_list

        return context


class PredatorUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Predator
    login_url = '/accounts/login_required/'
    form_class = forms.PredatorForm

    def get_initial(self):
        return {'last_modified_by': self.request.user, }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get lists
        species_list = ['<a href="#" class="species_insert" code={id}>{text}</a>'.format(id=obj.id, text=str(obj)) for
                        obj in models.Species.objects.all()]
        context['species_list'] = species_list
        return context


class PredatorCreateView(LoginRequiredMixin, CreateView):
    model = models.Predator
    login_url = '/accounts/login_required/'
    form_class = forms.PredatorForm

    def get_initial(self):
        initial_dict ={'last_modified_by': self.request.user,}

        # if this view is being called with a cruise number, cruise field should auto populate
        try:
            initial_dict["cruise"] = shared_models.Cruise.objects.get(pk=self.kwargs["cruise"])
        except KeyError:
            pass

        return initial_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get lists
        species_list = ['<a href="#" class="species_insert" code={id}>{text}</a>'.format(id=obj.id, text=str(obj)) for
                        obj in models.Species.objects.all()]
        context['species_list'] = species_list
        return context


class PredatorDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Predator
    permission_required = "__all__"
    success_url = reverse_lazy('diets:predator_filter')
    success_message = 'The predator was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PREY #
########


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
            'last_modified_by': self.request.user,
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

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


def prey_delete(request, pk):
    object = models.Prey.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The prey has been successfully deleted from {}.".format(object.predator))
    return HttpResponseRedirect(reverse_lazy("diets:predator_detail", kwargs={"pk": object.predator.id}))


# CRUISE #
##########

class CruiseListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    queryset = shared_models.Cruise.objects.all().order_by("-season", "mission_number")
    template_name = 'diets/cruise_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = shared_models.Cruise.objects.first()
        context["field_list"] = [
            'season',
            'mission_name',
            'mission_number',
            'vessel',
            'chief_scientist',
            'samplers',
            'start_date',
            'end_date',
        ]
        return context


class CruiseDetailView(LoginRequiredMixin, DetailView):
    model = shared_models.Cruise
    login_url = '/accounts/login_required/'
    template_name = 'diets/cruise_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'season',
            'mission_name',
            'mission_number',
            'description',
            'chief_scientist',
            'samplers',
            'start_date',
            'end_date',
            'notes',
            'vessel',
        ]
        return context


class CruiseUpdateView(LoginRequiredMixin, UpdateView):
    model = shared_models.Cruise
    login_url = '/accounts/login_required/'
    form_class = forms.CruiseForm
    template_name = 'diets/cruise_form.html'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('diets:cruise_detail', kwargs={"pk": object.id}))


class CruiseCreateView(LoginRequiredMixin, CreateView):
    model = shared_models.Cruise
    login_url = '/accounts/login_required/'
    form_class = forms.CruiseForm
    success_url = reverse_lazy('diets:cruise_list')
    template_name = 'diets/cruise_form.html'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('diets:cruise_detail', kwargs={"pk": object.id}))

class CruiseDeleteView(LoginRequiredMixin, DeleteView):
    model = shared_models.Cruise
    success_url = reverse_lazy('diets:cruise_list')
    success_message = 'The cruise was successfully deleted!'
    template_name = 'diets/cruise_confirm_delete.html'

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



# SAMPLER #
###########

class SamplerListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.Sampler


class SamplerUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Sampler
    login_url = '/accounts/login_required/'
    form_class = forms.SamplerForm
    success_url = reverse_lazy('diets:sampler_list')


class SamplerCreateView(LoginRequiredMixin, CreateView):
    model = models.Sampler
    login_url = '/accounts/login_required/'
    form_class = forms.SamplerForm
    success_url = reverse_lazy('diets:sampler_list')


class SamplerDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Sampler
    success_url = reverse_lazy('diets:sampler_list')
    success_message = 'The samplers was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
