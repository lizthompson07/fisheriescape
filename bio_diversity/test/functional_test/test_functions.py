from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse_lazy, resolve
from selenium import webdriver

from django.test import tag
from selenium.webdriver import ActionChains

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
        self.browser.maximize_window()
        self.browser.implicitly_wait(3)
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

        self.actions = ActionChains(self.browser)

    def tearDown(self):
        # self.browser.quit()  # causes connection was forcibly closed errors due to chrome being out of date
        super().tearDown()


def scroll_n_click(driver, element):
    # scroll to bring element to bottom of screen, then scroll up once to move element off of banners
    driver.execute_script("arguments[0].scrollIntoView(false);", element)
    driver.execute_script("window.scrollBy(0,50)");
    element.click()


@tag("Functional", "Basic")
class TestHomePageTitle(CommonFunctionalTest):

    def test_home_page_title(self):
        self.browser.get(self.live_server_url)
        assert 'DM Apps' in self.browser.title
        self.browser.implicitly_wait(3)
        biod_btn = self.browser.find_element_by_xpath("//h4[contains(text(), 'Biodiversity')]")
        scroll_n_click(self.browser, biod_btn)
        assert 'Biodiversity' in self.browser.title


@tag("Functional", "Instc")
class TestSimpleLookup(CommonFunctionalTest):

    def test_navigate_through_views(self):
        # user starts on app homepage:
        self.browser.get("{}{}".format(self.live_server_url, "/en/bio_diversity/"))

        # user clicks on a common lookup, ends up a list view
        instc_btn = self.browser.find_element_by_xpath("//a[@class='btn btn-secondary btn-lg' and contains(text(), 'Instrument Code')]")
        scroll_n_click(self.browser, instc_btn)

        self.browser.implicitly_wait(3)
        assert 'Instrument Code' in self.browser.title

        # user creates a new instance of the lookup
        self.browser.find_element_by_xpath("//a[@class='btn btn-primary' and contains(text(), '+')]").click()
        instc = BioFactoryFloor.InstcFactory.build_valid_data()
        name_field = self.browser.find_element_by_xpath("//input[@name='name']")
        description_field = self.browser.find_element_by_xpath("//textarea[@name='description_en']")
        name_field.send_keys(instc["name"])
        description_field.send_keys(instc["description_en"])

        submit_btn = self.browser.find_element_by_xpath("//button[@class='btn btn-success']")
        scroll_n_click(self.browser, submit_btn)

        sleep(3)


        # user checks to make sure that the instance is created and looks at its details

        # user updates the instances details and goes on their way


        self.browser.get('%s%s' % (self.live_server_url, '/en/bio_diversity/create/instc/'))
        assert 'Instrument Code' in self.browser.title

