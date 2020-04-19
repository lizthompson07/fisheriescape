import os
from django.test import TestCase
from django.urls import reverse_lazy, resolve
from django.utils.translation import activate
from shared_models.test.SharedModelsFactoryFloor import UserFactory, GroupFactory
from travel.forms import TripRequestForm

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


###########################################################################################
# Common Test for all views, this includes checking that a view is accessible or provides
# a redirect if permissions are required to access a view
###########################################################################################
class CommonTest(TestCase):
    fixtures = standard_fixtures

    login_url_base = '/accounts/login/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"
    expected_view = None
    expected_form = None

    # use when a user needs to be logged in.
    def get_and_login_user(self, user=None, in_group=None):
        if not user:
            user = UserFactory()
        login_successful = self.client.login(username=user.username, password=UserFactory.get_test_password())
        self.assertEqual(login_successful, True)
        if in_group:
            group = GroupFactory(name=in_group)
            user.groups.add(group)
        return user

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
            reg_user = self.get_and_login_user()
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

    # check that the creation view is using the correct form
    def assert_create_form(self, expected_view, expected_form):
        activate("en")
        self.assertEquals(self.expected_form, self.expected_view.form_class)

    # test that upon a successful form the view redirects to the expected success url
    def assert_success_url(self, data=None, signature=None, user=None):
        activate('en')
        if user:
            self.get_and_login_user(user)
        else:
            self.get_and_login_user()
        response = self.client.post(self.test_url, data)

        if response.context and 'form' in response.context:
            # If the data in this test is invaild the response will be invalid
            self.assertTrue(response.context_data['form'].is_valid(), msg="Test data was likely invalid")

        if signature:
            # in the event a successful url returns an address with an ID, like a creation form redirecting
            # to a details page, set the signature variable and this will resolve the url to get the URL name instead
            # of the URL
            self.assertEquals(302, response.status_code)
            self.assertEquals(signature, resolve(response.url).view_name)
        else:
            self.assertRedirects(response=response, expected_url=self.expected_success_url)

    def assert_form_valid(self, Form, data, instance=None):
        if instance:
            form = Form(data=data, instance=instance)
        else:
            form = Form(data=data)
        self.assertTrue(form.is_valid())

    def assert_form_not_valid(self, Form, data, instance=None):
        if instance:
            form = Form(data, instance=instance)
        else:
            form = Form(data)
        self.assertFalse(form.is_valid())

    def assert_field_in_form(self, Form, field_name, instance=None):
        if instance:
            form = Form(instance=instance)
        else:
            form = Form()
        self.assertIn(field_name,  form.fields)

    def assert_field_not_in_form(self, Form, field_name, instance=None):
            if instance:
                form = Form(instance=instance)
            else:
                form = Form()
            self.assertNotIn(field_name,  form.fields)

#
# ###########################################################################################
# # Create Tests include tests from common tests also adding tests for views extending the Create View
# ###########################################################################################
class CommonCreateTest(CommonTest):
    expected_form = None
    expected_view = None
    expected_success_url = reverse_lazy("shared_models:close_me_no_refresh")
    data = None
    test_url = None

    #   - Requires: self.test_url
    #   - Requires: self.data
    #   - Requires: self.expected_success_url
