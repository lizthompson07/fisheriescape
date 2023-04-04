from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView, UpdateView

from shared_models.views import CommonDetailView, CommonUpdateView, CommonPopoutUpdateView
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest
from .. import views
from .. import models


# Example how to run with keyword tags
# python manage.py test fisheriescape.test --tag species_edit


# TODO submit is failing because of polygon field I think
class TestFisheryUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FisheryFactory()
        self.test_url = reverse_lazy('fisheriescape:fishery_edit', args=[self.instance.pk, ])
        self.expected_template = 'fisheriescape/form.html'
        self.user = self.get_and_login_user(in_group="fisheriescape_admin")

    @tag("Fishery", "fishery_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FisheryUpdateView, CommonUpdateView)
        self.assert_inheritance(views.FisheryUpdateView, views.FisheriescapeAdminAccessRequired)

    @tag("Fishery", "fishery_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Fishery", "fishery_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FisheryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Fishery", "fishery_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("fisheriescape:fishery_edit", f"/en/fisheriescape/fishery/{self.instance.pk}/edit/", [self.instance.pk])
