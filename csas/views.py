from django.shortcuts import render
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, TemplateView, FormView


# Create your views here.
class IndexTemplateView(TemplateView):
    template_name = 'csas/index.html'
