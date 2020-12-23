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

test_password = "test1234"
#
# from importlib import import_module
# from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
#
# def force_login(user, driver, base_url):
#     from django.conf import settings
#     SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
#     driver.get('{}{}'.format(base_url, '/en/'))
#
#     session = SessionStore()
#     session[SESSION_KEY] = user.id
#     session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
#     session[HASH_SESSION_KEY] = user.get_session_auth_hash()
#     session.save()
#
#     cookie = {
#         'name': settings.SESSION_COOKIE_NAME,
#         'value': session.session_key,
#         'path': '/'
#     }
#     driver.add_cookie(cookie)
#     driver.refresh()


class CommonFunctionalTest(CommonTest, StaticLiveServerTestCase):

    def setUp(self):

        super().setUp()  # used to import fixtures
        # need to download the webdriver and stick it in the path/point to it here:
        # can be downloaded from: https://chromedriver.chromium.org/downloads
        self.browser = webdriver.Chrome('bio_diversity/test/functional_test/chromedriver.exe')
        # login user
        user_data = UserFactory.get_valid_data()
        user = User.objects.create_superuser(username=user_data['username'], email=user_data['email1'], password=test_password)
        bio_group = GroupFactory(name='bio_diversity_admin')
        user.groups.add(bio_group)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.set_password(test_password)
        user.save()
        # force_login(user, self.browser, self.live_server_url)
        # self.browser.get('%s%s' % (self.live_server_url, '/en/accounts/login/'))
        # sleep(1)
        # self.browser.find_element_by_id("id_username").send_keys(user.username)
        # sleep(1)
        # self.browser.find_element_by_id("id_password").send_keys(test_password)
        # sleep(1)
        #
        # #
        # self.browser.find_element_by_xpath("//button[@type=\"submit\"]").click()

        # self.browser.get(self.live_server_url + '/en/')  # selenium will set cookie domain based on current page domain
        # username = request.POST['username']
        # password = request.POST['password']
        # user = authenticate(request, username=username, password=password)

        self.browser.get(self.live_server_url + '/en/')
        self.client.force_login(user)  # Native django test client
        cookie = self.client.cookies['sessionid']
        self.browser.get(self.live_server_url + '/admin/')  # selenium will set cookie domain based on current page domain
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()  # need to update page for logged in user
        self.browser.get('%s%s' % (self.live_server_url, '/en/bio_diversity/create/instc/'))
        sleep(200)
        # test_auth = authenticate(user)
        # cookie = self.client.cookies['sessionid']
        #
        #
        # self.browser.get(self.live_server_url + '/en/')  # selenium will set cookie domain based on current page domain
        # self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        # self.browser.refresh()  # need to update page for logged in user
        # self.browser.get(self.live_server_url + '/en/')
        sleep(3)



    def tearDown(self):
        super().tearDown()  # used to import fixtures
        self.browser.close()


@tag("Functional", "Basic")
class TestHomePageTitle(CommonFunctionalTest):

    def test_home_page_title(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)
        self.browser.get('%s%s' % (self.live_server_url, '/en/bio_diversity/create/instc/') )
        sleep(3)
        # She notices the page title tells her she is at DM Apps
        assert 'Instrument Code' in self.browser.title


@tag("Functional", "Instc")
class TestSimpleLookup(CommonFunctionalTest):

    def navigate_through_views(self):
        self.test_url = reverse_lazy('bio_diversity:update_sire', args=[self.instance.pk, ])


