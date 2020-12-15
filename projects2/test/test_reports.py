import os
from django.test import TestCase, tag
from django.conf import settings

from .. import reports

from ..test import FactoryFloor as FactoryFloor
from ..test.common_tests import CommonProjectTest

from shared_models import models as shared_models
from shared_models.test.SharedModelsFactoryFloor import RegionFactory, BranchFactory, DivisionFactory, SectionFactory


