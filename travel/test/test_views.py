from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from travel.test.TravelFactoryFloor import ReviewerFactory
from travel.test.common_views import CommonTest


###########################################################################################
# Index View is a bit different from most views as it is basically just a landing page
###########################################################################################
class TestIndexView(CommonTest):

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('travel:index')
        self.test_expected_template = 'travel/index.html'

    # Users should be able to view the travel index page corresponding to the travel/index.html template, in French
    @tag("index", "slow")
    def test_index_view(self):
        # only logged in users can access the landing
        super().assert_view(lang='en', expected_code=302)
        super().assert_view(lang='fr', expected_code=302)
        reg_user = self.get_and_login_regular_user()
        super().assert_view(lang='en', expected_code=200)
        super().assert_view(lang='fr', expected_code=200)
        self.client.logout()

    # The index view should return a context to be used on the index.html template
    # this should consist of a "Sections" dictionary containing sub-sections

    @tag("index", "context")
    def test_index_view_context(self):
        activate('en')
        reg_user = self.get_and_login_regular_user()
        response = self.client.get(self.test_url)
        # expected to determine if the user is authorized to add content
        self.assertIn("number_waiting", response.context)
        self.assertIn("rdg_number_waiting", response.context)
        self.assertIn("adm_number_waiting", response.context)
        self.assertIn("unverified_trips", response.context)
        self.assertIn("adm_unverified_trips", response.context)
        self.assertIn("is_reviewer", response.context)
        self.assertIn("is_admin", response.context)
        self.assertIn("my_dict", response.context)

        # a regular user should not be an admin or a reviewer
        self.assertEqual(response.context["is_admin"], False)
        self.assertEqual(response.context["is_reviewer"], False)

        # if a regular user is also a reviewer, the 'is_reviewer' var should be true
        ReviewerFactory(user=reg_user)
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["is_reviewer"], True)

        # an admin user should be identified as such by the `is_admin` var in the template
        self.client.logout()
        admin_user = self.get_and_login_travel_admin_user()
        response = self.client.get(self.test_url)
        self.assertEqual(response.context["is_admin"], True)
