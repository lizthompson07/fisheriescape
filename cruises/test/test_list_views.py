from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView

from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.views import CommonFilterView, CommonListView
from cruises.test import FactoryFloor
from .. import models
from .. import views
from cruises.test.common_tests import CommonCruisesTest as CommonTest

