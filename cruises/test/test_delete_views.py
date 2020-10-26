from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DeleteView

from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.views import CommonDeleteView
from cruises.test import FactoryFloor
from .. import models
from .. import views
from cruises.test.common_tests import CommonCruisesTest as CommonTest

