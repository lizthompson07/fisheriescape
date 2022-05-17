import json

from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse
from rest_framework import status

from shared_models.test import SharedModelsFactoryFloor as FactoryFloor
from shared_models.test.common_tests import CommonTest, get_random_admin_user


class TestUserAPIListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = self.get_and_login_user()
        self.admin_user = get_random_admin_user()
        self.test_list_create_url = reverse("user-list", args=None)
        self.test_detail_url = reverse("user-detail", args=[self.instance.pk])
        data_dict = FactoryFloor.UserFactory.get_valid_data()
        self.data_json = json.dumps(data_dict)

    @tag("api", 'user')
    def test_url(self):
        self.assert_correct_url("user-list", test_url_args=None, expected_url_path=f"/api/shared/viewsets/users/")
        self.assert_correct_url("user-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/shared/viewsets/users/{self.instance.pk}/")

    @tag("api", 'user')
    def test_list_create(self):
        # LIST
        # anonymous user
        self.client.logout()
        response = self.client.get(self.test_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # random authenticated users
        self.get_and_login_user()
        response = self.client.get(self.test_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # CREATE
        # anonymous user
        self.client.logout()
        response = self.client.post(self.test_list_create_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # random authenticated users
        self.get_and_login_user()
        response = self.client.post(self.test_list_create_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # authorized user
        self.get_and_login_user(user=self.admin_user)
        response = self.client.post(self.test_list_create_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @tag("api", 'user')
    def test_put_patch_delete(self):
        # PUT
        # anonymous user
        self.client.logout()
        response = self.client.put(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # random authenticated users
        self.get_and_login_user()
        response = self.client.put(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # authorized user
        self.get_and_login_user(user=self.admin_user)
        response = self.client.put(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)


        # PATCH
        # anonymous user
        self.client.logout()
        response = self.client.patch(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # random authenticated users
        self.get_and_login_user()
        response = self.client.patch(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # authorized user
        self.get_and_login_user(user=self.admin_user)
        response = self.client.patch(self.test_detail_url, data=self.data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)


        # DELETE
        # anonymous user
        self.client.logout()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # random authenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # authorized user
        self.get_and_login_user(user=self.admin_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.instance.pk).exists())