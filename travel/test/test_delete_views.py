from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag

from travel.test import TravelFactoryFloor as FactoryFloor
from travel.test.TravelFactoryFloor import IndividualTripRequestFactory, TripFactory
from .. import models
from .. import views
from travel.test.common_tests import CommonTravelTest


class IndividualTripRequestDelete(CommonTravelTest):
    def setUp(self):
        super().setUp()
        self.tr = IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_delete', kwargs={"pk": self.tr.pk})
        self.expected_template = 'travel/trip_request_confirm_delete.html'

    @tag("trip_request", 'delete', "view")
    def test_view_class(self):
        # make sure the view is inheriting from CanModify Mixin
        self.assert_inheritance(views.TripRequestDeleteView, views.CanModifyMixin)

    @tag("trip_request", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_login_required_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("trip_request", 'delete', "submit")
    def test_submit(self):
        self.get_and_login_user(user=self.tr.user)
        self.assert_success_url(self.test_url)
        # ensure the user is deleted
        self.assertEqual(models.TripRequest.objects.filter(pk=self.tr.pk).count(), 0)
