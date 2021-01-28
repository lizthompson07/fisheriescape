from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Factory
from rest_framework import status

from . import FactoryFloor
from .. import models

faker = Factory.create()

