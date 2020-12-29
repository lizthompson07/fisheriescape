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
        # generate a user
        user_data = UserFactory.get_valid_data()
        user = User.objects.create_superuser(username=user_data['username'], email=user_data['email1'],
                                             password=UserFactory.get_test_password())
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
    # scroll to bring element to bottom of screen, then scroll up once to move element off of banners and click on it
    driver.execute_script("arguments[0].scrollIntoView(false);", element)
    driver.execute_script("window.scrollBy(0,50)");
    element.click()


@tag("Functional", "Basic")
class TestHomePageTitle(CommonFunctionalTest):

    def test_home_page_title(self):
        self.browser.get(self.live_server_url)
        self.assertIn('DM Apps', self.browser.title, "not on correct page")
        biod_btn = self.browser.find_element_by_xpath("//h4[contains(text(), 'Biodiversity')]")
        scroll_n_click(self.browser, biod_btn)
        self.assertIn('Biodiversity', self.browser.title, "not on correct page")


@tag("Functional", "Instc")
class InstcTestSimpleLookup(CommonFunctionalTest):

    lookup_verbose = 'Instrument Code'
    lookup_data = BioFactoryFloor.InstcFactory.build_valid_data()

    def test_full_interaction(self):
        # user starts on app homepage:
        self.browser.get("{}{}".format(self.live_server_url, "/en/bio_diversity/"))

        # user clicks on a common lookup, ends up a list view
        lookup_btn = self.browser.find_element_by_xpath("//a[@class='btn btn-secondary btn-lg' and contains(text(), "
                                                        "'{}')]".format(self.lookup_verbose))
        scroll_n_click(self.browser, lookup_btn)
        self.assertIn(self.lookup_verbose, self.browser.title, "not on correct page")

        # user creates a new instance of the lookup
        self.browser.find_element_by_xpath("//a[@class='btn btn-primary' and contains(text(), '+')]").click()
        name_field = self.browser.find_element_by_xpath("//input[@name='name']")
        description_field = self.browser.find_element_by_xpath("//textarea[@name='description_en']")
        name_field.send_keys(self.lookup_data["name"])
        description_field.send_keys(self.lookup_data["description_en"])
        submit_btn = self.browser.find_element_by_xpath("//button[@class='btn btn-success']")
        scroll_n_click(self.browser, submit_btn)

        # user checks to make sure that the instance is created
        details_table = self.browser.find_element_by_xpath("//table[@id='details_table']/tbody")
        rows = details_table.find_elements_by_tag_name("tr")
        new_object_row = False
        for row in rows:
            name_cell = row.find_elements_by_tag_name("td")[0]
            if name_cell.text == self.lookup_data["name"]:
                new_object_row = row
        self.assertTrue(new_object_row, "New object not displayed")

        # user looks at details of newly created object:
        new_object_row.find_element_by_xpath("//a[@class='btn btn-primary btn-sm my-1' and contains(text(), "
                                             "'Details')]").click()
        description_detail_element = self.browser.find_element_by_xpath("//span[@class='font-weight-bold'and "
                                                                        "contains(text(), 'Description (en) : ')]"
                                                                        "/following-sibling::span")
        self.assertEqual(description_detail_element.text, self.lookup_data["description_en"].replace("\n", " "),
                         "Description does not match input")

        # user updates the instances details and goes on their way
        self.browser.find_element_by_xpath("//a[@class='btn btn-primary' and@title='Update']").click()
        name_field = self.browser.find_element_by_xpath("//input[@name='name']")
        name_field.clear()
        name_field.send_keys("updated name")
        submit_btn = self.browser.find_element_by_xpath("//button[@class='btn btn-success']")
        scroll_n_click(self.browser, submit_btn)

        details_table = self.browser.find_element_by_xpath("//table[@id='details_table']/tbody")
        rows = details_table.find_elements_by_tag_name("tr")  # get all of the rows in the table
        new_object_row = False
        old_object_row = False
        for row in rows:
            # Get the columns (all the column 2)
            name_cell = row.find_elements_by_tag_name("td")[0]  # note: index start from 0, 1 is col 2
            if name_cell.text == self.lookup_data["name"]:
                old_object_row = row
            if name_cell.text == "updated name":
                new_object_row = row
        self.assertTrue(new_object_row, "updated object not in details list")
        self.assertFalse(old_object_row, "old object still in details list")


