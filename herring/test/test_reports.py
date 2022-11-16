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
        fish = FactoryFloor.FishDetailFactory(fish_number=100)
        sample = fish.sample

        for x in range(1, 10):
            fish = FactoryFloor.FishDetailFactory(sample=sample, fish_number=x)

        for l in models.LengthBin.objects.all()[:30]:
            lf = FactoryFloor.LengthFrequencyFactory(sample=sample, length_bin=l)

        activate('en')

        self.test_urls = [
            reverse_lazy('herring:progress_report_detail') + f"?year={sample.season}&species={sample.species.id}",
            reverse_lazy('herring:export_progress_report') + f"?year={sample.season}&species={sample.species.id}",
            reverse_lazy('herring:export_sample_report') + f"?year={sample.season}&species={sample.species.id}",
            reverse_lazy('herring:export_lf_report') + f"?year={sample.season}&species={sample.species.id}",
            reverse_lazy('herring:export_fish_detail') + f"?year={sample.season}&species={sample.species.id}",
            reverse_lazy('herring:export_hlen') + f"?year={sample.season}",
            reverse_lazy('herring:export_hlog') + f"?year={sample.season}",
            reverse_lazy('herring:export_hdet') + f"?year={sample.season}",
        ]


    @tag("ihub", 'reports')
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
