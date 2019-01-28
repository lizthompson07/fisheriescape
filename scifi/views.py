from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from accounts import models as accounts_models
from collections import OrderedDict

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'scifi/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'scifi/index.html'


# ALLOTMENT CODE #
##################

class AllotmentCodeListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.AllotmentCode


class AllotmentCodeUpdateView(LoginRequiredMixin, UpdateView):
    model = models.AllotmentCode
    login_url = '/accounts/login_required/'
    form_class = forms.AllotmentCodeForm
    success_url = reverse_lazy('scifi:allotment_list')


class AllotmentCodeCreateView(LoginRequiredMixin, CreateView):
    model = models.AllotmentCode
    login_url = '/accounts/login_required/'
    form_class = forms.AllotmentCodeForm
    success_url = reverse_lazy('scifi:digestion_list')


class AllotmentCodeDeleteView(LoginRequiredMixin, DeleteView):
    model = models.AllotmentCode
    success_url = reverse_lazy('scifi:digestion_list')
    success_message = 'The allotment code was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# BUSINESS LINE #
#################

class BusinessLineListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.BusinessLine


class BusinessLineUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BusinessLine
    login_url = '/accounts/login_required/'
    form_class = forms.BusinessLineForm
    success_url = reverse_lazy('scifi:business_list')


class BusinessLineCreateView(LoginRequiredMixin, CreateView):
    model = models.BusinessLine
    login_url = '/accounts/login_required/'
    form_class = forms.BusinessLineForm
    success_url = reverse_lazy('scifi:business_list')


class BusinessLineDeleteView(LoginRequiredMixin, DeleteView):
    model = models.BusinessLine
    success_url = reverse_lazy('scifi:business_list')
    success_message = 'The business line was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# LINE OBJECT #
###############

class LineObjectListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.LineObject


class LineObjectUpdateView(LoginRequiredMixin, UpdateView):
    model = models.LineObject
    login_url = '/accounts/login_required/'
    form_class = forms.LineObjectForm
    success_url = reverse_lazy('scifi:lo_list')


class LineObjectCreateView(LoginRequiredMixin, CreateView):
    model = models.LineObject
    login_url = '/accounts/login_required/'
    form_class = forms.LineObjectForm
    success_url = reverse_lazy('scifi:lo_list')


class LineObjectDeleteView(LoginRequiredMixin, DeleteView):
    model = models.LineObject
    success_url = reverse_lazy('scifi:lo_list')
    success_message = 'The line object was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# RC #
######

class ResponsibilityCentreListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    model = models.ResponsibilityCenter


class ResponsibilityCentreUpdateView(LoginRequiredMixin, UpdateView):
    model = models.ResponsibilityCenter
    login_url = '/accounts/login_required/'
    form_class = forms.ResponsibilityCentreForm
    success_url = reverse_lazy('scifi:rc_list')


class ResponsibilityCentreCreateView(LoginRequiredMixin, CreateView):
    model = models.ResponsibilityCenter
    login_url = '/accounts/login_required/'
    form_class = forms.ResponsibilityCentreForm
    success_url = reverse_lazy('scifi:rc_list')


class ResponsibilityCentreDeleteView(LoginRequiredMixin, DeleteView):
    model = models.ResponsibilityCenter
    success_url = reverse_lazy('scifi:rc_list')
    success_message = 'The RC was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
