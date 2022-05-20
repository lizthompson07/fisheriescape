import os

from ppt import models
from ppt.test.FactoryFloor import ServiceFactory
from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.test.common_tests import CommonTest

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


# here are common tests for Travel. Essentially they will just load the travel fixutres
class CommonProjectTest(CommonTest):
    fixtures = standard_fixtures

    def get_and_login_user(self, user=None, in_group=None, is_superuser=False, in_national_admin_group=False, in_regional_admin_group=False,
                           is_service_coordinator=False):
        user = super().get_and_login_user(user, in_group, is_superuser, in_national_admin_group)
        if in_national_admin_group:
            ppt_user = models.PPTAdminUser.objects.get_or_create(user=user)[0]
            ppt_user.is_national_admin = True
            ppt_user.save()
        if in_regional_admin_group:
            ppt_user = models.PPTAdminUser.objects.get_or_create(user=user)[0]
            ppt_user.region = RegionFactory()
            ppt_user.save()
        if is_service_coordinator:
            ServiceFactory(coordinator=user)
        return user
