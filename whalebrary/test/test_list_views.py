from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView

from shared_models.views import CommonFilterView
from .. import models
from .. import views

from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from whalebrary.test import FactoryFloor
from ..views import WhalebraryAccessRequired


class TestItemListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_list')
        self.expected_template = 'whalebrary/item_list.html'
        self.user = self.get_and_login_user()



    @tag("Item", "item_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemListView, CommonFilterView)
        self.assert_inheritance(views.ItemListView, views.WhalebraryAccessRequired)



    @tag("Item", "item_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)


    @tag("Item", "item_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
