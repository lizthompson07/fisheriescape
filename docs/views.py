from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.utils import timezone
from . import models
# Create your views here.

class IndexView(TemplateView):
    template_name = "docs/index.html"


class OceanographyListView(ListView):
    model = models.doc
    template_name = "docs/oceanography_doc_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
