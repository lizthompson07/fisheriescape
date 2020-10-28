from django.urls import reverse_lazy
from django.test import tag
from shared_models.test.SharedModelsFactoryFloor import RegionFactory, CruiseFactory
from shared_models.views import CommonFilterView, CommonListView
from cruises.test import FactoryFloor
from .. import models
from .. import views
from cruises.test.common_tests import CommonCruisesTest as CommonTest


class TestCruiseListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('cruises:cruise_list')
        self.expected_template = 'cruises/list.html'
        self.user = self.get_and_login_user()

    @tag("Cruise", "cruise_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CruiseListView, CommonFilterView)

    @tag("Cruise", "cruise_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Cruise", "cruise_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:cruise_list", f"/en/cruises/list/")
