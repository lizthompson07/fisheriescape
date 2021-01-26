from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Factory
from rest_framework import status

from . import BioFactoryFloor
from .. import models
from shared_models.test.common_tests import CommonTest

faker = Factory.create()


@tag("api", 'current-user')
class TestCurrentUser(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.test_url = reverse("current-user")

    def test_url(self):
        self.assert_correct_url("current-user", expected_url_path=f"/api/bio_diversity/user/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data
        keys = ["id", "first_name", "last_name", "username", "is_admin"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)

