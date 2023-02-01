from django.test import tag
from django.urls import reverse_lazy
from django.views.generic import FormView
from faker import Faker

from ..test.common_tests import CommonInventoryTest as CommonTest
from .. import views

faker = Faker()


class TestReportSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('inventory:report_search')
        self.expected_template = 'inventory/report_search.html'

    @tag("inventory", 'report', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReportSearchFormView, FormView)

    @tag("inventory", 'report', "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        my_user = self.get_and_login_user(is_regional_admin=True)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=my_user)


class TestODIReport(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_urls = [
            reverse_lazy('inventory:export_odi_report'),
        ]
        self.view = views.export_odi_report

    @tag("inventory", 'report')
    def test_view(self):
        self.assert_non_public_view(test_url=self.test_urls[0])
        for url in self.test_urls:
            self.assert_good_response(url)


class TestPhysicalSamplesReport(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_urls = [
            reverse_lazy('inventory:export_phyiscal_samples'),
        ]
        self.view = views.export_odi_report

    @tag("inventory", 'report')
    def test_view(self):
        self.assert_non_public_view(test_url=self.test_urls[0])
        for url in self.test_urls:
            self.assert_good_response(url)
