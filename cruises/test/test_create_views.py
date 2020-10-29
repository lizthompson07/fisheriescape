from django.urls import reverse_lazy
from django.test import tag

from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from shared_models.views import CommonCreateView, CommonPopoutCreateView
from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from .. import views
from .. import models


class TestCruiseCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('cruises:cruise_new')
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Cruise", "cruise_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CruiseCreateView, CommonCreateView)

    @tag("Cruise", "cruise_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Cruise", "cruise_new", "submit")
    def test_submit(self):
        data = CruiseFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Cruise", "cruise_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:cruise_new", f"/en/cruises/new/")


class TestFileCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()
        self.test_url = reverse_lazy('cruises:file_new', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("File", "file_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FileCreateView, CommonPopoutCreateView)

    @tag("File", "file_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("File", "file_new", "submit")
    def test_submit(self):
        data = FactoryFloor.FileFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user, file_field_name="file")

    @tag("File", "file_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:file_new", f"/en/cruises/{self.instance.pk}/file/new/", [self.instance.pk])


class TestInstrumentCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()
        self.test_url = reverse_lazy('cruises:instrument_new', args=[self.instance.pk, ])
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Instrument", "file_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentCreateView, CommonCreateView)

    @tag("Instrument", "file_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instrument", "file_new", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user, file_field_name="file")

    @tag("Instrument", "file_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:instrument_new", f"/en/cruises/{self.instance.pk}/instrument/new/", [self.instance.pk])


class TestInstrumentComponentCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentFactory()
        self.test_url = reverse_lazy('cruises:component_new', args=[self.instance.pk, ])
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("InstrumentComponent", "component_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentComponentCreateView, CommonCreateView)

    @tag("InstrumentComponent", "component_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("InstrumentComponent", "component_new", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentComponentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("InstrumentComponent", "component_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:component_new", f"/en/cruises/instrument/{self.instance.pk}/new-component/", [self.instance.pk])
