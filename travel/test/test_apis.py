from datetime import timedelta

from django.test import tag
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest


class TestTripAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.admin_user = self.get_and_login_user(in_group="travel_admin")
        self.adm_admin_user = self.get_and_login_user(in_group="travel_adm_admin")
        self.instance = FactoryFloor.TripFactory()
        self.test_list_url = reverse("trip-list", args=None)
        self.test_detail_url = reverse("trip-detail", args=[self.instance.pk])

    @tag("api", 'trip')
    def test_url(self):
        self.assert_correct_url("trip-list", test_url_args=None, expected_url_path=f"/api/travel/trips/")
        self.assert_correct_url("trip-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/travel/trips/{self.instance.pk}/")

    @tag("api", 'trip')
    def test_get(self):
        # PERMISSIONS
        # list and detail
        # authenticated users
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        # here is the cast of trips
        self.get_and_login_user(user=self.user)
        # make this a trip in the future
        trip1 = self.instance
        trip1.start_date = timezone.now() + timedelta(days=366)
        trip1.is_adm_approval_required = True
        trip1.save()
        # trip in the past
        trip2 = FactoryFloor.TripFactory(start_date=timezone.now() - timedelta(days=366), is_adm_approval_required=True)
        # regional in the past
        trip3 = FactoryFloor.TripFactory(start_date=timezone.now() - timedelta(days=366), is_adm_approval_required=False)

        # a regular user should not be able to see anything other than upcoming trips
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
        response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
        response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
        response5 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response2.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response3.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response4.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response5.data["results"]), 1)  # upcoming trips

        # admin user
        self.get_and_login_user(user=self.admin_user)
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
        response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
        response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
        response5 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response2.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response3.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response4.data["results"]), 1)  # real
        self.assertEqual(len(response5.data["results"]), 3)  # real

        # adm admin user
        self.get_and_login_user(user=self.adm_admin_user)
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
        response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
        response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
        response5 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 1)  # upcoming trips
        self.assertEqual(len(response2.data["results"]), 2)  # real
        self.assertEqual(len(response3.data["results"]), 0)  # real
        self.assertEqual(len(response4.data["results"]), 1)  # real
        self.assertEqual(len(response5.data["results"]), 3)  # real

        # when there is a regular for a specific instance
        self.get_and_login_user(user=self.user)
        response = self.client.get(f'{self.test_detail_url}')
        self.assertEqual(response.data["id"], trip1.id)


    @tag("api", 'trip')
    def test_post(self):
        """ The post method is not used for creating trips, but instead for resetting reviewers.
        Since trip reviews only happen on ADM trips, only adm admin should be allow to do this action """
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user(user=self.adm_admin_user)
        response1 = self.client.post(f'{self.test_detail_url}')
        response2 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        trip = self.instance
        trip.status = 42
        trip.save()
        response3 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        # unauthenticated users
        trip = self.instance
        trip.status = 30
        trip.save()
        self.get_and_login_user(user=self.admin_user)
        response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #
    # @tag("api", 'trip')
    # def test_put_patch(self):
    #     # PERMISSIONS
    #     # authenticated users
    #     data_dict = TripFactoryFactory.get_valid_data()
    #     data_json = json.dumps(data_dict)
    #     response = self.client.put(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # unauthenticated users
    #     self.client.logout()
    #     response = self.client.put(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     # RESPONSE DATA
    #     data_dict = ObservationFactory.get_valid_data()
    #     data_json = json.dumps(data_dict)
    #     self.get_and_login_user(self.user)
    #     response = self.client.patch(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.data["is_adm_approval_required"], data_dict["carapace_length_mm"])
    #
    #     data_dict = ObservationFactory.get_valid_data()
    #     data_json = json.dumps(data_dict)
    #     self.get_and_login_user(self.user)
    #     response = self.client.put(self.test_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.data["is_adm_approval_required"], data_dict["carapace_length_mm"])
    #
    # @tag("api", 'trip')
    # def test_unallowed_methods_only(self):
    #     restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
    #     self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
    #     self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
    #     self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
    #     self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestModelAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ModelFactory()
        self.test_url = reverse("model", args=None)

    @tag("api", 'model')
    def test_url(self):
        self.assert_correct_url("model", test_url_args=None, expected_url_path=f"/api/URL/{self.instance.pk}/")

    @tag("api", 'model')
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
        valid_user = None
        self.get_and_login_user(user=None)
        response = self.client.get(self.test_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.instance.id)
        # or, for lists with pagination...
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.instance.id)

        # check query params
        object = FactoryFloor.Factory()
        data = self.client.get(self.test_url + f"?={object.id}").data
        keys.extend([
            "",
        ])
        self.assert_dict_has_keys(data, keys)

    @tag("api", 'model')
    def test_post(self):
        # PERMISSIONS
        # authenticated users
        response = self.client.post(self.test_url, data=FactoryFloor.ModelFactory.get_valid_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # unauthenticated users
        self.client.logout()
        response = self.client.post(self.test_url, data=FactoryFloor.ModelFactory.get_valid_data())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # RESPONSE DATA
        valid_user = None
        self.get_and_login_user(user=None)
        response = self.client.post(self.test_url, data=FactoryFloor.ModelFactory.get_valid_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        keys = [
            "id",
        ]
        self.assert_dict_has_keys(response.data, keys)

    @tag("api", 'model')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        data_dict = Factory.get_valid_data()
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
        self.assertEqual(response.data["my_random_field_to_spot_check"], data_dict["carapace_length_mm"])

        data_dict = ObservationFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        self.get_and_login_user(self.user)
        response = self.client.put(self.test_url, data=data_json, content_type="application/json")
        self.assertEqual(response.data["my_random_field_to_spot_check"], data_dict["carapace_length_mm"])

    @tag("api", 'model')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)
