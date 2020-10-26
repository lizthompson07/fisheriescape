from django.urls import reverse_lazy
from django.test import tag
from django.utils import timezone
from django.utils.translation import activate
from django.views.generic import CreateView, UpdateView, FormView

from shared_models.views import CommonUpdateView
from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from .. import views
from .. import models
from faker import Faker

faker = Faker()

