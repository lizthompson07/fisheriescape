from django.urls import reverse_lazy
from django.test import tag

import shared_models
from whalebrary import models
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from faker import Faker

faker = Faker()


