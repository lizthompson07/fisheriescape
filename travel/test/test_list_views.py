from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView

from travel.test import FactoryFloor
from .. import models
from .. import views
from travel.test.common_tests import CommonTravelTest as CommonTest


class TripRequestListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.tr = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_list')
        self.expected_template = 'travel/trip_request_list.html'

    @tag("trip_request", 'list', "view")
    def test_view_class(self):
        # make sure the view is inheriting from CanModify Mixin
        self.assert_inheritance(views.TripRequestListView, FilterView)

    @tag("trip_request", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # create an admin user (who should always be able to delete) and check to see there is a 200 response
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    # Test that the context contains the proper vars
    @tag("trip_request", 'list', "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)

class TestTripListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('travel:trip_list')
        self.expected_template = 'travel/trip_list.html'

    @tag("travel", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripListView, FilterView)

    @tag("travel", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("travel", 'list', "context")
    def test_context(self):
        context_vars = [
            "my_object",
            "field_list",
            "is_admin",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
    

class TestAdminTripVerificationListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:admin_trip_verification_list', kwargs={"region":0, "adm":0})
        self.expected_template = 'travel/trip_verification_list.html'

    @tag("travel", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.AdminTripVerificationListView, ListView)

    @tag("travel", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("travel", 'list', "context")
    def test_context(self):
        context_vars = [
            "field_list",
            "my_object",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
    
