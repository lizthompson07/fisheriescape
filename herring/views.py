from django.shortcuts import render
import csv
from django.shortcuts import render
from django.views.generic import ListView,  UpdateView, DeleteView, CreateView, DetailView, TemplateView
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from braces.views import GroupRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django_filters.views import FilterView
from django.utils import timezone
from . import models
from . import forms
from . import filters
from . import emails
# Create your views here.

class IndexView(GroupRequiredMixin,TemplateView):
    template_name = 'herring/index.html'
    group_required = [u"grais_access",]
    login_url = '/accounts/login_required/'

class CloserTemplateView(TemplateView):
    template_name = 'grais/close_me.html'

# SAMPLE #
##########

class SampleFilterView(LoginRequiredMixin, FilterView):
    filterset_class = filters.SampleFilter
    template_name = "herring/sample_filter.html"
    login_url = '/accounts/login_required/'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"SeasonSince": timezone.now().year-2 }
        return kwargs

class PortSampleCreateView(LoginRequiredMixin,CreateView):
    template_name = 'herring/port_sample_form.html'
    form_class = forms.PortSampleForm
    model = models.Sample

    def get_initial(self):
        return {
            'created_by': self.request.user,
            'last_modified_by': self.request.user,
        }

class PortSampleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'herring/port_sample_form.html'
    form_class = forms.PortSampleForm
    model = models.Sample

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            }

class PortSampleDetailView(LoginRequiredMixin,DetailView):
    template_name = 'herring/port_sample_detail.html'
    model = models.Sample
