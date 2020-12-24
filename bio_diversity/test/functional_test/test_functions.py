from time import sleep

from django.contrib.auth import authenticate, login
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse_lazy, resolve
from selenium import webdriver

from django.test import tag, override_settings
from bio_diversity import forms
from bio_diversity.test import BioFactoryFloor
# from ..test.common_tests import CommonProjectTest as CommonTest
from django.conf import settings
from shared_models.test.SharedModelsFactoryFloor import UserFactory, GroupFactory
from shared_models.test.common_tests import CommonTest
from django.contrib.auth.models import User


class CommonFunctionalTest(StaticLiveServerTestCase):

    def setUp(self):

        super().setUp()  # used to import fixtures
        # need to download the webdriver and stick it in the path/point to it here:
        # can be downloaded from: https://chromedriver.chromium.org/downloads
        self.browser = webdriver.Chrome('bio_diversity/test/functional_test/chromedriver.exe')
        # generate a user
        user_data = UserFactory.get_valid_data()
        user = User.objects.create_superuser(username=user_data['username'], email=user_data['email1'], password=UserFactory.get_test_password())
        bio_group = GroupFactory(name='bio_diversity_admin')
        user.groups.add(bio_group)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.save()

        self.browser.get(self.live_server_url + '/en/')
        self.client.force_login(user)  # Native django test client
        cookie = self.client.cookies['sessionid'] #grab the login cookie
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()  # selenium will set cookie domain based on current page domain

    def tearDown(self):
        self.browser.quit()  # causes connection was forcibly closed errors due to chrome being out of date
        super().tearDown()

@tag("Functional", "Basic")
class TestHomePageTitle(CommonFunctionalTest):

    def test_home_page_title(self):
        self.browser.get(self.live_server_url)
        assert 'DM Apps' in self.browser.title
        self.browser.implicitly_wait(3)
        self.browser.find_element_by_xpath("//h4[contains(text(), 'Biodiversity')]").click()
        assert 'Biodiversity' in self.browser.title


@tag("Functional", "Instc")
class TestSimpleLookup(CommonFunctionalTest):

    def test_navigate_through_views(self):
        self.browser.get('%s%s' % (self.live_server_url, '/en/bio_diversity/create/instc/'))
        assert 'Instrument Code' in self.browser.title

