from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse

from django.db.models import Q
from shared_models import models as shared_models
from publications import filters

import json

from . import models
from . import forms


def get_mod(mod_str):
    if mod_str == "theme":
        lookup_mod = models.Theme
    elif mod_str == "human":
        lookup_mod = models.HumanComponents
    elif mod_str == "linkage":
        lookup_mod = models.ProgramLinkage
    elif mod_str == "ecosystem":
        lookup_mod = models.EcosystemComponents

    return lookup_mod


def get_mod_title(mod_str):
    if mod_str == "theme":
        title = "Theme"
    elif mod_str == "human":
        title = "Human Component"
    elif mod_str == "linkage":
        title = "Linkage to Program"
    elif mod_str == "ecosystem":
        title = "Ecosystem Component"

    return title

project_field_list = [
    'id',
    'pub_year',
    'pub_title',
    'date_last_modified',
    'last_modified_by',
]


class CloserTemplateView(TemplateView):
    template_name = 'publications/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'publications/index.html'


class PublicationCreateView(LoginRequiredMixin, CreateView):
    template_name = 'publications/pub_form.html'
    model = models.Publications
    login_url = '/accounts/login_required/'
    form_class = forms.NewPublicationsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # here are the option objects we want to send in through context
        # only from the science branches of each region
        division_choices = [(d.id, str(d)) for d in
                            shared_models.Division.objects.filter(Q(branch_id=1) | Q(branch_id=3)).order_by("branch__region", "name")]

        division_dict = {}
        for s in division_choices:
            division_dict[s[1]] = s[0]

        context['division_json'] = json.dumps(division_dict)

        return context

    def form_valid(self, form):
        publication = form.save()

        return HttpResponseRedirect(reverse_lazy("publications:pub_detail", kwargs={"pk": publication.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PublicationSubmitUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Publications
    login_url = '/accounts/login_required/'
    form_class = forms.PublicationsSubmitForm
    template_name = "publications/pub_submit_form.html"

    def get_initial(self):

        return {
            'last_modified_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class PublicationUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Publications
    login_url = '/accounts/login_required/'
    form_class = forms.NewPublicationsForm
    template_name = "publications/pub_form.html"

    def get_initial(self):
        my_dict = {
            'last_modified_by': self.request.user,
        }

        try:
            my_dict["pub_year"] = "{}".format(self.object.pub_year.year)
        except:
            print("no start date...")

        return my_dict


class PublicationDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Publications
    permission_required = "__all__"
    success_url = reverse_lazy('publications:')
    success_message = _('The publication was successfully deleted!')
    login_url = '/accounts/login_required/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class PublicationDetailView(LoginRequiredMixin, DetailView):
    template_name = 'publications/pub_detail.html'
    model = models.Publications
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.object

        context["abstract"] =[
            'pub_abstract'
        ]

        context["field_list"] = [
            'pub_year',
            'division',
        ]

        context["lookups"] = [
            {
                "url": "theme",
                "label": "Theme",
                "list": models.Theme.objects.filter(publications__id=publication.id).order_by("name")
            },
            {
                "url": "human",
                "label": "Human Component",
                "list": models.HumanComponents.objects.filter(publications__id=publication.id).order_by("name")
            },
            {
                "url": "ecosystem",
                "label": "Ecosystem Component",
                "list": models.EcosystemComponents.objects.filter(publications__id=publication.id).order_by("name")
            },
            {
                "url": "linkage",
                "label": "Linkage to Program",
                "list": models.ProgramLinkage.objects.filter(publications__id=publication.id).order_by("name")
            },
        ]
        context["field_list_1"] = [
            'human_component',
            'ecosystem_component',
            'spatial_management',
            'sustainability_pillar',
            'program_linkage',
        ]

        return context


class PublicationsListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'publications/pub_list.html'
    model = models.Publications
    filterset_class = filters.PublicationsFilter


class LookupCreateView(LoginRequiredMixin, CreateView):
    template_name = 'publications/new_lookup.html'
    model = models.Theme
    form_class = forms.LookupNew

    def get_initial(self):

        lookup_mod = get_mod(self.kwargs['lookup'])
        return {
            'lookup': lookup_mod
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = get_mod_title(self.kwargs['lookup'])

        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('publications:close_me'))


class LookupAddView(LoginRequiredMixin, CreateView):
    template_name = 'publications/new_lookup_popout.html'
    model = models.Theme
    form_class = forms.LookupForm

    def get_initial(self):
        publications = models.Publications.objects.get(pk=self.kwargs['publications'])
        lookup_mod = get_mod(self.kwargs['lookup'])

        return {
            'publications': publications,
            'lookup': lookup_mod
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publications = models.Publications.objects.get(id=self.kwargs['publications'])
        context['publications'] = publications
        context['title'] = get_mod_title(self.kwargs['lookup'])
        context['url_var'] = self.kwargs['lookup']
        return context

    def form_valid(self, form):
        mod = get_mod(self.kwargs['lookup'])

        # get a queryset of lookup matching what was selected in the form field
        vals = mod.objects.filter(pk__in=form.cleaned_data['name'])

        # get the publication the lookup are being added to
        publication = models.Publications.objects.get(id=self.kwargs['publications'])

        dirty = False
        # for each lookup make sure it doesn't already exist in the publication variable
        for val in vals:
            if publication and not mod.objects.filter(pk=val.id, publications__id=publication.id):
                if mod is models.Theme:
                    publication.theme.add(val)
                elif mod is models.HumanComponents:
                    publication.human_component.add(val)
                elif mod is models.ProgramLinkage:
                    publication.program_linkage.add(val)
                elif mod is models.EcosystemComponents:
                    publication.ecosystem_component.add(val)
                dirty = True

        if dirty:
            publication.save()

        return HttpResponseRedirect(reverse('publications:close_me'))