@tag("Functional", "Instdc")
class InstdcTestSimpleLookup(CommonFunctionalTest):

    lookup_verbose = 'Instrument Detail Code'
    lookup_data = BioFactoryFloor.InstdcFactory.build_valid_data()

    def test_full_interaction(self):
        # user starts on app homepage:
        self.browser.get("{}{}".format(self.live_server_url, "/en/bio_diversity/"))

        # user clicks on a common lookup, ends up a list view
        lookup_btn = self.browser.find_element_by_xpath("//a[@class='btn btn-secondary btn-lg' and contains(text(), "
                                                        "'{}')]".format(self.lookup_verbose))
        scroll_n_click(self.browser, lookup_btn)
        self.assertIn(self.lookup_verbose, self.browser.title, "not on correct page")

        # user creates a new instance of the lookup
        self.browser.find_element_by_xpath("//a[@class='btn btn-primary' and contains(text(), '+')]").click()
        name_field = self.browser.find_element_by_xpath("//input[@name='name']")
        description_field = self.browser.find_element_by_xpath("//textarea[@name='description_en']")
        name_field.send_keys(self.lookup_data["name"])
        description_field.send_keys(self.lookup_data["description_en"])
        submit_btn = self.browser.find_element_by_xpath("//button[@class='btn btn-success']")
        scroll_n_click(self.browser, submit_btn)

        # user checks to make sure that the instance is created
        details_table = self.browser.find_element_by_xpath("//table[@id='details_table']/tbody")
        rows = details_table.find_elements_by_tag_name("tr")
        new_object_row = False
        for row in rows:
            name_cell = row.find_elements_by_tag_name("td")[0]
            if name_cell.text == self.lookup_data["name"]:
                new_object_row = row
        self.assertTrue(new_object_row, "New object not displayed")

        # user looks at details of newly created object:
        new_object_row.find_element_by_xpath("//a[@class='btn btn-primary btn-sm my-1' and contains(text(), "
                                             "'Details')]").click()
        description_detail_element = self.browser.find_element_by_xpath("//span[@class='font-weight-bold'and "
                                                                        "contains(text(), 'Description (en) : ')]"
                                                                        "/following-sibling::span")
        self.assertEqual(description_detail_element.text, self.lookup_data["description_en"].replace("\n", " "),
                         "Description does not match input")

        # user updates the instances details and goes on their way
        self.browser.find_element_by_xpath("//a[@class='btn btn-primary' and@title='Update']").click()
        name_field = self.browser.find_element_by_xpath("//input[@name='name']")
        name_field.clear()
        name_field.send_keys("updated name")
        submit_btn = self.browser.find_element_by_xpath("//button[@class='btn btn-success']")
        scroll_n_click(self.browser, submit_btn)

        details_table = self.browser.find_element_by_xpath("//table[@id='details_table']/tbody")
        rows = details_table.find_elements_by_tag_name("tr")  # get all of the rows in the table
        new_object_row = False
        old_object_row = False
        for row in rows:
            # Get the columns (all the column 2)
            name_cell = row.find_elements_by_tag_name("td")[0]  # note: index start from 0, 1 is col 2
            if name_cell.text == self.lookup_data["name"]:
                old_object_row = row
            if name_cell.text == "updated name":
                new_object_row = row
        self.assertTrue(new_object_row, "updated object not in details list")
        self.assertFalse(old_object_row, "old object still in details list")
