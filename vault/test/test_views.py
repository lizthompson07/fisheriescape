from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from vault.test.common_tests import CommonVaultTest as CommonTest
from .. import views


class TestIndexView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('vault:index')
        self.expected_template = 'vault/index.html'

    @tag("vault", 'index', "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url)

