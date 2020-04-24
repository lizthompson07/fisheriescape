from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DeleteView

from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from travel.test import FactoryFloor
from .. import models
from .. import views
from travel.test.common_tests import CommonTravelTest as CommonTest


class IndividualTripRequestDelete(CommonTest):
    def setUp(self):
        super().setUp()
        self.tr = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_delete', kwargs={"pk": self.tr.pk})
        self.expected_template = 'travel/trip_request_confirm_delete.html'

    @tag("trip_request", 'delete', "view")
    def test_view_class(self):
        # make sure the view is inheriting from CanModify Mixin
        self.assert_inheritance(views.TripRequestDeleteView, views.CanModifyMixin)

    @tag("trip_request", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # create an admin user (who should always be able to delete) and check to see there is a 200 response
        admin_user = self.get_and_login_user(in_group="travel_admin")
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=admin_user)

    @tag("trip_request", 'delete', "submit")
    def test_submit(self):
        # use an admin user because they should always be able to delete
        admin_user = self.get_and_login_user(in_group="travel_admin")
        self.assert_success_url(self.test_url, user=admin_user)
        # ensure the user is deleted
        self.assertEqual(models.TripRequest.objects.filter(pk=self.tr.pk).count(), 0)


class TestTripDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_delete', kwargs={"pk":self.instance.pk})
        self.expected_template = 'travel/trip_confirm_delete.html'

    @tag("travel", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripDeleteView, DeleteView)

    @tag("travel", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # TODO: do some more elaborate testing here!!
        my_user = self.get_and_login_user(in_group="travel_admin")
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=my_user)

    @tag("travel", 'delete', "submit")
    def test_submit(self):
        my_user = self.get_and_login_user(in_group="travel_admin")
        self.assert_success_url(self.test_url, user=my_user)

        # for delete views...
        self.assertEqual(models.Conference.objects.filter(pk=self.instance.pk).count(), 0)


class TestTripDeleteViewReturnToVerification(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory(lead=RegionFactory())
        self.test_url = reverse_lazy('travel:trip_delete', kwargs={"pk": self.instance.pk, "back_to_verify":1})
        self.expected_template = 'travel/trip_confirm_delete.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("travel", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripDeleteView, DeleteView)
        self.assert_inheritance(views.TripDeleteView, views.TravelAdminRequiredMixin)

    @tag("travel", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("travel", 'delete', "submit")
    def test_submit(self):
        self.assert_success_url(self.test_url, user=self.admin_user)

        # for delete views...
        self.assertEqual(models.Conference.objects.filter(pk=self.instance.pk).count(), 0)