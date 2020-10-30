from django.test import tag
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from faker import Faker

from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from shared_models.models import Cruise
from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from shared_models.views import CommonCreateView, CommonDeleteView, CommonDetailView, CommonFilterView, CommonUpdateView, \
    CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView
from .. import views, models

faker = Faker()


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


class TestFileDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FileFactory()
        self.test_url = reverse_lazy('cruises:file_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("File", "file_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FileDeleteView, CommonPopoutDeleteView)

    @tag("File", "file_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("File", "file_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.FileFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.File.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("File", "file_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:file_delete", f"/en/cruises/file/{self.instance.pk}/delete/", [self.instance.pk])


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


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('cruises:index')
        self.expected_template = 'cruises/index.html'
        self.user = self.get_and_login_user()

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, TemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # @tag("Index", "index", "context")
    # def test_context(self):
    #     context_vars = [
    #         "field_list",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:index", f"/en/cruises/")


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


class TestInstrumentComponentDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentComponentFactory()
        self.test_url = reverse_lazy('cruises:component_delete', args=[self.instance.pk, ])
        self.expected_template = 'cruises/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("InstrumentComponent", "component_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentComponentDeleteView, CommonDeleteView)

    @tag("InstrumentComponent", "component_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("InstrumentComponent", "component_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentComponentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.InstrumentComponent.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("InstrumentComponent", "component_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:component_delete", f"/en/cruises/component/{self.instance.pk}/delete/", [self.instance.pk])


class TestInstrumentComponentUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentComponentFactory()
        self.test_url = reverse_lazy('cruises:component_edit', args=[self.instance.pk, ])
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("InstrumentComponent", "component_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentComponentUpdateView, CommonUpdateView)

    @tag("InstrumentComponent", "component_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("InstrumentComponent", "component_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentComponentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("InstrumentComponent", "component_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:component_edit", f"/en/cruises/component/{self.instance.pk}/edit/", [self.instance.pk])


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


class TestInstrumentDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentFactory()
        self.test_url = reverse_lazy('cruises:instrument_delete', args=[self.instance.pk, ])
        self.expected_template = 'cruises/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Instrument", "instrument_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentDeleteView, CommonDeleteView)

    @tag("Instrument", "instrument_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instrument", "instrument_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Instrument.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Instrument", "instrument_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:instrument_delete", f"/en/cruises/instrument/{self.instance.pk}/delete/", [self.instance.pk])


class TestInstrumentDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentFactory()
        self.test_url = reverse_lazy('cruises:instrument_detail', args=[self.instance.pk, ])
        self.expected_template = 'cruises/instrument_detail.html'
        self.user = self.get_and_login_user()

    @tag("Instrument", "instrument_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentDetailView, CommonDetailView)

    @tag("Instrument", "instrument_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instrument", "instrument_detail", "context")
    def test_context(self):
        context_vars = [
            "component_field_list",
            "component_object",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Instrument", "instrument_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:instrument_detail", f"/en/cruises/instrument/{self.instance.pk}/view/", [self.instance.pk])
class TestInstrumentUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InstrumentFactory()
        self.test_url = reverse_lazy('cruises:instrument_edit', args=[self.instance.pk, ])
        self.expected_template = 'cruises/form.html'
        self.user = self.get_and_login_user(in_group="oceanography_admin")

    @tag("Instrument", "instrument_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstrumentUpdateView, CommonUpdateView)

    @tag("Instrument", "instrument_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instrument", "instrument_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.InstrumentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Instrument", "instrument_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:instrument_edit", f"/en/cruises/instrument/{self.instance.pk}/edit/", [self.instance.pk])


