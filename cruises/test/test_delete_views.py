from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DeleteView

from shared_models.test.SharedModelsFactoryFloor import RegionFactory, CruiseFactory
from shared_models.views import CommonDeleteView
from shared_models.models import Cruise
from cruises.test import FactoryFloor
from .. import models
from .. import views
from cruises.test.common_tests import CommonCruisesTest as CommonTest

class TestCruiseDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()
        self.test_url = reverse_lazy('cruises:cruise_delete', args=[self.instance.pk, ])
        self.expected_template = 'cruises/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Cruise", "cruise_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CruiseDeleteView, CommonDeleteView)

    @tag("Cruise", "cruise_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Cruise", "cruise_delete", "submit")
    def test_submit(self):
        data = CruiseFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(Cruise.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Cruise", "cruise_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:cruise_delete", f"/en/cruises/{self.instance.pk}/delete/", [self.instance.pk])