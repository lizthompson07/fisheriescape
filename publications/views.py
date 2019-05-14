from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse

from django.db.models import Q
from shared_models import models as shared_models

import json

from . import models
from . import forms


class IndexTemplateView(TemplateView):
    template_name = 'publications/index.html'


class PublicationsCreateView(LoginRequiredMixin, CreateView):
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
        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch_id=1) | Q(division__branch_id=3)).order_by(
                               "division__branch__region", "division__branch", "division", "name")]

        division_dict = {}
        for d in division_choices:
            division_dict[d[1]] = d[0]

        section_dict = {}
        for s in section_choices:
            section_dict[s[1]] = s[0]

        context['division_json'] = json.dumps(division_dict)

        return context

    def form_valid(self, form):
        object = form.save()

        return HttpResponseRedirect(reverse_lazy("publications:pub_detail", kwargs={"pk": object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PublicationDetailView(LoginRequiredMixin, DetailView):
    template_name = 'publications/pub_detail.html'
    model = models.Publications
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.object
        context["field_list"] = [
            'id',
            'pub_year',
            'pub_title',
            'date_last_modified',
            'last_modified_by',
        ]

        return context


class MyPublicationsListView(LoginRequiredMixin, ListView):
    template_name = 'publications/my_pub_list'
    login_url = '/accounts/login_required/'
    template_name = 'projects/my_project_list.html'

    def get_queryset(self):
        return models.Staff.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
