from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag

from travel.test import TravelFactoryFloor as FactoryFloor
from travel.test.common_views import CommonTest


class TripRequestDetails(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.trip_request = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_detail', args=(self.trip_request.pk,))
        self.expected_template = 'travel/trip_request_detail.html'

    @tag("trip_request", 'detail')
    def test_trip_request_details(self):
        # only logged in users can access the landing
        super().assert_login_required_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("trip_request", 'detail', "field_list")
    def test_trip_request_fields(self):
        reg_user = self.get_and_login_regular_user()
        response = self.client.get(self.test_url)
        name_of_field_list = 'field_list'
        fields_to_test = [
            "fiscal_year"
        ]
        super().assert_field_in_fields(response, name_of_field_list, fields_to_test)

    # Test that the context contains the proper vars
    @tag("trip_request", 'detail', "context")
    def test_context_fields_emm(self):
        activate('en')
        reg_user = self.get_and_login_regular_user()
        response = self.client.get(self.test_url)
        # expected to determine if the user is authorized to add content
        self.assertIn("field_list", response.context)
        self.assertIn("child_field_list", response.context)
        self.assertIn("reviewer_field_list", response.context)
        self.assertIn("conf_field_list", response.context)
        self.assertIn("cost_field_list", response.context)
        self.assertIn("help_text_dict", response.context)
        self.assertIn("help_text_dict", response.context)
        self.assertIn("fy", response.context)
        self.assertIn("is_admin", response.context)
        self.assertIn("is_owner", response.context)
        self.assertIn("is_current_reviewer", response.context)
        self.assertIn("can_modify", response.context)

        # a random user should not be an admin, owner, current_reviewer, able-to-modify
        self.assertEqual(response.context["is_admin"], False)
        self.assertEqual(response.context["is_owner"], False)
        # self.assertEqual(response.context["report_mode"], True)
        # self.assertIsNone(response.context["can_modify"], False)
        self.assertIsNone(response.context["is_current_reviewer"], True)

        # if owner, the is_owner var should be true
        self.trip_request.user = reg_user
        self.trip_request.save()
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["is_admin"], False)
        self.assertEqual(response.context["is_owner"], True)
        self.assertIsNone(response.context["is_current_reviewer"], True)

        # if a user is an admin, they should be able to modify and are also always the current_reviewer
        self.get_and_login_travel_admin_user()
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["is_admin"], True)
        self.assertEqual(response.context["is_owner"], False)
        self.assertEqual(response.context["is_current_reviewer"], True)

        # if a regular user is the current reviewer
        my_reviewer = FactoryFloor.ReviewerFactory(trip_request=self.trip_request, status_id=1)
        self.get_and_login_regular_user(user=my_reviewer.user)
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["is_admin"], False)
        self.assertEqual(response.context["is_owner"], False)
        self.assertEqual(response.context["is_current_reviewer"], True)

        # a submitted project being viewed by someone who is not admin or not current reviewer should have report_mode set to True
        self.trip_request.submitted = timezone.now()
        self.trip_request.save()
        reg_user = self.get_and_login_regular_user()
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["report_mode"], True)

