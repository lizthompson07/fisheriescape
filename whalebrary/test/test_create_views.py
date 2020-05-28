from django.urls import reverse_lazy
from django.test import tag
from inventory.test import FactoryFloor
from inventory.test.common_tests import CommonInventoryTest


#
# class IndividualTripRequestCreate(CommonTravelTest):
#
#     def setUp(self):
#         super().setUp()  # used to import fixutres
#         self.trip_request = FactoryFloor.IndividualTripRequestFactory()
#         self.test_url = reverse_lazy('travel:request_new')
#         self.expected_template = 'travel/trip_request_form.html'
#
#     @tag("trip_request", 'create', 'response')
#     def test_access(self):
#         # only logged in users can access the landing
#         self.assert_not_broken(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
#
#     # Test that the context contains the proper vars
#     @tag("trip_request", 'create', "context")
#     def test_context(self):
#         context_vars = [
#             "user_json",
#             "conf_json",
#             "help_text_dict",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars)
#
#     @tag("trip_request", 'create', "submit")
#     def test_submit(self):
#         data = IndividualTripRequestFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data)
#         # TODO: now we will want to make sense that the reviewers make sense... adm vs. non adm.. regional ppl etc
