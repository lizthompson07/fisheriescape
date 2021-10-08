import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy, gettext as _

from lib.templatetags.custom_filters import nz
from res.mixins import LoginAccessRequiredMixin, ResAdminRequiredMixin, ResCRUDAccessRequiredMixin
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonUpdateView, CommonCreateView, \
    CommonDeleteView, CommonDetailView, CommonFormView
from . import models, forms, filters, reports


class IndexTemplateView(LoginAccessRequiredMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'res/index.html'

