from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView

from shared_models.test.SharedModelsFactoryFloor import GroupFactory
from shared_models.views import CommonFilterView, CommonListView
from .. import models
from .. import views

from vault.test.common_tests import CommonVaultTest as CommonTest
from vault.test import FactoryFloor


# Example how to run with keyword tags
# python manage.py test vault.test --tag species_list


class TestUserListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.UserFactory()
        self.test_url = reverse_lazy('vault:user_list')
        self.test_url1 = reverse_lazy('vault:user_list', args=[1])
        self.expected_template = 'vault/user_list.html'
        self.user = self.get_and_login_user(in_group="vault_admin")
        GroupFactory(name="vault_admin")
        GroupFactory(name="vault_edit")

    @tag("User", "user_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.UserListView, CommonFilterView)
        self.assert_inheritance(views.UserListView, views.VaultAdminAccessRequired)

    @tag("User", "user_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)

    @tag("User", "user_list", "context")
    def test_context(self):
        context_vars = [
            "vault_admin",
            "vault_edit",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("User", "user_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("vault:user_list", f"/en/vault/settings/users/")


class TestSpeciesListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('vault:species_list')
        self.expected_template = 'vault/list.html'
        self.user = self.get_and_login_user()

    @tag("Species", "species_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesListView, CommonFilterView)
        self.assert_inheritance(views.SpeciesListView, views.VaultAccessRequired)

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
        self.assert_correct_url("vault:species_list", f"/en/vault/species-list/")


class TestOutingListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OutingFactory()
        self.test_url = reverse_lazy('vault:outing_list')
        self.expected_template = 'vault/list.html'
        self.user = self.get_and_login_user()

    @tag("Outing", "outing_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OutingListView, CommonFilterView)
        self.assert_inheritance(views.OutingListView, views.VaultAccessRequired)

    @tag("Outing", "outing_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Outing", "outing_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Outing", "outing_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("vault:outing_list", f"/en/vault/outing-list/")
