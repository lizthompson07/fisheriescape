from selenium import webdriver

from django.test import tag
from bio_diversity import forms
from bio_diversity.test import BioFactoryFloor
# from ..test.common_tests import CommonProjectTest as CommonTest
from shared_models.test.common_tests import CommonTest


class CommonFunctionalTest(CommonTest):
    def setUp(self):
        super().setUp()  # used to import fixtures
        self.browser = webdriver.Chrome('bio_diversity/test/functional_test/chromedriver.exe')

    def tearDown(self):
        super().tearDown()  # used to import fixtures
        self.browser.close()


@tag("Functional", "Basic")
class TestHomePageTitle(CommonFunctionalTest):

    def test_home_page_title(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get('http://localhost:8000')

        # She notices the page title tells her she is at DM Apps
        assert 'DM Apps' in self.browser.title



