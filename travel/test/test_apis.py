import json
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status

from shared_models.models import Region
from shared_models.test.SharedModelsFactoryFloor import UserFactory
from travel import models
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
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        trip = self.instance
        trip.status = [31, 32, 43][faker.pyint(0, 2)]
        trip.save()
        response3 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        # unauthenticated users
        trip = self.instance
        trip.status = [30, 41][faker.pyint(0, 1)]
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
        authorized_user = users[faker.pyint(0, len(users) - 1)]
        self.get_and_login_user(user=authorized_user)
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)
        # let's make sure this is the same even after the request is submitted
        self.instance.submit()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)
        self.get_and_login_user()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # list
        # cast of requests
        request1 = self.instance
        request2 = FactoryFloor.TripRequestFactory(section=self.instance.section)
        request3 = FactoryFloor.TripRequestFactory()

        # regular user; should only see 1 request
        self.get_and_login_user(user=owner)
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 1)  # related requests
        self.assertEqual(len(response2.data["results"]), 1)  # related requests
        self.assertEqual(self.instance.id, response1.data["results"][0]["id"])

        self.get_and_login_user(user=manager1)
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 0)  # related requests
        self.assertEqual(len(response2.data["results"]), 2)  # managerial access

        self.get_and_login_user(in_group="travel_admin")
        response1 = self.client.get(f'{self.test_list_url}')
        response2 = self.client.get(f'{self.test_list_url}?all=true')
        self.assertEqual(len(response1.data["results"]), 0)  # related requests
        self.assertEqual(len(response2.data["results"]), 3)  # managerial access

    @tag("api", 'request')
    def test_post(self):
        """ The post method is not used for creating requests, but instead for resetting reviewers. """
        # PERMISSIONS
        # authenticated users
        request = self.instance
        owner = request.created_by
        traveller = FactoryFloor.TravellerFactory(request=request).user
        request.status = 8
        request.save()
        self.get_and_login_user(user=[self.adm_admin_user, self.admin_user, owner, traveller][faker.pyint(0, 3)])
        response1 = self.client.post(f'{self.test_detail_url}')
        response2 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        request.status = [17, 12, 14, 15, 16, 10, 11, 22, ][faker.pyint(0, 7)]
        request.save()
        response3 = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        # unauthenticated users
        request = self.instance
        request.status = 8
        request.save()
        self.get_and_login_user()
        response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.post(f'{self.test_detail_url}?reset_reviewers=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'request')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.created_by
        traveller = FactoryFloor.TravellerFactory(request=self.instance).user
        users = [owner, traveller, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        data_dict = FactoryFloor.TripRequestFactory.get_valid_data()
        del data_dict["section"]  # avoiding having to deal with section dict
        data_json = json.dumps(data_dict)
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

    @tag("api", 'request')
    def test_delete(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.created_by
        traveller = FactoryFloor.TravellerFactory(request=self.instance).user
        users = [owner, traveller, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # unauthenticated users
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_detail_url = reverse("triprequest-detail", args=[self.instance.pk])
        self.client.logout()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=self.admin_user)


class TestTravellerAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.admin_user = self.get_and_login_user(in_group="travel_admin")
        self.adm_admin_user = self.get_and_login_user(in_group="travel_adm_admin")
        self.instance = FactoryFloor.TravellerFactory()
        self.test_list_url = reverse("traveller-list", args=None)
        self.test_detail_url = reverse("traveller-detail", args=[self.instance.pk])

    @tag("api", 'request')
    def test_url(self):
        self.assert_correct_url("traveller-list", test_url_args=None, expected_url_path=f"/api/travel/travellers/")
        self.assert_correct_url("traveller-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/travel/travellers/{self.instance.pk}/")

    @tag("api", 'request')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # related requests

        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'request')
    def test_post(self):
        """ this is a loaded method... """

        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        users = [owner, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 2)])
        data_dict = FactoryFloor.TravellerFactory.get_valid_data()
        data_dict["request"] = self.instance.request.id
        data_dict["start_date"] = self.instance.request.trip.start_date.strftime("%Y-%m-%d %H:%M")
        data_dict["end_date"] = self.instance.request.trip.end_date.strftime("%Y-%m-%d %H:%M")
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # clean up the traveller
        t = get_object_or_404(models.Traveller, pk=response.data["id"])
        t.delete()

        # unauthenticated users
        self.client.logout()
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # SPECIAL OPERATIONS:
        # populate all costs
        traveller = self.instance
        request = traveller.request

        # these do not have to be anyone in particular.
        self.get_and_login_user()
        self.assertTrue(traveller.costs.count() == 0)
        response = self.client.post(f'{self.test_detail_url}?populate_all_costs=true')
        self.assertTrue(traveller.costs.count() > 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # clear_empty_costs
        cost = traveller.costs.first()
        cost.amount_cad = 100
        cost.save()
        response = self.client.post(f'{self.test_detail_url}?clear_empty_costs=true')
        self.assertTrue(traveller.costs.count() == 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # CHERRY PICKING --> while this is a util, we will test the func here out of
        # convenience since the func requires a wsgi request object.

        # first let's make sure it is only adm who can access this view:
        bad_users = [self.adm_admin_user, self.admin_user, traveller.user]
        adm1 = UserFactory()
        national_branch, created = Region.objects.get_or_create(name="national")
        national_branch.head = adm1
        national_branch.save()
        adm2 = UserFactory()
        models.DefaultReviewer.objects.get_or_create(user=adm2, special_role=5)
        good_users = [adm1, adm2]
        bad_user = bad_users[faker.pyint(0, len(bad_users) - 1)]
        good_user = good_users[faker.pyint(0, len(good_users) - 1)]
        self.get_and_login_user(user=bad_user)
        response = self.client.post(f'{self.test_detail_url}?cherry_pick_approval=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=good_user)
        self.assertNotEqual(request.status, 14)
        response = self.client.post(f'{self.test_detail_url}?cherry_pick_approval=true')
        # we are expecting a 400 since the trip request is not in the correct status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # set the status of the trip to PENDING ADM and make sure there is a current reviewer ready to go
        request.status = 14
        request.save()
        reviewer = FactoryFloor.ReviewerFactory(request=request, status=1)
        self.assertEqual(request.current_reviewer, reviewer)
        # We have to test two scenarios. 1) single traveller request 2) group request
        # SCENARIO 1:
        self.assertEqual(request.travellers.count(), 1)
        response = self.client.post(f'{self.test_detail_url}?cherry_pick_approval=true')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # check the status of the reviewer
        reviewer = get_object_or_404(models.Reviewer, pk=reviewer.pk)
        self.assertEqual(reviewer.status, 2)
        self.assertIn("approved", reviewer.comments.lower())
        self.assertIsNotNone(reviewer.status_date)

        # SCENARIO 2:
        traveller = FactoryFloor.TravellerFactory()
        self.test_detail_url = reverse("traveller-detail", args=[traveller.pk])
        request = traveller.request
        request.status = 14
        request.save()
        self.assertIn(traveller, request.travellers.all())
        for i in range(0, 10):
            FactoryFloor.TravellerFactory(request=request)
        reviewer1 = FactoryFloor.ReviewerFactory(request=request, status=1)
        my_comment = faker.text()
        reviewer2 = FactoryFloor.ReviewerFactory(request=request, status=2, comments=my_comment)
        self.assertEqual(request.current_reviewer, reviewer1)
        response = self.client.post(f'{self.test_detail_url}?cherry_pick_approval=true')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # refresh the traveller
        traveller = get_object_or_404(models.Traveller, pk=traveller.pk)

        # now here is where things get a bit complicated
        # the original request has been cloned and the traveller moved to the new request
        self.assertNotIn(traveller, request.travellers.all())
        self.assertIn(traveller, traveller.request.travellers.all())
        self.assertEqual(traveller.request.travellers.count(), 1)
        # the new request should have two reviewers
        self.assertEqual(traveller.request.reviewers.count(), 2)
        self.assertNotEqual(traveller.request.current_reviewer, reviewer1)
        for r in traveller.request.reviewers.all():
            self.assertEqual(r.status, 2)
        # finally, make sure that there is a reviewer on the new request that matches with reviewer2
        r2 = traveller.request.reviewers.get(user=reviewer2.user)
        self.assertEqual(r2.comments, my_comment)

    @tag("api", 'request')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        traveller_user = self.instance.user
        users = [owner, traveller_user, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        data_dict = FactoryFloor.TravellerFactory.get_valid_data()
        data_dict["request"] = self.instance.request.id
        data_dict["user"] = self.instance.user.id  # keep the same user otherwise might loose permissions!
        data_dict["start_date"] = self.instance.request.trip.start_date.strftime("%Y-%m-%d %H:%M")
        data_dict["end_date"] = self.instance.request.trip.end_date.strftime("%Y-%m-%d %H:%M")
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

    @tag("api", 'request')
    def test_delete(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        traveller_user = self.instance.user
        users = [owner, traveller_user, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # unauthenticated users
        self.instance = FactoryFloor.TravellerFactory()
        self.test_detail_url = reverse("traveller-detail", args=[self.instance.pk])
        self.client.logout()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=self.admin_user)


class TestReviewerAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.admin_user = self.get_and_login_user(in_group="travel_admin")
        self.adm_admin_user = self.get_and_login_user(in_group="travel_adm_admin")
        reviewer = FactoryFloor.ReviewerFactory()
        request = reviewer.request
        request.status = 17
        request.save()
        reviewer.status = 1
        reviewer.save()
        self.instance = reviewer

        self.test_list_url = reverse("reviewer-list", args=None)
        self.test_detail_url = reverse("reviewer-detail", args=[self.instance.pk])

    @tag("api", 'request')
    def test_url(self):
        self.assert_correct_url("reviewer-list", test_url_args=None, expected_url_path=f"/api/travel/request-reviewers/")
        self.assert_correct_url("reviewer-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/travel/request-reviewers/{self.instance.pk}/")

    @tag("api", 'request')
    def test_get(self):
        # PERMISSIONS
        # authenticated users
        self.get_and_login_user()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.instance.id)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # related requests reviewers
        self.get_and_login_user(user=self.instance.user)  # log in with reviewer user
        response = self.client.get(self.test_list_url)
        self.assertEqual(len(response.data), 1)  # related requests reviewers

        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # SPECIAL OPERATION -- > get RDG reviewer instances
        self.client.logout()
        response = self.client.get(f'{self.test_list_url}?rdg=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.get(f'{self.test_list_url}?rdg=true')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=[self.admin_user, self.adm_admin_user][faker.pyint(0, 1)])
        response = self.client.get(f'{self.test_list_url}?rdg=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'request')
    def test_post(self):

        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        users = [owner, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 2)])
        data_dict = FactoryFloor.ReviewerFactory.get_valid_data()
        data_dict["request"] = self.instance.request.id
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.client.logout()
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'request')
    def test_put_patch(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        reviewer_user = self.instance.user
        users = [owner, reviewer_user, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        data_dict = FactoryFloor.ReviewerFactory.get_valid_data()
        data_dict["request"] = self.instance.request.id
        data_dict["user"] = self.instance.user.id  # keep the same user otherwise might loose permissions!
        data_dict["start_date"] = self.instance.request.trip.start_date.strftime("%Y-%m-%d %H:%M")
        data_dict["end_date"] = self.instance.request.trip.end_date.strftime("%Y-%m-%d %H:%M")
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

    @tag("api", 'request')
    def test_delete(self):
        # PERMISSIONS
        # authenticated users
        owner = self.instance.request.created_by
        reviewer_user = self.instance.user
        users = [owner, reviewer_user, self.admin_user, self.adm_admin_user]
        self.get_and_login_user(user=users[faker.pyint(0, 3)])
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # unauthenticated users
        self.instance = FactoryFloor.ReviewerFactory()
        self.test_detail_url = reverse("reviewer-detail", args=[self.instance.pk])
        self.client.logout()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.get_and_login_user(user=self.admin_user)
