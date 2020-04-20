from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag

from travel.test import TravelFactoryFloor as FactoryFloor
from travel.test.TravelFactoryFloor import IndividualTripRequestFactory, TripFactory

from travel.test.common_tests import CommonTravelTest


class IndividualTripRequestCreate(CommonTravelTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.trip_request = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_new')
        self.expected_template = 'travel/trip_request_form.html'

    @tag("trip_request", 'create', 'response')
    def test_access(self):
        # only logged in users can access the landing
        self.assert_not_broken(self.test_url)
        self.assert_login_required_view(test_url=self.test_url, expected_template=self.expected_template)

    # Test that the context contains the proper vars
    @tag("trip_request", 'create', "context")
    def test_context(self):
        activate('en')
        reg_user = self.get_and_login_user()
        response = self.client.get(self.test_url)
        # expected to determine if the user is authorized to add content
        self.assertIn("user_json", response.context)
        self.assertIn("conf_json", response.context)
        self.assertIn("help_text_dict", response.context)

    @tag("trip_request", 'create', "submit")
    def test_submit(self):
        data = IndividualTripRequestFactory.get_valid_data()
        trip = TripFactory()
        data["trip"] = trip
        self.assert_success_url(data)

        # once submitted, we will want to check out that the reviewers make sense

        # ensure the user is deleted
        # self.assertEqual(User.objects.filter(pk=self.user.pk).count(), 0)
