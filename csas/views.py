from django.shortcuts import render

from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from django.urls import reverse_lazy
from . import models, forms


class CloserTemplateView(TemplateView):
    template_name = 'whalesdb/close_me.html'


# Create your views here.
class IndexTemplateView(TemplateView):
    template_name = 'csas/index.html'


class ContactsTemplateView(CreateView):
    template_name = 'csas/contacts.html'
    model = models.ConContact
    form_class = forms.ContactForm

#    form_class = forms.ContactForm


class MeetingsTemplateView(CreateView):
    template_name = 'csas/meetings.html'
    model = models.MetMeeting
    form_class = forms.MeetingForm


class PublicationsTemplateView(CreateView):
    template_name = 'csas/publications.html'
    model = models.PubPublication
    form_class = forms.PublicationForm


class RequestsTemplateView(CreateView):
    template_name = 'csas/requests.html'
    model = models.MetMeeting
    form_class = forms.MeetingForm


class OthersTemplateView(CreateView):
    template_name = 'csas/others.html'
    model = models.MetMeeting
    form_class = forms.MeetingForm


class CommonLookup(CreateView):
    template_name = 'csas/_lookup_entry_form.html'
    fields = ['name']
    success_url = reverse_lazy("csas:close_me")


class HonorificView(CommonLookup):
    model = models.CohHonorific


class LanguageView(CommonLookup):
    model = models.LanLanguage
