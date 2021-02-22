import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from . import models


class IndexTemplateView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if settings.VUEJS_DEBUG:
            return 'events/index-dev.html'
        return 'events/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_choice_array"] = json.dumps([[c[0], str(c[1])] for c in models.Event.type_choices])
        return context
