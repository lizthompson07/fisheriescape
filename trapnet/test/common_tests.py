from faker import Faker

from shared_models.test.common_tests import CommonTest
from trapnet.models import TrapNetUser

faker = Faker()


class TrapnetCommonTest(CommonTest):

    def get_and_login_admin(self):
        user = self.get_and_login_user()
        admin, created = TrapNetUser.objects.get_or_create(user=user)
        admin.is_admin = True
        admin.save()
        return user

    def get_and_login_crud_user(self):
        user = self.get_and_login_user()
        admin, created = TrapNetUser.objects.get_or_create(user=user)
        admin.is_crud_user = True
        admin.save()
        return user
