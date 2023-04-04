from collections import OrderedDict

from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from accounts.models import Announcement


# Create your views here.


def get_app_dict(request):
    """
    This function will go through and try to connect to all apps in the project. If an app is not available
    (i.e., raising a NoReverseMatch exception it will not be included in the OrderedDict
    each object in the OrderedDict will result in a card on the website's splash page

    :param request:
    :return: ordered dictionary containing all connected apps
    """

    app_dict = {}

    if settings.SHOW_TICKETING_APP or request.user.is_staff:
        try:
            app_dict["tickets"] = {
                "title": _("DM Apps Tickets"),
                "description": _("Submit and track data management service requests."),
                "status": "production",
                "access": "open",
                "url": reverse('tickets:router'),
                "icon_path": 'img/icons/flowchart.svg',
                "region": "all",
            }
        except NoReverseMatch:
            pass

        try:
            app_dict["fisheriescape"] = {
                "title": _("Fisheries Landscape Tool"),
                "description": _("Tool for mapping fisheries landscapes for marine species at risk"),
                "status": "dev",
                "access": "login-required",
                "url": reverse('fisheriescape:index'),
                "icon_path": 'img/icons/fisheriescape.svg',
                "region": "regional",
            }
        except NoReverseMatch:
            pass

    return OrderedDict(app_dict)


class IndexView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_odict = get_app_dict(self.request)
        app_dict_shared = OrderedDict()
        app_dict_regional = OrderedDict()
        for key in app_odict:
            if app_odict[key]["region"] == "all":
                app_dict_shared[key] = app_odict[key]

            if app_odict[key]["region"] == "regional":
                app_dict_regional[key] = app_odict[key]

        context["app_dict_shared"] = app_dict_shared
        context["app_dict_regional"] = app_dict_regional
        context["app_dict"] = app_odict
        context["announcements"] = [a for a in Announcement.objects.all() if a.is_current]
        if settings.GIT_VERSION and settings.GIT_VERSION != "":
            context["git_version_number"] = settings.GIT_VERSION
        return context
