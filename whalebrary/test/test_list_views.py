from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import ListView
from django_filters.views import FilterView

from shared_models.views import CommonFilterView, CommonListView
from .. import models
from .. import views

from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from whalebrary.test import FactoryFloor
from ..views import WhalebraryAccessRequired


# Example how to run with keyword tags
# python manage.py test whalebrary.test --tag transaction_new


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


class TestItemTransactionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:item_transaction_detail', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("ItemTransaction", "item_transaction_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemTransactionListView, CommonFilterView)
        self.assert_inheritance(views.ItemTransactionListView, views.WhalebraryAdminAccessRequired)

    @tag("ItemTransaction", "item_transaction_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ItemTransaction", "item_transaction_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestLocationListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.LocationFactory()
        self.test_url = reverse_lazy('whalebrary:location_list')
        self.expected_template = 'whalebrary/list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("Location", "location_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.LocationListView, CommonFilterView)
        self.assert_inheritance(views.LocationListView, views.WhalebraryAdminAccessRequired)

    @tag("Location", "location_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Location", "location_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestTransactionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:transaction_list')
        self.expected_template = 'whalebrary/list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("Transaction", "transaction_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TransactionListView, CommonFilterView)
        self.assert_inheritance(views.TransactionListView, views.WhalebraryAdminAccessRequired)

    @tag("Transaction", "transaction_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Transaction", "transaction_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestBulkTransactionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:bulk_transaction_list')
        self.expected_template = 'whalebrary/bulk_transaction_list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("BulkTransaction", "bulk_transaction_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BulkTransactionListView, CommonFilterView)
        self.assert_inheritance(views.BulkTransactionListView, views.WhalebraryAdminAccessRequired)

    @tag("BulkTransaction", "bulk_transaction_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BulkTransaction", "bulk_transaction_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestOrderListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrderFactory()
        self.test_url = reverse_lazy('whalebrary:order_list')
        self.expected_template = 'whalebrary/order_list.html'
        self.user = self.get_and_login_user()

    @tag("Order", "order_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrderListView, CommonFilterView)
        self.assert_inheritance(views.OrderListView, views.WhalebraryAccessRequired)

    @tag("Order", "order_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Order", "order_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestPersonnelListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonnelFactory()
        self.test_url = reverse_lazy('whalebrary:personnel_list')
        self.expected_template = 'whalebrary/personnel_list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("Personnel", "personnel_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonnelListView, CommonFilterView)
        self.assert_inheritance(views.PersonnelListView, views.WhalebraryAdminAccessRequired)

    @tag("Personnel", "personnel_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Personnel", "personnel_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestSupplierListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SupplierFactory()
        self.test_url = reverse_lazy('whalebrary:supplier_list')
        self.expected_template = 'whalebrary/list.html'
        self.user = self.get_and_login_user()

    @tag("Supplier", "supplier_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SupplierListView, CommonFilterView)
        self.assert_inheritance(views.SupplierListView, views.WhalebraryAccessRequired)

    @tag("Supplier", "supplier_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Supplier", "supplier_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestFileListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FileFactory()
        self.test_url = reverse_lazy('whalebrary:file_list')
        self.expected_template = 'whalebrary/file_list.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("File", "file_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FileListView, CommonFilterView)
        self.assert_inheritance(views.FileListView, views.WhalebraryAdminAccessRequired)

    @tag("File", "file_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("File", "file_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestIncidentListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentFactory()
        self.test_url = reverse_lazy('whalebrary:incident_list')
        self.expected_template = 'whalebrary/incident_list.html'
        self.user = self.get_and_login_user()

    @tag("Incident", "incident_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IncidentListView, CommonFilterView)
        self.assert_inheritance(views.IncidentListView, views.WhalebraryAccessRequired)

    @tag("Incident", "incident_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Incident", "incident_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
