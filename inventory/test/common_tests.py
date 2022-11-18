import os

from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.test.common_tests import CommonTest
from ..models import InventoryUser

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


# here are common tests for Travel. Essentially they will just load the travel fixutres
class CommonInventoryTest(CommonTest):
    fixtures = standard_fixtures

    def get_and_login_user(self, user=None, in_group=None, is_superuser=False, is_admin=False, is_regional_admin=False, is_read_only=False):
        user = super().get_and_login_user(user, in_group, is_superuser)
        if is_read_only:
            InventoryUser.objects.get_or_create(user=user)
        else:
            if is_admin:
                u = InventoryUser.objects.get_or_create(user=user)[0]
                u.is_admin = True
                u.save()
            if is_regional_admin:
                u = InventoryUser.objects.get_or_create(user=user)[0]
                region = RegionFactory()
                u.region = region
                u.save()
        return user
