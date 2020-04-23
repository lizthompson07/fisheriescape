from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from inventory.test import FactoryFloor
from inventory.test.common_tests import CommonInventoryTest as CommonTest
from .. import views
#
# class TestIndexTemplateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('inventory:index')
#         self.expected_template = 'inventory/index.html'
#
#     @tag("inventory", 'index', "view")
#     def test_view_class(self):
#         self.assert_inheritance(views.IndexTemplateView, TemplateView)
#
#     @tag("inventory", 'index', "access")
#     def test_view(self):
#         self.assert_not_broken(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
#         self.assert_public_view(test_url=self.test_url, expected_template=self.expected_template)
#
#     # Test that the context contains the proper vars
#     @tag("inventory", 'index', "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars)
#
#     @tag("inventory", 'index', "submit")
#     def test_submit(self):
#         data = FactoryFloor.IndexFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data)
#
#         # for delete views...
#         self.assertEqual(models.Index.objects.filter(pk=self.instance.pk).count(), 0)