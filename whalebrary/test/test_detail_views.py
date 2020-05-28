from django.utils import timezone
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import DetailView
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from .. import views


class TestItemDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.item = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_detail', kwargs={"pk": self.item.pk})
        self.expected_template = 'whalebrary/item_detail.html'

    @tag("whalebrary", 'detail', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemDetailView, DetailView)
        self.assert_inheritance(views.ItemDetailView, views.VaultAccessRequired)

    @tag("whalebrary", 'detail', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    # Test that the context contains the proper vars
    @tag("whalebrary", 'detail', "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
        fields_to_test = [
            "serial_number",
        ]
        self.assert_field_in_field_list(self.test_url, "field_list", fields_to_test)
        # we want to make sure no just anyone sees this field

# Liz, here is my template testview

# class TestViewName(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('app_name:view_name')
#         self.expected_template = 'app_name/template_file_path.html'
#
#     @tag("app_name", 'type', "view")
#     def test_view_class(self):
#         self.assert_inheritance(views.ViewName, ViewClass)
#
#     @tag("app_name", 'type', "access")
#     def test_view(self):
#         self.assert_not_broken(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
#         self.assert_public_view(test_url=self.test_url, expected_template=self.expected_template)
#
#     # Test that the context contains the proper vars
#     @tag("app_name", 'type', "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars)

