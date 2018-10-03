from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy
from . import models
from . import forms
# Create your views here.

class IndexTemplateView(TemplateView):
    template_name = "oceanography/index.html"

class DocListView(ListView):
    model = models.Doc
    template_name = "oceanography/doc_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class DocCreateView(CreateView):
    model = models.Doc
    template_name = "oceanography/doc_form.html"
    form_class = forms.DocForm
    success_url = reverse_lazy("oceanography:doc_list")

class DocUpdateView(UpdateView):
    model = models.Doc
    template_name = "oceanography/doc_form.html"
    form_class = forms.DocForm
    success_url = reverse_lazy("oceanography:doc_list")

class MissionYearListView(TemplateView):
    template_name = "oceanography/mission_year_list.html"

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)


        # create a reference list of years
        season_list = []
        for item in models.Mission.objects.values("season").distinct():
            season_list.append(item["season"])

        context["season_list"] = season_list
        return context


class MissionListView(ListView):
    template_name = "oceanography\mission_list.html"

    def get_queryset(self):
        return models.Mission.objects.filter(season = self.kwargs["year"])


class MissionDetailView(UpdateView):
    template_name = "oceanography\mission_form.html"
    model = models.Mission
    form_class = forms.MissionForm

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)

        context["editable"] = False
        return context
