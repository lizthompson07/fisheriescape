from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView

from shared_models.views import CommonDetailView
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from .. import views


class TestItemDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_detail', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/item_detail.html'
        self.user = self.get_and_login_user()

    @tag("Item", "item_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemDetailView, CommonDetailView)

    @tag("Item", "item_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Item", "item_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
            "random_qty",
            "qty_field_list",
            "oh_qty_field_list",
            "random_sup",
            "sup_field_list",
            "random_ord",
            "ord_field_list",
            "random_lend",
            "lend_field_list",
            "random_file",
            "file_field_list",

        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestTransactionDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:transaction_detail', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/transaction_detail.html'
        self.user = self.get_and_login_user()

    @tag("Transaction", "transaction_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TransactionDetailView, CommonDetailView)

    @tag("Transaction", "transaction_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Transaction", "transaction_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)