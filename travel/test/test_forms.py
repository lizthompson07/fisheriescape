from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag

from travel.test import TravelFactoryFloor as FactoryFloor
from travel.test.TravelFactoryFloor import IndividualTripRequestFactory, TripFactory

from travel.test.common_tests import CommonTravelTest
from .. import forms


class TestTripRequestForm(CommonTravelTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.TripRequestForm

    @tag("trip_request", 'form')
    def test_valid_data(self):
        data = IndividualTripRequestFactory.get_valid_data()
        trip = TripFactory()
        data["trip"] = trip
        self.assert_form_valid(forms.TripRequestForm, data)

    @tag("trip_request", 'form')
    def test_fields(self):
        # if looking at the trip request form with no instance, the reset reviewer field should not be there
        self.assert_field_not_in_form(self.Form, "reset_reviewers")
        tr = IndividualTripRequestFactory()
        self.assert_field_in_form(self.Form, "reset_reviewers", tr)
