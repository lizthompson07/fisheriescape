from datetime import datetime

from django.test import tag
from django.utils import timezone
from faker import Factory

from shared_models.test.SharedModelsFactoryFloor import SectionFactory
from . import FactoryFloor
from .. import models, utils

faker = Factory.create()

