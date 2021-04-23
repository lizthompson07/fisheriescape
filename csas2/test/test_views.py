from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.test.common_tests import CommonTest
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView, \
    CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView
from . import FactoryFloor
from .. import views, models

faker = Factory.create()
