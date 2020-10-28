from django.urls import reverse_lazy
from django.test import tag
from django.utils import timezone
from django.utils.translation import activate
from django.views.generic import CreateView, UpdateView, FormView

from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from shared_models.views import CommonUpdateView, CommonPopoutUpdateView
from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from .. import views
from .. import models
from faker import Faker

faker = Faker()


class TestCruiseUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()
        self.test_url = reverse_lazy('cruises:cruise_edit', args=[self.instance.pk, ])
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Cruise", "cruise_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CruiseUpdateView, CommonUpdateView)

    @tag("Cruise", "cruise_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Cruise", "cruise_edit", "submit")
    def test_submit(self):
        data = CruiseFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Cruise", "cruise_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:cruise_edit", f"/en/cruises/{self.instance.pk}/edit/", [self.instance.pk])


class TestFileUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FileFactory()
        self.test_url = reverse_lazy('cruises:file_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("File", "file_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FileUpdateView, CommonPopoutUpdateView)

    @tag("File", "file_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("File", "file_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FileFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("File", "file_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:file_edit", f"/en/cruises/file/{self.instance.pk}/edit/", [self.instance.pk])
