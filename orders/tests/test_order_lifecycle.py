from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order
from orders.services.lifecycle import cancel_order, fulfill_order


class OrderLifecycleServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ops = User.objects.create_user(username="ops_user", password="pass12345")

    @patch("orders.services.lifecycle.log_event")
    def test_cancel_pending_order(self, mock_log):
        order = Order.objects.create(
            email="a@test.com",
            status="pending",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )

        updated = cancel_order(order=order, actor=self.ops, reason="customer request")
        updated.refresh_from_db()

        self.assertEqual(updated.status, "cancelled")
        mock_log.assert_called()
        self.assertEqual(mock_log.call_args.kwargs["event_type"], "order_cancelled")

    @patch("orders.services.lifecycle.log_event")
    def test_cancel_non_pending_raises(self, mock_log):
        order = Order.objects.create(
            email="b@test.com",
            status="paid",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )

        with self.assertRaises(ValidationError):
            cancel_order(order=order, actor=self.ops, reason="should fail")

        self.assertFalse(mock_log.called)

    @patch("orders.services.lifecycle.log_event")
    def test_fulfill_paid_order(self, mock_log):
        order = Order.objects.create(
            email="c@test.com",
            status="paid",
            subtotal=Decimal("20.00"),
            total=Decimal("20.00"),
        )

        updated = fulfill_order(order=order, actor=self.ops, note="packed and shipped")
        updated.refresh_from_db()

        self.assertEqual(updated.status, "fulfilled")
        mock_log.assert_called()
        self.assertEqual(mock_log.call_args.kwargs["event_type"], "order_fulfilled")

    @patch("orders.services.lifecycle.log_event")
    def test_fulfill_not_paid_raises(self, mock_log):
        order = Order.objects.create(
            email="d@test.com",
            status="pending",
            subtotal=Decimal("20.00"),
            total=Decimal("20.00"),
        )

        with self.assertRaises(ValidationError):
            fulfill_order(order=order, actor=self.ops, note="should fail")

        self.assertFalse(mock_log.called)
