from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView

from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from shared_models.views import CommonDetailView
from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from .. import views


class TestCruiseDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()
        self.test_url = reverse_lazy('cruises:cruise_detail', args=[self.instance.pk, ])
        self.expected_template = 'cruises/cruise_detail.html'
        self.user = self.get_and_login_user()

    @tag("Cruise", "cruise_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CruiseDetailView, CommonDetailView)

    @tag("Cruise", "cruise_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # @tag("Cruise", "cruise_detail", "context")
    # def test_context(self):
    #     context_vars = [
    #         "field_list",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Cruise", "cruise_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:cruise_detail", f"/en/cruises/{self.instance.pk}/view/", [self.instance.pk])
