from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView
from .. import models
from .. import views

from inventory.test.common_tests import CommonInventoryTest as CommonTest
from inventory.test import FactoryFloor
from ..views import WhalebraryAccessRequired


class TestItemListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('whalebrary:item_list')
        self.expected_template = 'whalebrary/item_list.html'

    @tag("whalebrary", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemListView, FilterView)
        self.assert_inheritance(views.ItemListView, WhalebraryAccessRequired)

    @tag("whalebrary", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    # Test that the context contains the proper vars
    @tag("whalebrary", 'list', "context")
    def test_context(self):
        context_vars = [
            "field_list",
            "my_object",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
