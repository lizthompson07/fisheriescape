from django.urls import reverse_lazy, resolve
from django.utils.translation import activate
from django.contrib.auth.models import User, Group


###########################################################################################
# Common Test for all views, this includes checking that a view is accessible or provides
# a redirect if permissions are required to access a view
###########################################################################################
class CommonTest(object):
    fixtures = []

    test_url = None
    test_expected_template = None
    login_url_base = '/accounts/login_required/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"

    test_password = "test1234"

    # use when a user needs to be logged in.
    def login_regular_user(self):
        user_name = "Regular"
        if User.objects.filter(username=user_name):
            user = User.objects.get(username=user_name)
        else:
            user = User.objects.create_user(username=user_name, first_name="Joe", last_name="Average",
                                            email="Average.Joe@dfo-mpo.gc.ca", password=self.test_password)
            user.save()

        self.client.login(username=user.username, password=self.test_password)

        return user

    # use when a user needs to be logged in.
    def login_bio_user(self):
        user_name = "bio_diversity"
        if User.objects.filter(username=user_name):
            user = User.objects.get(username=user_name)
        else:
            bio_diversity_group = Group(name="bio_diversity_admin")
            bio_diversity_group.save()

            user = User.objects.create_user(username=user_name, first_name="Bio", last_name="Diversity",
                                            email="Bio.Diversity@dfo-mpo.gc.ca", password=self.test_password)
            user.groups.add(bio_diversity_group)
            user.save()

        self.client.login(username=user.username, password=self.test_password)

        return user

    # Get context will use the default Test url set up in the setUp function, unless otherwise supplied as an
    # argument here. By default this method will also log a user in as the standard whale user, unless
    # whale_user=False, in which case a user will be logged in as a regular user not in the whale_admin group
    def get_context(self, url=None, whale_user=True):
        activate('en')

        if whale_user:
            self.login_bio_user()
        else:
            self.login_regular_user()

        response = self.client.get(self.test_url if url is None else url)

        return response

    # All views should at a minimum have a title field and determine if a user is authorized,
    # and if content is editable
    def assert_context_fields(self, response):
        self.assertIn("title", response.context)
        self.assertIn("auth", response.context)
        self.assertIn("editable", response.context)

    # This is a standard view test most classes should run at some point to ensure
    # that a view is reachable and to check permissions/redirect if required
    #
    # Users must be logged in to create or update objects, if this class fails because the returned value was 200
    # instead of 302 it might be because the extending CreateView did not extend shared_models.CommonAuthCreateView.
    # If the shared_models.CommonCreateView was extended then no login will be required and the view will
    # return 200 OK, rather than 303 REDIRECT
    def assert_view(self, lang='en', test_url=None, expected_template=None, expected_code=200):
        activate(lang)

        response = self.client.get(self.test_url if not test_url else test_url)

        self.assertEquals(expected_code, response.status_code)
        # if it's a 302 redirect and a redirect url is provided
        template = self.test_expected_template if not expected_template else expected_template
        if expected_code == 403:
            self.assertEqual(expected_code, response.status_code)
        elif expected_code == 302:
            self.assertEqual(expected_code, response.status_code)
            self.assertEqual("{}{}".format(self.login_url_base, self.test_url), response.url)
        else:
            self.assertIn(template, response.template_name)


###########################################################################################
# Create Tests include tests from common tests also adding tests for views extending the
# Create View. For the most part we expect users will have to be logged in and in some security
# group in order to create data. So when using these tests the CreateView being tested should
# extend the shared_models.CommonAuthCreateView() class.
###########################################################################################
class CommonCreateTest(CommonTest):

    # It is expected that an extending test class will override some or all of the variable created in this
    # setUp method.
    def setUp(self):
        super().setUp()

        # CreateViews intended to be used from a views.ListCommon should use the shared_entry_form.html template
        # if they use some other Template, make sure to set it in the extending tests class' setUp method
        self.test_expected_template = 'whalesdb/shared_entry_form.html'

        expected_form = None
        expected_view = None
        expected_success_url = reverse_lazy("shared_models:close_me_no_refresh")
        data = None

    # Users must be logged in to create new objects, if this class fails because the returned value was 200 instead
    # of 302 it might be because the extending XXXCreateView did not extend shared_models.CommonAuthCreateView
    # if the shared_models.CommonCreateView was extended then no login will be required and the view will
    # return 200 OK, rather than 303 REDIRECT
    def test_view_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    def test_view_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # If a user is logged in and not in 'whalesdb_admin' they should be get a 403 restriction
    def test_logged_in_not_access(self):
        regular_user = self.login_regular_user()

        self.assertEqual(int(self.client.session['_auth_user_id']), regular_user.pk)

        super().assert_view(expected_code=403)

    # If a user is logged in and in 'whalesdb_admin' they should not be redirected
    def test_logged_in_has_access(self):
        whale_user = self.login_bio_user()

        self.assertEqual(int(self.client.session['_auth_user_id']), whale_user.pk)

        super().assert_view()

    # check that the creation view is using the correct form
    def test_form(self):
        activate("en")

        view = self.expected_view

        self.assertEquals(self.expected_form, view.form_class)

    # All CommonCreate views should at a minimum have a title.
    # This will return the response for other create view tests to run further tests on context if required
    def test_view_context_fields(self):
        activate('en')

        super().assert_context_fields(self.get_context())

    def test_successful_url(self):
        self.assert_successful_url()

    # test that upon a successful form the view redirects to the expected success url
    #   - Requires: self.test_url
    #   - Requires: self.data
    #   - Requires: self.expected_success_url
    def assert_successful_url(self, data=None, signature=None):
        activate('en')

        self.login_bio_user()
        response = self.client.post(self.test_url, data if data else self.data)

        if response.context and 'form' in response.context:
            # If the data in this test is invaild the response will be invalid
            # The Test data might be invalid because of the Factory is producing invalid data,
            # This happens a lot
            self.assertTrue(response.context_data['form'].is_valid(), msg="Test data was likely invalid")

        if signature:
            # in the event a successful url returns an address with an ID, like a creation form redirecting
            # to a details page, set the signature variable and this will resolve the url to get the URL name instead
            # of the URL
            self.assertEquals(302, response.status_code)
            self.assertEquals(signature, resolve(response.url).view_name)
        else:
            self.assertRedirects(response=response, expected_url=self.expected_success_url)
