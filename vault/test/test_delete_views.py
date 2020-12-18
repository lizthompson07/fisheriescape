from django.urls import reverse_lazy
from django.test import tag

from shared_models.views import CommonDeleteView, CommonPopoutDeleteView
from .. import models
from .. import views
from vault import views
from vault.test import FactoryFloor
from vault.test.common_tests import CommonVaultTest as CommonTest


# Example how to run with keyword tags
# python manage.py test vault.test --tag species_delete


class TestSpeciesDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('vault:species_delete', args=[self.instance.pk, ])
        self.expected_template = 'vault/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="vault_admin")

    @tag("Species", "species_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDeleteView, CommonDeleteView)
        self.assert_inheritance(views.SpeciesDeleteView, views.VaultAdminAccessRequired)

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


class TestOutingDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OutingFactory()
        self.test_url = reverse_lazy('vault:outing_delete', args=[self.instance.pk, ])
        self.expected_template = 'vault/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="vault_admin")

    @tag("Outing", "outing_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OutingDeleteView, CommonDeleteView)
        self.assert_inheritance(views.OutingDeleteView, views.VaultAdminAccessRequired)

    @tag("Outing", "outing_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Outing", "outing_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.OutingFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Outing.objects.filter(pk=self.instance.pk).count(), 0)
