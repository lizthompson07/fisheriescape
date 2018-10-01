from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy
from . import models
from . import forms
# Create your views here.


class DocListView(ListView):
    model = models.Doc
    template_name = "docs/doc_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class DocCreateView(CreateView):
    model = models.Doc
    template_name = "docs/doc_form.html"
    form_class = forms.DocForm
    success_url = reverse_lazy("docs:doc_list")

class DocUpdateView(UpdateView):
    model = models.Doc
    template_name = "docs/doc_form.html"
    form_class = forms.DocForm
    success_url = reverse_lazy("docs:doc_list")
