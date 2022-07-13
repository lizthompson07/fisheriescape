import os

from shared_models.test.common_tests import CommonTest
from ..models import iHubUser
fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


# here are common tests for Travel. Essentially they will just load the travel fixutres
class CommonIHubTest(CommonTest):
    fixtures = standard_fixtures

    def get_and_login_user(self, user=None, in_group=None, is_superuser=False, is_admin=False, is_crud_user=False):
        user = super().get_and_login_user(user, in_group, is_superuser)
        if is_admin:
            ihub_user = iHubUser.objects.get_or_create(user=user)[0]
            ihub_user.is_admin = True
            ihub_user.save()
        if is_crud_user:
            ihub_user = iHubUser.objects.get_or_create(user=user)[0]
            ihub_user.is_crud_user = True
            ihub_user.save()
        return user
