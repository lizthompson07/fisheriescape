from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.models import Port
from .common_tests import CommonHerringTest as CommonTest
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView, \
    CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView
from . import FactoryFloor
from .. import views, models

faker = Factory.create()


class TestSpeciesCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:species_new')
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesCreateView, CommonCreateView)

    @tag("Species", "species_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_new", f"/en/herman/species/new/")


class TestSpeciesDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDeleteView, CommonDeleteView)

    @tag("Species", "species_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Species.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Species", "species_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_delete", f"/en/herman/species/delete/{self.instance.pk}/", [self.instance.pk])


class TestSpeciesDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/detail.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Species", "species_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDetailView, CommonDetailView)

    @tag("Species", "species_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_detail", f"/en/herman/species/view/{self.instance.pk}/", [self.instance.pk])


class TestSpeciesListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:species_list')
        self.expected_template = 'herring/list.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Species", "species_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesListView, CommonFilterView)

    @tag("Species", "species_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Species", "species_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_list", f"/en/herman/species/")


class TestSpeciesUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_edit', args=[self.instance.pk, ])
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesUpdateView, CommonUpdateView)

    @tag("Species", "species_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_edit", f"/en/herman/species/edit/{self.instance.pk}/", [self.instance.pk])




class TestPortCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:port_new')
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortCreateView, CommonCreateView)

    @tag("Port", "port_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_new", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Port", "port_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_new", f"/en/herman/ports/new/")


class TestPortDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortDeleteView, CommonDeleteView)

    @tag("Port", "port_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(Port.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Port", "port_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_delete", f"/en/herman/ports/delete/{self.instance.pk}/", [self.instance.pk])


class TestPortDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/detail.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortDetailView, CommonDetailView)

    @tag("Port", "port_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_detail", f"/en/herman/ports/view/{self.instance.pk}/", [self.instance.pk])


class TestPortListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:port_list')
        self.expected_template = 'herring/list.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortListView, CommonFilterView)

    @tag("Port", "port_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Port", "port_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_list", f"/en/herman/ports/")


class TestPortUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_edit', args=[self.instance.pk, ])
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortUpdateView, CommonUpdateView)

    @tag("Port", "port_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Port", "port_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_edit", f"/en/herman/ports/edit/{self.instance.pk}/", [self.instance.pk])



