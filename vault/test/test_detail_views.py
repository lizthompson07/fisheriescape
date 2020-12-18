from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView

from shared_models.views import CommonDetailView
from vault.test import FactoryFloor
from vault.test.common_tests import CommonVaultTest as CommonTest
from .. import views

# Example how to run with keyword tags
# python manage.py test vault.test --tag species_detail


class TestSpeciesDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('vault:species_detail', args=[self.instance.pk, ])
        self.expected_template = 'vault/species_detail.html'
        self.user = self.get_and_login_user(in_group="vault_admin")

    @tag("Species", "species_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDetailView, CommonDetailView)
        self.assert_inheritance(views.SpeciesDetailView, views.VaultAdminAccessRequired)

    @tag("Species", "species_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestOutingDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OutingFactory()
        self.test_url = reverse_lazy('vault:outing_detail', args=[self.instance.pk, ])
        self.expected_template = 'vault/outing_detail.html'
        self.user = self.get_and_login_user(in_group="vault_admin")

    @tag("Outing", "outing_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OutingDetailView, CommonDetailView)
        self.assert_inheritance(views.OutingDetailView, views.VaultAdminAccessRequired)

    @tag("Outing", "outing_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Outing", "outing_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
