from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView

from shared_models.views import CommonDetailView, CommonUpdateView
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

    @tag("Item", "item_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Item", "item_edit", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Item", "item_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ItemFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Item.objects.filter(pk=self.instance.pk).count(), 0)


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
