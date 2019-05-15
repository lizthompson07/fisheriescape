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

import json

from . import models
from . import forms

project_field_list = [
    'id',
    'pub_year',
    'pub_title',
    'date_last_modified',
    'last_modified_by',
]

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
        object = form.save()


        return HttpResponseRedirect(reverse_lazy("publications:pub_detail", kwargs={"pk": object.id}))

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
    form_class = forms.PublicationsForm
    template_name = "publications/pub_form.html"

    def get_initial(self):
        my_dict = {
            'last_modified_by': self.request.user,
        }

        try:
            my_dict["pub_year"] = "{}-{:02d}-{:02d}".format(self.object.pub_year.year)
        except:
            print("no start date...")

        return my_dict


class PublicationDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Publications
    permission_required = "__all__"
    success_url = reverse_lazy('publications:my_pub_list')
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

    def get_queryset(self):
        return models.Staff.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class PublicationsListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'publications/pub_list.html'
    model = models.Publications
