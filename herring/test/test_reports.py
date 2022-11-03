from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import FormView
from faker import Faker

from ..test import FactoryFloor
from ..test.common_tests import CommonHerringTest as CommonTest
from .. import models
from .. import views

faker = Faker()


class TestReportSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:report_search')
        self.expected_template = 'herring/reports.html'
        self.user = self.get_and_login_user(is_read_only=True)


    @tag("herring", 'reports', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReportSearchFormView, FormView)

    @tag("herring", 'reports', "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)


class TestReports(CommonTest):
    def setUp(self):
        super().setUp()
        fish = FactoryFloor.SamplerFactory()
        sample = fish.sample
        year = sample.season

        for x in range(1, 10):
            fish = FactoryFloor.SamplerFactory(sample=sample)

        for l in models.LengthBin.objects.all()[:30]:
            lf = FactoryFloor.LengthFrequencyFactory(sample=sample, length_bin=l)

        activate('en')

        self.test_urls = [
            reverse_lazy('herring:export_progress_report'),
            reverse_lazy('herring:export_sample_report'),
            reverse_lazy('herring:export_lf_report'),
            reverse_lazy('herring:export_fish_detail'),
            reverse_lazy('herring:export_hlen'),
            reverse_lazy('herring:export_hlog'),
            reverse_lazy('herring:export_hdet'),
        ]


    @tag("ihub", 'reports')
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
