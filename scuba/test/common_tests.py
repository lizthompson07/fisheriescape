import os

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.translation import activate
from faker import Faker
from html2text import html2text

from csas2.models import CSASAdminUser
from ppt.models import PPTAdminUser
from scuba.models import ScubaUser
from shared_models.test.SharedModelsFactoryFloor import UserFactory, GroupFactory
from shared_models.test.common_tests import CommonTest
from travel.models import TravelUser

faker = Faker()

class ScubaCommonTest(CommonTest):

    def get_and_login_admin(self):
        user = self.get_and_login_user()
        admin, created = ScubaUser.objects.get_or_create(user=user)
        admin.is_admin = True
        admin.save()
        return user

    def get_and_login_crud_user(self):
        user = self.get_and_login_user()
        admin, created = ScubaUser.objects.get_or_create(user=user)
        admin.is_crud_user = True
        admin.save()
        return user
