from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView, UpdateView

from shared_models.views import CommonDetailView, CommonUpdateView, CommonPopoutUpdateView
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from .. import views
from .. import models

# Example how to run with keyword tags
# python manage.py test whalebrary.test --tag transaction_new


class TestItemUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Item", "item_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemUpdateView, CommonUpdateView)
        self.assert_inheritance(views.ItemUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("Item", "item_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Item", "item_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ItemFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestLocationUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.LocationFactory()
        self.test_url = reverse_lazy('whalebrary:location_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("Location", "location_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.LocationUpdateView, CommonUpdateView)
        self.assert_inheritance(views.LocationUpdateView, views.WhalebraryAdminAccessRequired)

    @tag("Location", "location_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Location", "location_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.LocationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestTransactionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:transaction_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Transaction", "transaction_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TransactionUpdateView, CommonUpdateView)
        self.assert_inheritance(views.TransactionUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("Transaction", "transaction_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Transaction", "transaction_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.TransactionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

#TODO check that kwargs can be static
class TestOrderReceivedTransactionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransactionFactory()
        self.test_url = reverse_lazy('whalebrary:transaction_edit', kwargs={"pk": 1, "user": 1, "pop": 1})
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("OrderReceivedTransaction", "transaction_order_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrderReceivedTransactionUpdateView, CommonPopoutUpdateView)
        self.assert_inheritance(views.OrderReceivedTransactionUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("OrderReceivedTransaction", "transaction_order_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("OrderReceivedTransaction", "transaction_order_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.TransactionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


#TODO something wrong with date_ordered -- ask David
class TestOrderUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrderFactory()
        self.test_url = reverse_lazy('whalebrary:order_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Order", "order_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrderUpdateView, CommonUpdateView)
        self.assert_inheritance(views.OrderUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("Order", "order_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Order", "order_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.OrderFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

#TODO something wrong with date_ordered -- ask David
class TestOrderUpdatePopoutView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrderFactory()
        self.test_url = reverse_lazy('whalebrary:order_edit', kwargs={"pk": 1, "pop": 1})
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("OrderUpdate", "order_edit_pop", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrderUpdatePopoutView, CommonPopoutUpdateView)
        self.assert_inheritance(views.OrderUpdatePopoutView, views.WhalebraryEditRequiredMixin)

    @tag("OrderUpdate", "order_edit_pop", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)

    @tag("OrderUpdate", "order_edit_pop", "submit")
    def test_submit(self):
        data = FactoryFloor.OrderFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestPersonnelUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonnelFactory()
        self.test_url = reverse_lazy('whalebrary:personnel_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_admin")

    @tag("Personnel", "personnel_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonnelUpdateView, CommonUpdateView)
        self.assert_inheritance(views.PersonnelUpdateView, views.WhalebraryAdminAccessRequired)

    @tag("Personnel", "personnel_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Personnel", "personnel_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.PersonnelFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestSupplierUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SupplierFactory()
        self.test_url = reverse_lazy('whalebrary:supplier_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Supplier", "supplier_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SupplierUpdateView, CommonUpdateView)
        self.assert_inheritance(views.SupplierUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("Supplier", "supplier_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Supplier", "supplier_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SupplierFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestSupplierUpdatePopoutView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SupplierFactory()
        self.test_url = reverse_lazy('whalebrary:supplier_edit', kwargs={"pk": 1, "pop": 1})
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("SupplierUpdate", "supplier_edit_pop", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SupplierUpdatePopoutView, CommonPopoutUpdateView)
        self.assert_inheritance(views.SupplierUpdatePopoutView, views.WhalebraryEditRequiredMixin)

    @tag("SupplierUpdate", "supplier_edit_pop", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("SupplierUpdate", "supplier_edit_pop", "submit")
    def test_submit(self):
        data = FactoryFloor.SupplierFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestFileUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FileFactory()
        self.test_url = reverse_lazy('whalebrary:file_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/file_form_popout.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("File", "file_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FileUpdateView, UpdateView)
        self.assert_inheritance(views.FileUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("File", "file_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("File", "file_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FileFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

#TODO - str translation error
class TestIncidentUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentFactory()
        self.test_url = reverse_lazy('whalebrary:incident_edit', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

    @tag("Incident", "incident_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IncidentUpdateView, CommonUpdateView)
        self.assert_inheritance(views.IncidentUpdateView, views.WhalebraryEditRequiredMixin)

    @tag("Incident", "incident_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Incident", "incident_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.IncidentFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)




# class TestTripRequestUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.IndividualTripRequestFactory()
#         self.instance_child = FactoryFloor.IndividualTripRequestFactory()
#         self.test_url = reverse_lazy('travel:request_edit', args=(self.instance.pk, "my"))
#         self.test_url1 = reverse_lazy('travel:request_edit', args=(self.instance_child.pk, "pop"))
#         self.expected_template = 'travel/trip_request_form.html'
#         self.expected_template1 = 'travel/trip_request_form_popout.html'
#
#     @tag("travel", "view")
#     def test_view_class(self):
#         self.assert_inheritance(views.TripRequestUpdateView, CommonUpdateView)
#         self.assert_inheritance(views.TripRequestUpdateView, views.CanModifyMixin)
#
#     @tag("travel", "access")
#     def test_view(self):
#         self.assert_not_broken(self.test_url)
#         self.assert_not_broken(self.test_url1)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.instance.user)
#         self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template1, user=self.instance_child.user)
#
#     @tag("travel", "context")
#     def test_context(self):
#         context_vars = [
#             "cost_field_list",
#             "user_json",
#             "conf_json",
#             "help_text_dict",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.instance.user)
#         self.assert_presence_of_context_vars(self.test_url1, context_vars, user=self.instance_child.user)
#
#     @tag("travel", "submit")
#     def test_submit(self):
#         data = FactoryFloor.IndividualTripRequestFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.instance.user)
#         data = FactoryFloor.ChildTripRequestFactory.get_valid_data()
#         self.assert_success_url(self.test_url1, data=data, user=self.instance_child.user)
