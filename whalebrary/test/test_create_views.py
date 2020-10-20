from django.urls import reverse_lazy
from django.test import tag

from shared_models.views import CommonCreateView
from whalebrary import views
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest

# Example how to run with keyword tags
# python manage.py test whalebrary.test --tag transaction_new


class TestItemCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_new')
        self.expected_template = "whalebrary/form.html"
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Item", "item_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemCreateView, CommonCreateView)
        self.assert_inheritance(views.ItemCreateView, views.WhalebraryEditRequiredMixin)

    @tag("Item", "item_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Item", "item_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ItemFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestTransactionCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:transaction_new')
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Transaction", "transaction_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TransactionCreateView, CommonCreateView)
        self.assert_inheritance(views.TransactionCreateView, views.WhalebraryEditRequiredMixin)

    @tag("Transaction", "transaction_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Transaction", "transaction_new", "submit")
    def test_submit(self):
        data = FactoryFloor.TransactionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
