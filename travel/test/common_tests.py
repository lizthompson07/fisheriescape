import os

from django.contrib.auth.models import Group

from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.test.common_tests import CommonTest
from travel.models import TravelUser

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


# here are common tests for Travel. Essentially they will just load the travel fixutres
class CommonTravelTest(CommonTest):
    fixtures = standard_fixtures

    def setUp(self):
        super().setUp()
        Group.objects.get_or_create(name="travel_admin")
        Group.objects.get_or_create(name="travel_adm_admin")

    def get_and_login_admin(self):
        user = self.get_and_login_user()
        admin, created = TravelUser.objects.get_or_create(user=user)
        admin.is_national_admin = True
        admin.save()
        return user

    def get_and_login_cfo_user(self):
        user = self.get_and_login_user()
        admin, created = TravelUser.objects.get_or_create(user=user)
        admin.is_cfo = True
        admin.save()
        return user

    def get_and_login_regional_admin(self):
        user = self.get_and_login_user()
        admin, created = TravelUser.objects.get_or_create(user=user)
        admin.region = RegionFactory()
        admin.save()
        return user