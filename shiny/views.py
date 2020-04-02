from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class IndexTemplateView(TemplateView):
    template_name = 'shiny/index.html'