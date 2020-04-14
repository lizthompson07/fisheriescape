import os
from django.test import TestCase
from django.utils.translation import activate
from shared_models.test.SharedModelsFactoryFloor import UserFactory, GroupFactory

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


# This is used to simulate calling the as_veiw() function normally called in the urls.py
# this will return a view that can then have it's internal methods tested


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class CommonFormTest(TestCase):
    form_class = None
    test_factory = None

    fixtures = standard_fixtures

    def setUp(self) -> None:
        activate('en')

    def assert_valid_data(self):
        form = self.form_class(data=self.test_factory.get_valid_data())
        self.assertTrue(form.is_valid(), msg=form.errors)


###########################################################################################
# Common Test for all views, this includes checking that a view is accessible or provides
# a redirect if permissions are required to access a view
###########################################################################################
class CommonTest(TestCase):
    fixtures = standard_fixtures

    login_url_base = '/accounts/login/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"

    # use when a user needs to be logged in.
    def get_and_login_regular_user(self, user=None):
        if not user:
            user = UserFactory()
        login_successful = self.client.login(username=user.username, password=UserFactory.get_test_password())
        self.assertEqual(login_successful, True)
        return user

    # use when a user needs to be logged in.
    def get_and_login_travel_admin_user(self, user=None):
        if not user:
            user = UserFactory()
        travel_admin_group = GroupFactory(name="travel_admin")
        user.groups.add(travel_admin_group)
        login_successful = self.client.login(username=user.username, password=UserFactory.get_test_password())
        self.assertEqual(login_successful, True)
        return user

    # use when a user needs to be logged in.
    def get_and_login_travel_adm_admin_user(self, user=None):
        if not user:
            user = UserFactory()
        travel_admin_adm_group = GroupFactory(name="travel_admin_adm")
        user.groups.add(travel_admin_adm_group)
        login_successful = self.client.login(username=user.username, password=UserFactory.get_test_password())
        self.assertEqual(login_successful, True)
        return user

    # at this point there is nothing to check across all context vars
    def assert_context_fields(self, response):
        # self.assertIn("title", response.context)
        pass

    # This is a standard view test most classes should run at some point to ensure
    # that a view is reachable and to check permissions/redirect if required
    # run through both languages to ensure they work
    def assert_login_required_view(self, test_url, langs=('en', 'fr'), expected_template=None):
        # perform this test for each locale
        for lang in langs:
            activate(lang)
            response = self.client.get(test_url)
            # with Anonymous User, a 302 response is expected
            self.assertEquals(302, response.status_code)
            # self.assertEqual(f"{self.login_url_base}{self.test_url}", response.url)

            # login a random user
            reg_user = self.get_and_login_regular_user()
            # must get a new response
            response = self.client.get(test_url)
            # now a 200 response is expected
            self.assertEquals(200, response.status_code)

            # if an expected template was provided, test it against the template_name in the response
            if expected_template:
                self.assertIn(expected_template, response.template_name)
            self.client.logout()

    def assert_public_view(self, test_url, langs=('en', 'fr'), expected_template=None):
        # perform this test for each locale
        for lang in langs:
            activate(lang)
            response = self.client.get(test_url)
            # now a 200 response is expected
            self.assertEquals(200, response.status_code)
            # if an expected template was provided, test it against the template_name in the response
            if expected_template:
                self.assertIn(expected_template, response.template_name)
            self.client.logout()

    def assert_field_in_fields(self, response, name_of_field_list, fields_to_test):
        for field in fields_to_test:
            self.assertIn(field, response.context[name_of_field_list])



#
# ###########################################################################################
# # Create Tests include tests from common tests also adding tests for views extending the Create View
# ###########################################################################################
# class CommonCreateTest(CommonTest):
#     expected_form = None
#     expected_view = None
#     expected_success_url = reverse_lazy("shared_models:close_me_no_refresh")
#     data = None
#
#     def setUp(self):
#         super().setUp()
#
#         # CreateViews intended to be used from a views.ListCommon should use the shared_entry_form.html template
#         self.test_expected_template = 'whalesdb/shared_entry_form.html'
#
#     # If a user is logged in and not in 'whalesdb_admin' they should be get a 403 restriction
#     def assert_logged_in_not_access(self):
#         regular_user = self.login_regular_user()
#
#         self.assertEqual(int(self.client.session['_auth_user_id']), regular_user.pk)
#
#         super().assert_view(expected_code=403)
#
#     # If a user is logged in and in 'whalesdb_admin' they should not be redirected
#     def assert_logged_in_has_access(self):
#         whale_user = self.login_whale_user()
#
#         self.assertEqual(int(self.client.session['_auth_user_id']), whale_user.pk)
#
#         super().assert_view()
#
#     # check that the creation view is using the correct form
#     def assert_create_form(self):
#         activate("en")
#
#         view = self.expected_view
#
#         self.assertEquals(self.expected_form, view.form_class)
#
#     # All CommonCreate views should at a minimum have a title.
#     # This will return the response for other create view tests to run further tests on context if required
#     def assert_create_view_context_fields(self):
#         activate('en')
#
#         self.login_whale_user()
#         response = self.client.get(self.test_url)
#
#         super().assert_context_fields(response)
#
#         return response
#
#     # test that upon a successful form the view redirects to the expected success url
#     #   - Requires: self.test_url
#     #   - Requires: self.data
#     #   - Requires: self.expected_success_url
#     def assert_successful_url(self, data=None, signature=None):
#         activate('en')
#
#         self.login_whale_user()
#         response = self.client.post(self.test_url, data if data else self.data)
#
#         if response.context and 'form' in response.context:
#             # If the data in this test is invaild the response will be invalid
#             self.assertTrue(response.context_data['form'].is_valid(), msg="Test data was likely invalid")
#
#         if signature:
#             # in the event a successful url returns an address with an ID, like a creation form redirecting
#             # to a details page, set the signature variable and this will resolve the url to get the URL name instead
#             # of the URL
#             self.assertEquals(302, response.status_code)
#             self.assertEquals(signature, resolve(response.url).view_name)
#         else:
#             self.assertRedirects(response=response, expected_url=self.expected_success_url)
#
#
# ###########################################################################################
# # Common update test has access to tests from Common Creation tests also adding test specific to
# # views extending UpdateView
# ###########################################################################################
# class CommonUpdateTest(CommonCreateTest):
#     pass
#
#
# ###########################################################################################
# # Common Detail test includes tests from Common Test also adding tests specific for views extending DetailsView
# ###########################################################################################
# class CommonDetailsTest(CommonTest):
#     fields = []
#     _details_dict = None
#
#     def createDict(self):
#         pass
#
#     # used to destroy test objects created during a test
#     def tearDown(self) -> None:
#         _details_dict = self.createDict()
#
#         for key in self._details_dict:
#             _details_dict[key].delete()
#
#     def assert_field_in_fields(self, response):
#         for field in self.fields:
#             self.assertIn(field, response.context['fields'])
#
#     def assert_context_fields(self, response):
#         super().assert_context_fields(response)
#
#         self.assertIn("list_url", response.context)
#         self.assertIn("update_url", response.context)
