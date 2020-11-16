from django.urls import reverse_lazy
from django.test import tag

import shared_models
from whalebrary import models
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from faker import Faker

faker = Faker()


class TestItemModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.instance = models.Item.objects.all()[faker.random_int(0, models.Item.objects.count() - 1)]

    @tag('Item', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "item_name",
            "description",
            "note",
            "owner",
            "size",
            "category",
            "gear_type",
            "suppliers",
        ]
        self.assert_has_fields(models.Item, fields_to_check)

    @tag('Item', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Item, ["tname",
                                            "lent_out_quantities",
                                            "get_oh_quantity",
                                            "total_oh_quantity",
                                            "oh_quantity_by_location",
                                            "active_orders"
                                            ])

    @tag('Item', 'models', 'm2m')
    def test_m2m_supplier(self):
        # a `my_model` that is attached to a given `supplier` should be accessible by the m2m field name `suppliers`
        supplier = models.Supplier.objects.all()[faker.random_int(0, models.Supplier.objects.count() - 1)]
        supplier = FactoryFloor.SupplierFactory()
        self.instance.suppliers.add(supplier)
        self.assertEqual(self.instance.suppliers.count(), 1)
        self.assertIn(supplier, self.instance.suppliers.all())

    @tag('Item', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('item_name', 'size'),)
        actual_unique_together = models.Item._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('Item', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['owner',
                           'category',
                           'gear_type',
                           ]
        self.assert_mandatory_fields(models.Item, fields_to_check)