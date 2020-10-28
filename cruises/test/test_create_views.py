from django.urls import reverse_lazy
from django.test import tag
from django.utils import timezone
from django.views.generic import CreateView

from shared_models.test.SharedModelsFactoryFloor import SectionFactory, BranchFactory
from shared_models.views import CommonCreateView
from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from .. import views
from .. import models

