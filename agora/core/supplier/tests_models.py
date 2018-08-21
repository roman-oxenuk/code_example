# -*- coding: utf-8 -*-
from django.test import TestCase

from agora.core.supplier.models import Supplier, PriceType


class SupplierTestCase(TestCase):

    def test_create_default_price_type_on_suppliers_creation(self):
        # создаём Поставщика
        supplier = Supplier.objects.create()
        self.assertTrue(supplier.price_types.filter(default=True).exists())
        self.assertEqual(supplier.price_types.all().count(), 1)

        # редактируем Поставщика
        supplier.order_process = False
        supplier.save()
        self.assertTrue(supplier.price_types.filter(default=True).exists())
        self.assertEqual(supplier.price_types.all().count(), 1)

    def test_default_price_type(self):
        supplier = Supplier.objects.create()
        pt0 = supplier.default_price_type
        pt1 = PriceType.objects.create(supplier=supplier)
        pt2 = PriceType.objects.create(supplier=supplier)
        pt3 = PriceType.objects.create(supplier=supplier)

        self.assertTrue(pt0.default is True)
        self.assertTrue(pt1.default is False)
        self.assertTrue(pt2.default is False)
        self.assertTrue(pt3.default is False)

        # меняем Тип цены по умолчанию
        supplier.default_price_type = pt1
        self.assertTrue(PriceType.objects.get(id=pt0.id).default is False)
        self.assertTrue(PriceType.objects.get(id=pt1.id).default is True)
        self.assertTrue(PriceType.objects.get(id=pt2.id).default is False)
        self.assertTrue(PriceType.objects.get(id=pt3.id).default is False)
