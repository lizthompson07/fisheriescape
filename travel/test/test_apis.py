import json
from datetime import timedelta

from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status

from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest

faker = Faker()


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

    @tag("api", 'trip')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user(user=self.adm_admin_user)
        data_dict = FactoryFloor.TripFactory.get_valid_data()
        # make sure that adm approval status doesnt change
        data_dict["is_adm_approval_required"] = self.instance.is_adm_approval_required

        data_json = json.dumps(data_dict)
        response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=self.admin_user)

        my_status = status.HTTP_403_FORBIDDEN if self.instance.is_adm_approval_required else status.HTTP_200_OK
        response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, my_status)
        response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, my_status)

    @tag("api", 'trip')
    def test_delete(self):
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user(user=self.adm_admin_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.instance = FactoryFloor.TripFactory()
        self.test_detail_url = reverse("trip-detail", args=[self.instance.pk])
        self.client.logout()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=self.admin_user)
        my_status = status.HTTP_403_FORBIDDEN if self.instance.is_adm_approval_required else status.HTTP_204_NO_CONTENT
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, my_status)


class TestTripRequestAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.admin_user = self.get_and_login_user(in_group="travel_admin")
        self.adm_admin_user = self.get_and_login_user(in_group="travel_adm_admin")
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_list_url = reverse("triprequest-list", args=None)
        self.test_detail_url = reverse("triprequest-detail", args=[self.instance.pk])

    @tag("api", 'request')
    def test_url(self):
        self.assert_correct_url("triprequest-list", test_url_args=None, expected_url_path=f"/api/travel/requests/")
        self.assert_correct_url("triprequest-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/travel/requests/{self.instance.pk}/")

    @tag("api", 'request')
    def test_get(self):
        # PERMISSIONS
        # detail
        # authenticated users
        # the following should be eligible to view
        owner = self.instance.created_by
        traveller = FactoryFloor.TravellerFactory(request=self.instance).user
        manager1 = self.instance.section.head
        manager2 = self.instance.section.division.head
        admin1 = self.instance.section.admin
        admin2 = self.instance.section.division.admin
        users = [owner, traveller, manager1, manager2, admin1, admin2]
        # pick a random user
        user = users[faker.pyint(0, len(users) - 1)]
        self.get_and_login_user(user=user)
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)
        # let's make sure this is the same even after the request is submitted
        self.instance.submit()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)

    #     response = self.client.get(self.test_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # unauthenticated users
    #     self.client.logout()
    #     response = self.client.get(self.test_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     response = self.client.get(self.test_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #
    #     # RESPONSE DATA
    #     # here is the cast of requests
    #     self.get_and_login_user(user=self.user)
    #     # make this a request in the future
    #     request1 = self.instance
    #     request1.start_date = timezone.now() + timedelta(days=366)
    #     request1.is_adm_approval_required = True
    #     request1.save()
    #     # request in the past
    #     request2 = FactoryFloor.TripRequestFactory(start_date=timezone.now() - timedelta(days=366), is_adm_approval_required=True)
    #     # regional in the past
    #     request3 = FactoryFloor.TripRequestFactory(start_date=timezone.now() - timedelta(days=366), is_adm_approval_required=False)
    #
    #     # a regular user should not be able to see anything other than upcoming requests
    #     response1 = self.client.get(f'{self.test_list_url}')
    #     response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
    #     response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
    #     response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
    #     response5 = self.client.get(f'{self.test_list_url}?all=true')
    #     self.assertEqual(len(response1.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response2.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response3.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response4.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response5.data["results"]), 1)  # upcoming requests
    #
    #     # admin user
    #     self.get_and_login_user(user=self.admin_user)
    #     response1 = self.client.get(f'{self.test_list_url}')
    #     response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
    #     response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
    #     response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
    #     response5 = self.client.get(f'{self.test_list_url}?all=true')
    #     self.assertEqual(len(response1.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response2.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response3.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response4.data["results"]), 1)  # real
    #     self.assertEqual(len(response5.data["results"]), 3)  # real
    #
    #     # adm admin user
    #     self.get_and_login_user(user=self.adm_admin_user)
    #     response1 = self.client.get(f'{self.test_list_url}')
    #     response2 = self.client.get(f'{self.test_list_url}?adm-verification=true')
    #     response3 = self.client.get(f'{self.test_list_url}?adm-hit-list=true')
    #     response4 = self.client.get(f'{self.test_list_url}?regional-verification=true')
    #     response5 = self.client.get(f'{self.test_list_url}?all=true')
    #     self.assertEqual(len(response1.data["results"]), 1)  # upcoming requests
    #     self.assertEqual(len(response2.data["results"]), 2)  # real
    #     self.assertEqual(len(response3.data["results"]), 0)  # real
    #     self.assertEqual(len(response4.data["results"]), 1)  # real
    #     self.assertEqual(len(response5.data["results"]), 3)  # real
    #
    #     # when there is a regular for a specific instance
    #     self.get_and_login_user(user=self.user)
    #     response = self.client.get(f'{self.test_detail_url}')
    #     self.assertEqual(response.data["id"], request1.id)
    #
    # @tag("api", 'request')
    # def test_post(self):
    #     """ The post method is not used for creating requests, but instead for resetting reviewers.
    #     Since request reviews only happen on ADM requests, only adm admin should be allow to do this action """
    #     # PERMISSIONS
    #     # authenticated users
    #     self.get_and_login_user(user=self.adm_admin_user)
    #     response1 = self.client.post(f'{self.test_detail_url}')
    #     response2 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
    #     self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
    #     request = self.instance
    #     request.status = 42
    #     request.save()
    #     response3 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
    #     self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     # unauthenticated users
    #     request = self.instance
    #     request.status = 30
    #     request.save()
    #     self.get_and_login_user(user=self.admin_user)
    #     response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.get_and_login_user()
    #     response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    # @tag("api", 'request')
    # def test_put_patch(self):
    #     # PERMISSIONS
    #     # authenticated users
    #     self.get_and_login_user(user=self.adm_admin_user)
    #     data_dict = FactoryFloor.TripRequestFactory.get_valid_data()
    #     # make sure that adm approval status doesnt change
    #     data_dict["is_adm_approval_required"] = self.instance.is_adm_approval_required
    #
    #     data_json = json.dumps(data_dict)
    #     response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # unauthenticated users
    #     self.client.logout()
    #     response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.get_and_login_user()
    #     response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.get_and_login_user(user=self.admin_user)
    #
    #     my_status = status.HTTP_403_FORBIDDEN if self.instance.is_adm_approval_required else status.HTTP_200_OK
    #     response = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, my_status)
    #     response = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
    #     self.assertEqual(response.status_code, my_status)
    #
    # @tag("api", 'request')
    # def test_delete(self):
    #     # PERMISSIONS
    #     # authenticated users
    #     self.get_and_login_user(user=self.adm_admin_user)
    #     response = self.client.delete(self.test_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     # unauthenticated users
    #     self.instance = FactoryFloor.TripRequestFactory()
    #     self.test_detail_url = reverse("request-detail", args=[self.instance.pk])
    #     self.client.logout()
    #     response = self.client.delete(self.test_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.get_and_login_user()
    #     response = self.client.delete(self.test_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.get_and_login_user(user=self.admin_user)
    #     my_status = status.HTTP_403_FORBIDDEN if self.instance.is_adm_approval_required else status.HTTP_204_NO_CONTENT
    #     response = self.client.delete(self.test_detail_url)
    #     self.assertEqual(response.status_code, my_status)
