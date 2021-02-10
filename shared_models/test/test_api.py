from django.test import tag
from django.urls import reverse
from rest_framework import status

from shared_models.test import SharedModelsFactoryFloor as FactoryFloor
from shared_models.test.common_tests import CommonTest


class TestUserAPIListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.test_url = reverse("user-list", args=None)

    @tag("api", 'user')
    def test_url(self):
        self.assert_correct_url("user-list", test_url_args=None, expected_url_path=f"/api/shared/users/")

    @tag("api", 'user')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # TODO: build up this test!
        # # RESPONSE DATA
        # valid_user = None
        # self.get_and_login_user(user=None)
        # response = self.client.get(self.test_url)
        # self.assertEqual(len(response.data), 1)
        # self.assertEqual(response.data[0]["id"], self.instance.id)
        # # or, for lists with pagination...
        # self.assertEqual(len(data["results"]), 1)
        # self.assertEqual(data["results"][0]["id"], self.instance.id)
        # 
        # # check query params
        # object = FactoryFloor.UserFactory()
        # data = self.client.get(self.test_url+f"?={object.id}").data
        # keys.extend([
        #     "",
        # ])
        # self.assert_dict_has_keys(data, keys)

    @tag("api", 'user')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)
