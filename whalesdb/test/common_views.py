from django.test import TestCase, tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.contrib.auth.models import User, Group

from django.core.files.base import ContentFile
from django.utils.six import BytesIO
from PIL import Image

import os

from whalesdb import models


def get_mor(with_image=True):
    if models.MorMooringSetup.objects.filter(mor_name="MOR001"):
        mor_1 = models.MorMooringSetup.objects.get(mor_name="MOR001")
    elif with_image:
        img_file_name = "MooringSetupTest.png"
        img_file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + img_file_name

        data = BytesIO()
        Image.open(img_file_path).save(data, "PNG")
        data.seek(0)

        file = ContentFile(data.read(), img_file_name)

        mor_1 = models.MorMooringSetup(mor_name="MOR001", mor_max_depth=100,
                                       mor_link_setup_image="https://somelink.com",
                                       mor_setup_image=file)
        mor_1.save()
    else:
        mor_1 = models.MorMooringSetup(mor_name="MOR001", mor_max_depth=100,
                                       mor_link_setup_image="https://somelink.com")
        mor_1.save()

    return mor_1


def get_prj():
    if models.PrjProject.objects.filter(prj_name="PRJ_001"):
        prj_1 = models.PrjProject.objects.get(prj_name="PRJ_001")
    else:
        prj_1 = models.PrjProject(prj_name="PRJ_001", prj_description="Sample Project",
                                  prj_url="http://someproject.com")
        prj_1.save()

    return prj_1


def get_stn():
    if models.StnStation.objects.filter(stn_code="ST1"):
        stn_1 = models.StnStation.objects.get(stn_code="ST1")
    else:
        stn_1 = models.StnStation(stn_name='Station 1', stn_code='ST1', stn_revision=1, stn_planned_lat=52,
                                  stn_planned_lon=25, stn_planned_depth=1)
        stn_1.save()

    return stn_1


def get_dep():
    if models.DepDeployment.objects.filter(dep_name="DEP_001"):
        dep_1 = models.DepDeployment.objects.get(dep_name="DEP_001")
    else:
        prj = get_prj()
        mor = get_mor()
        stn = get_stn()

        dep_1 = models.DepDeployment(dep_year=2020, dep_month=2, dep_name='DEP_001', stn=stn, prj=prj, mor=mor)
        dep_1.save()

    return dep_1


class CommonFormTest(TestCase):
    valid_data = None

    @staticmethod
    def get_valid_data():
        pass

    def setUp(self) -> None:
        if not self.valid_data:
            self.get_valid_data()


###########################################################################################
# Common Test for all views, this includes checking that a view is accessible or provides
# a redirect if permissions are required to access a view
###########################################################################################
class CommonTest(TestCase):
    test_url = None
    test_expected_template = None
    login_url_base = '/accounts/login_required/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"

    # All views should at a minimum have a title field
    def assert_context_fields(self, response):
        self.assertIn("title", response.context)

    # This is a standard view test most classes should run at some point to ensure
    # that a view is reachable and to check permissions/redirect if required
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
# List Test contain tests used from common Test also adding tests specific for list/filter views
###########################################################################################
class CommonListTest(CommonTest):

    def setUp(self):
        super().setUp()

        self.test_expected_template = 'whalesdb/whale_filter.html'

    # List context should return:
    #   - a title to display in the html template
    #   - a list of fields to display
    #   - a url to use for the create button
    #   - a url to use for the detail links
    def assert_list_view_context_fields(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)
        self.assertIn("fields", response.context)
        self.assertIn("create_url", response.context)
        self.assertIn("details_url", response.context)

        # determine if a user is logged in and has access to see "add" button
        self.assertIn("auth", response.context)

        return response


###########################################################################################
# Create Tests include tests from common tests also adding tests for views extending the Create View
###########################################################################################
class CommonCreateTest(CommonTest):

    expected_form = None
    expected_view = None
    expected_success_url = reverse_lazy("whalesdb:close_me")
    data = None
    test_password = "test1234"

    def setUp(self):
        super().setUp()

        # CreateViews intended to be used from a views.ListCommon should use the _entry_form.html template
        self.test_expected_template = 'whalesdb/_entry_form.html'

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
    def login_whale_user(self):
        user_name = "Whale"
        if User.objects.filter(username=user_name):
            user = User.objects.get(username=user_name)
        else:
            whale_group = Group(name="whalesdb_admin")
            whale_group.save()

            user = User.objects.create_user(username=user_name, first_name="Hump", last_name="Back",
                                                         email="Hump.Back@dfo-mpo.gc.ca", password=self.test_password)
            user.groups.add(whale_group)
            user.save()

        self.client.login(username=user.username, password=self.test_password)

        return user

    # If a user is logged in and not in 'whalesdb_admin' they should be get a 403 restriction
    def assert_logged_in_not_access(self):
        regular_user = self.login_regular_user()

        self.assertEqual(int(self.client.session['_auth_user_id']), regular_user.pk)

        super().assert_view(expected_code=403)

    # If a user is logged in and in 'whalesdb_admin' they should not be redirected
    def assert_logged_in_has_access(self):
        whale_user = self.login_whale_user()

        self.assertEqual(int(self.client.session['_auth_user_id']), whale_user.pk)

        super().assert_view()

    # check that the creation view is using the correct form
    def assert_create_form(self):
        activate("en")

        view = self.expected_view

        self.assertEquals(self.expected_form, view.form_class)

    # All CommonCreate views should at a minimum have a title.
    # This will return the response for other create view tests to run further tests on context if required
    def assert_create_view_context_fields(self):
        activate('en')

        self.login_whale_user()
        response = self.client.get(self.test_url)

        super().assert_context_fields(response)

        return response

    # test that upon a successful form the view redirects to the expected success url
    #   - Requires: self.test_url
    #   - Requires: self.data
    #   - Requires: self.expected_success_url
    def assert_successful_url(self, data=None):
        activate('en')

        self.login_whale_user()
        response = self.client.post(self.test_url, data if data else self.data)

        self.assertRedirects(response=response, expected_url=self.expected_success_url)


###########################################################################################
# Common update test has access to tests from Common Creation tests also adding test specific to
# views extending UpdateView
###########################################################################################
class CommonUpdateTest(CommonCreateTest):
    pass


###########################################################################################
# Common Detail test includes tests from Common Test also adding tests specific for views extending DetailsView
###########################################################################################
class CommonDetailsTest(CommonTest):

    fields = []
    _details_dict = None

    def createDict(self):
        pass

    # used to destroy test objects created during a test
    def tearDown(self) -> None:
        _details_dict = self.createDict()

        for key in self._details_dict:
            _details_dict[key].delete()

    def assert_field_in_fields(self, response):
        for field in self.fields:
            self.assertIn(field, response.context['fields'])

    def assert_context_fields(self, response):
        super().assert_context_fields(response)

        self.assertIn("list_url", response.context)
        self.assertIn("update_url", response.context)
