from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import CreateView, UpdateView

from inventory.test import FactoryFloor
from inventory.test.common_tests import CommonInventoryTest as CommonTest
from .. import views


class TestResourceUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ResourceFactory()
        self.test_url = reverse_lazy('inventory:resource_edit', kwargs={"pk": self.instance.pk})
        self.resource_person = FactoryFloor.CustodianResourcePersonFactory(resource=self.instance)
        self.expected_template = 'inventory/resource_form.html'

    @tag("inventory", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ResourceUpdateView, UpdateView)

    @tag("inventory", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # the user must be a custodian...
        user = FactoryFloor.CustodianResourcePersonFactory(resource=self.instance)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.resource_person.person.user)

    # Test that the context contains the proper vars
    @tag("inventory", 'update', "context")
    def test_context(self):
        context_vars = [
            "resource_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.resource_person.person.user)

    @tag("inventory", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.ResourceFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.resource_person.person.user)
