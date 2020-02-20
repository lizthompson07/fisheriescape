from django.shortcuts import render
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView
from . import models


# Create your views here.
class IndexTemplateView(TemplateView):
    template_name = 'csas/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = models.CotType.objects.get(name="Smith")
        return context

class ContactsTemplateView(TemplateView):
    template_name = 'csas/contacts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["title"] = models.CotType.objects.get(name="Smith")
        return context
