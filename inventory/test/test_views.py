from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import TemplateView

from inventory.test import FactoryFloor
from inventory.test.common_tests import CommonInventoryTest as CommonTest
from .. import views


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('inventory:index')
        self.expected_template = 'inventory/index.html'

    @tag("inventory", 'index', "view")
    def test_view_class(self):
        self.assert_inheritance(views.Index, TemplateView)

    @tag("inventory", 'index', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_public_view(test_url=self.test_url, expected_template=self.expected_template)

