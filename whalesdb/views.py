from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _

import json
import datetime

from . import forms
from . import models
from . import filters


class IndexView(TemplateView):
    template_name = 'whalesdb/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['section'] = [
            {
                'title': 'Entry Forms',
                'forms': [
                    {
                        'title': _("Station List"),
                        'url': "whalesdb:list_stn",
                        'icon': "img/whales/station.svg",
                    },
                    {
                        'title': _("Project List"),
                        'url': "whalesdb:list_prj",
                        'icon': "img/whales/project.svg",
                    },
                    {
                        'title': _("Mooring Setup List"),
                        'url': "whalesdb:list_mor",
                        'icon': "img/whales/mooring.svg",
                    },
                ]
           },
        ]

        return context


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


class CloserNoRefreshTemplateView(TemplateView):
    template_name = 'whalesdb/close_me_no_refresh.html'


class CreateCommon(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login_required/'
    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context["title"] = self.title

        return context


class CreatePrj(CreateCommon):
    model = models.PrjProject
    form_class = forms.PrjForm
    success_url = reverse_lazy("whalesdb:list_prj")
    title = _("Create Project")
    template_name = 'whalesdb/_entry_form.html'


class CreateStn(CreateCommon):
    model = models.StnStation
    form_class = forms.StnForm
    success_url = reverse_lazy("whalesdb:list_stn")
    title = _("Create Station")

    template_name = 'whalesdb/_entry_form.html'


class CreateMor(CreateCommon):
    model = models.MorMooringSetup
    form_class = forms.MorForm
    success_url = reverse_lazy("whalesdb:list_mor")
    title = _("Create Mooring Setup")

    template_name = 'whalesdb/_entry_form.html'


class DetailsCommon(DetailView):
    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context['title'] = self.title

        return context


class DetailsPrj(DetailsCommon):
    model = models.PrjProject


class DetailsStn(DetailsCommon):
    model = models.StnStation


class DetailsMor(DetailsCommon):
    model = models.MorMooringSetup
    title = _("Mooring Setup Details")


class ListCommon(FilterView):
    template_name = 'whalesdb/whale_filter.html'
    fields = []
    create_url = None
    details_url = None
    title = None

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.fields

        if self.title:
            context['title'] = self.title

        if self.create_url:
            context['create_url'] = self.create_url

        if self.details_url:
            context['details_url'] = self.details_url

        return context


class ListPrj(ListCommon):
    model = models.PrjProject
    filterset_class = filters.PrjFilter
    create_url = "whalesdb:create_prj"
    details_url = "whalesdb:details_prj"
    title = _("Project List")
    fields = ['prj_name', 'prj_description']


class ListStn(ListCommon):
    model = models.StnStation
    filterset_class = filters.StnFilter
    create_url = "whalesdb:create_stn"
    details_url = "whalesdb:details_stn"
    fields = ['stn_name', 'stn_code', 'stn_revision']
    title = _("Station List")


class ListMor(ListCommon):
    model = models.MorMooringSetup
    filterset_class = filters.MorFilter
    create_url = "whalesdb:create_mor"
    details_url = "whalesdb:details_mor"
    fields = ['mor_name', 'mor_max_depth', 'more_notes']
    title = _("Mooring Setup List")
