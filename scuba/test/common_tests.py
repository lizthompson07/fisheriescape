from faker import Faker

from scuba.models import ScubaUser
from shared_models.test.common_tests import CommonTest

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
