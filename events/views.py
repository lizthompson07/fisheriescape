import json
import os
from copy import deepcopy

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy, get_language
from django.views.generic import TemplateView

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.views import CommonTemplateView, CommonCreateView, \
    CommonDetailView, CommonFilterView, CommonDeleteView, CommonUpdateView, CommonListView, CommonHardDeleteView, CommonFormsetView, CommonFormView
from . import filters, forms, models, reports



class IndexTemplateView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if settings.VUEJS_DEBUG:
            return 'events/index-dev.html'
        return 'events/index.html'
