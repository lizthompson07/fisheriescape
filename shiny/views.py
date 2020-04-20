from django.shortcuts import render

# Create your views here.
from django.templatetags.static import static
from django.utils.translation import gettext as _
from django.views.generic import TemplateView


class IndexTemplateView(TemplateView):
    template_name = 'shiny/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
                "author": "??",
                "description": _("n/a"),
                "github_url": "n/a",
                "url": "http://dmapps:3838/sustainability",
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
            # TEMPLATE
            # {
            #     "title": _(""),
            #     "author": "",
            #     "description": _(""),
            #     "url": "http://dmapps:3838/",
            #     "thumbnail": static("shiny/img/"),
            # },

        ]

        return context