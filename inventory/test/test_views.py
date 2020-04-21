from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from inventory.test import FactoryFloor
from inventory.test.common_tests import CommonInventoryTest

#
#
# class TestIndexView(CommonTravelTest):
#
#     def setUp(self):
#         super().setUp()
#
#         self.test_url = reverse_lazy('travel:index')
#         self.expected_template = 'travel/index.html'
#
#     # Users should be able to view the travel index page corresponding to the travel/index.html template, in French
#     @tag("index")
#     def test_access(self):
#         # only logged in users can access the landing
#         super().assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
#
#     # The index view should return a context to be used on the index.html template
#     # this should consist of a "Sections" dictionary containing sub-sections
#
#     @tag("index", "context")
#     def test_context(self):
#         context_vars = [
#             "number_waiting",
#             "rdg_number_waiting",
#             "adm_number_waiting",
#             "unverified_trips",
#             "adm_unverified_trips",
#             "is_reviewer",
#             "is_admin",
#             "my_dict",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars)
#
#         activate('en')
#         reg_user = self.get_and_login_user()
#         response = self.client.get(self.test_url)
#         # a regular user should not be an admin or a reviewer
#         self.assertEqual(response.context["is_admin"], False)
#         self.assertEqual(response.context["is_reviewer"], False)
#
#         # if a regular user is also a reviewer, the 'is_reviewer' var should be true
#         ReviewerFactory(user=reg_user)
#         response = self.client.get(self.test_url)
#         self.assertEqual(response.context["is_reviewer"], True)
#
#         # an admin user should be identified as such by the `is_admin` var in the template
#         self.client.logout()
#         admin_user = self.get_and_login_user(in_group="travel_admin")
#         response = self.client.get(self.test_url)
#         self.assertEqual(response.context["is_admin"], True)
