import json

from django.test import tag
from django.urls import reverse
from faker import Factory
from rest_framework import status

from shared_models.test.SharedModelsFactoryFloor import UserFactory
from shared_models.test.common_tests import CommonTest
from . import FactoryFloor
from .FactoryFloor import ObservationFactory, DiveFactory, SectionFactory

faker = Factory.create()


class TestCurrentUserAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = UserFactory()
        self.test_url = reverse("scuba-current-user", args=None)

    @tag("api", 'current-user')
    def test_url(self):
        self.assert_correct_url("scuba-current-user", test_url_args=None, expected_url_path=f"/api/scuba/user/")

    @tag("api", 'current-user')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        user = self.get_and_login_user(user=None)
        response = self.client.get(self.test_url)
        self.assertEqual(response.data["id"], user.id)
        self.assertEqual(response.data["first_name"], user.first_name)
        self.assertEqual(response.data["last_name"], user.last_name)
        self.assertEqual(response.data["username"], user.username)

    @tag("api", 'current-user')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestObservationListCreateAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.dive = DiveFactory()
        self.section = SectionFactory(dive=self.dive)
        self.observation = ObservationFactory(section=self.section)
        for i in range(0, 5):
            ObservationFactory()
        self.test_url = reverse("scuba-observation-list", args=None)

    @tag("api", 'observation-list')
    def test_url(self):
        self.assert_correct_url("scuba-observation-list", test_url_args=None, expected_url_path=f"/api/scuba/observations/")

    @tag("api", 'observation-list')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        print(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user(user=None)
        response = self.client.get(self.test_url)
        self.assertEqual(len(response.data), 6)

        # check query params
        response = self.client.get(self.test_url + f"?dive={self.dive.id}")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.observation.id)

    @tag("api", 'observation-list')
    def test_post(self):
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user(in_group="scuba_admin")
        data = ObservationFactory.get_valid_data()
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # unauthenticated users
        self.client.logout()
        self.get_and_login_user()
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user(in_group="scuba_admin")
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        keys = [
            "id",
        ]
        self.assert_dict_has_keys(response.data, keys)

    @tag("api", 'observation-list')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestObservationRetrieveUpdateDestroyAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user(in_group="scuba_admin")
        self.instance = FactoryFloor.ObservationFactory()
        self.test_url = reverse("scuba-observation-detail", args=[self.instance.pk])
        # self.client = APIClient()

    @tag("api", 'observation-detail')
    def test_url(self):
        self.assert_correct_url("scuba-observation-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/scuba/observations/{self.instance.pk}/")

    @tag("api", 'observation-detail')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user()
        response = self.client.get(self.test_url)
        self.assertEqual(response.data["id"], self.instance.id)

    @tag("api", 'observation-detail')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        data_dict = ObservationFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        data_dict = ObservationFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        self.get_and_login_user(self.user)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.data["carapace_length_mm"], data_dict["carapace_length_mm"])

        data_dict = ObservationFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        self.get_and_login_user(self.user)
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.data["carapace_length_mm"], data_dict["carapace_length_mm"])

    @tag("api", 'observation-detail')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)


class TestSectionListCreateAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user(in_group="scuba_admin")
        self.dive = DiveFactory()
        self.section = SectionFactory(dive=self.dive)
        for i in range(0, 5):
            SectionFactory()
        self.test_url = reverse("scuba-section-list", args=None)

    @tag("api", 'section-list')
    def test_url(self):
        self.assert_correct_url("scuba-section-list", test_url_args=None, expected_url_path=f"/api/scuba/sections/")

    @tag("api", 'section-list')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user(user=None)
        response = self.client.get(self.test_url)
        self.assertEqual(len(response.data), 6)

        # check query params
        response = self.client.get(self.test_url + f"?dive={self.dive.id}")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.section.id)

    @tag("api", 'section-list')
    def test_post(self):
        # PERMISSIONS
        # authenticated users
        data = SectionFactory.get_valid_data()
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # unauthenticated users
        self.client.logout()
        self.get_and_login_user()
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user(self.user)
        data = SectionFactory.get_valid_data()
        response = self.client.post(self.test_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        keys = [
            "id",
        ]
        self.assert_dict_has_keys(response.data, keys)

    @tag("api", 'section-list')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestSectionRetrieveUpdateDestroyAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user(in_group="scuba_admin")
        self.instance = FactoryFloor.SectionFactory()
        self.test_url = reverse("scuba-section-detail", args=[self.instance.pk])

    @tag("api", 'section-detail')
    def test_url(self):
        self.assert_correct_url("scuba-section-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/scuba/sections/{self.instance.pk}/")

    @tag("api", 'section-detail')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        self.get_and_login_user()
        response = self.client.get(self.test_url)
        self.assertEqual(response.data["id"], self.instance.id)

    @tag("api", 'section-detail')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        data_dict = SectionFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        data_dict = SectionFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        self.get_and_login_user(self.user)
        response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.data["depth_ft"], data_dict["depth_ft"])

        data_dict = SectionFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        self.get_and_login_user(self.user)
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.data["depth_ft"], data_dict["depth_ft"])

    @tag("api", 'section-detail')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
