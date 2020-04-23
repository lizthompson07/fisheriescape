from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, ListView, DeleteView, CreateView, UpdateView
from . import models
from . import forms


class IndexTemplateView(ListView):
    template_name = 'shiny/index.html'
    model = models.App

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            "thumbnail| ",
            "ttitle|{}".format(_("title")),
            "tdescription|{}".format(_("description")),
            "github_url",
            "owner",
            "last_modified",
        ]
        context['apps'] = [
            # Restigouche Salmon
            {
                "title": _("Juvenile Atlantic Salmon Densities in the Restigouche Watershed"),
                "author": "Guillaume Dauphin",
                "description": _("n/a"),
                "github_url": "n/a",
                "url": "http://dmapps:3838/restigouche",
                "thumbnail": static("shiny/img/salmon.jpg"),
            },

            # trawl sustainability
            {
                "title": _("2018 Sustainability Survey Viewer"),
                "author": "Jason Ladell",
                "description": _(
                    "This application was designed to convert data included in the results of the 2018 Sustainability Survey into a more easily readable format that can be filtered by specific stocks, regions, and/or species groups."),
                "github_url": "https://github.com/NCR-FPS/2018.SS.Viewer",
                "url": "http://dmapps:3838/2018.SS.Viewer",
                "thumbnail": static("shiny/img/trawl.jpg"),
            },

            # DFO/TC Right Whale Sightings Trigger Analysis
            {
                "title": _("DFO/TC Right Whale Sightings Trigger Analysis"),
                "author": "leeyuhc",
                "description": _("n/a"),
                "github_url": "https://github.com/leeyuhc/DFO_dyna",
                "url": "http://dmapps:3838/DFO_dyna",
                "thumbnail": static("shiny/img/narw.jfif"),
            },
            # NARW Identification Tool
            {
                "title": _("NARW Identification Tool"),
                "author": "Liz Thompson",
                "description": _("For helping to identify whales quickly in the Gulf Region"),
                "github_url": "n/a",
                "url": "http://dmapps:3838/DFO_IDapp",
                "thumbnail": static("shiny/img/narw.jfif"),
            },

        ]

        return context


class AppUpdateView(LoginRequiredMixin, UpdateView):
    model = models.App
    form_class = forms.AppForm
    success_url = reverse_lazy('shiny:index')
    template_name = 'shiny/app_form.html'


class AppCreateView(LoginRequiredMixin, CreateView):
    model = models.App
    form_class = forms.AppForm
    success_url = reverse_lazy('shiny:index')
    template_name = 'shiny/app_form.html'

    def get_initial(self):
        return {
            "owner": self.request.user
        }


class AppDeleteView(LoginRequiredMixin, DeleteView):
    model = models.App
    success_url = reverse_lazy('shiny:index')
    success_message = 'The app record was successfully deleted!'
    template_name = 'shiny/app_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
