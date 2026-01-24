from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order
from orders.services.lifecycle import cancel_order, fulfill_order


class OrderLifecycleRuleTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ops = User.objects.create_user(
            username="ops", password="pass12345", is_staff=True
        )

        self.pending = Order.objects.create(
            email="p@test.com",
            status="pending",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )
        self.paid = Order.objects.create(
            email="x@test.com",
            status="paid",
            subtotal=Decimal("20.00"),
            total=Decimal("20.00"),
        )
        self.canceled = Order.objects.create(
            email="c@test.com",
            status="canceled",
            subtotal=Decimal("5.00"),
            total=Decimal("5.00"),
        )

    def test_cancel_only_pending(self):
        # ok
        cancel_order(order=self.pending, actor=self.ops, reason="customer request")
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "canceled")

        # not allowed
        with self.assertRaises(ValidationError):
            cancel_order(order=self.paid, actor=self.ops)

    def test_fulfill_only_paid(self):
        # ok
        fulfill_order(order=self.paid, actor=self.ops, note="shipped")
        self.paid.refresh_from_db()
        self.assertEqual(self.paid.status, "fulfilled")

        # not allowed
        with self.assertRaises(ValidationError):
            fulfill_order(order=self.canceled, actor=self.ops)

        with self.assertRaises(ValidationError):
            fulfill_order(order=self.pending, actor=self.ops)
