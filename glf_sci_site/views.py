from collections import OrderedDict

from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.translation import gettext as _


# Create your views here.
def get_app_dict(request):
    if request.user.is_authenticated:
        inventory_url = reverse('inventory:my_resource_list')
    else:
        inventory_url = reverse('inventory:resource_list')

    app_dict = {
        "inventory": {
            "title": _("Metadata Inventory"),
            "description": _("Tool for organizing and managing metadata of regional datasets and data resources."),
            "status": "production",
            "access": "open",
            "url": inventory_url,
        },
        "tickets": {
            "title": _("Data Management Tickets"),
            "description": _("Tool for submitting and tracking data management requests."),
            "status": "production",
            "access": "open",
            "url": reverse('tickets:list'),
        },
        "grais": {
            "title": _("grAIS"),
            "description": _("Gulf Region Aquatic Invasive Species application."),
            "status": "production",
            "access": "permission-required",
            "url": reverse('grais:index'),
        },
        "herring": {
            "title": _("HERmorrhage"),
            "description": _("The herring sampling and ageing application."),
            "status": "production",
            "access": "permission-required",
            "url": reverse('herring:index'),
        },
        "oceanography": {
            "title": _("Regional Oceanographic Archive"),
            "description": _("Tool for tracking the collection and processing of oceanographic data."),
            "status": "beta",
            "access": "open",
            "url": reverse('oceanography:index'),
        },
        "camp": {
            "title": _("CAMP db"),
            "description": _("Tool for organizing and managing metadata of regional datasets and data resources."),
            "status": "production",
            "access": "permission-required",
            "url": reverse('camp:index'),
        },
        "projects": {
            "title": _("Science Project Planning"),
            "description": _("Tool for the tracking, development and coordination of project work-planning."),
            "status": "production",
            "access": "login-required",
            "url": reverse('projects:index'),
        },
        "scifi": {
            "title": _("SciFi"),
            "description": _("Gulf Science finance tracking and reporting tool."),
            "status": "beta",
            "access": "permission-required",
            "url": reverse('scifi:index'),
        },
        "ihub": {
            "title": _("iHub"),
            "description": _("Indigenous Hub entry management tool."),
            "status": "beta",
            "access": "permission-required",
            "url": reverse('ihub:index'),
        },
        "masterlist": {
            "title": _("MasterList"),
            "description": _("Regional master list and consultation instructions."),
            "status": "dev",
            "access": "permission-required",
            "url": reverse('masterlist:index'),
        },
        "snowcrab": {
            "title": _("Snow Crab"),
            "description": _("front-end application for the Gulf snow crab monitoring dataset"),
            "status": "dev",
            "access": "open",
            "url": reverse('crab:index'),
        },
        "diets": {
            "title": _("Marine Diets"),
            "description": _("Stomach contents analysis database / application."),
            "status": "dev",
            "access": "permission-required",
            "url": reverse('diets:index'),
        },
        "meq": {
            "title": _("MEQ"),
            "description": _("Marine Environmental Quality (MEQ) database."),
            "status": "dev",
            "access": "open",
            "url": "#"
        },
    }

    return app_dict


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["app_dict"] = get_app_dict(self.request)
        return context
